#!/usr/bin/env python3
"""Layer-2 routing eval harness. Scores a routing selection against expected sets.

NEVER calls an API. The model call sits behind a provider function:

    provider(request: str, case_id: str) -> dict
        keys: primary (str), modules (list[str]), boundary_ids (list[str]), mode (str)

Two implementations ship:

  fixture  (default)  reads eval/fixtures/<case-id>.json. Self-testable offline.
                      A fixture may hold either one response dict, or a list of
                      response dicts -- with -n repeats, repeat i takes element
                      i % len(list), which is how probabilistic selection is
                      replayed deterministically.

  command  --provider command --command "<argv...>"
                      CONTRACT: the command is run once per case per repeat with
                      no arguments added; the case request is written to its
                      stdin and stdin is closed; the command must write exactly
                      one JSON object to stdout with the four keys above; the
                      exit status is ignored, stderr is ignored. Anything on
                      stdout that is not one JSON object is a HARNESS ERROR for
                      that case. No default command is shipped, no model name is
                      embedded, no credential is read.

Cases file: JSONL, one object per line.
    id                 str, required
    request            str, required
    expect_primary     str
    expect_modules     list[str]    may be empty (a negative case)
    expect_boundary_ids list[str]   may be empty
    expect_mode        str
    forbid_modules     list[str]
    negative           bool
All of the above are required on every line; a missing key is a harness error.

Metrics are reported separately and never averaged into a single score.
No pass mark is set here.
"""

import argparse
import hashlib
import io
import json
import os
import tempfile
import subprocess
import sys

# SKILL.md step 2: "Load at most two TASK modules initially"; steps 4-5 say the discovery
# budget cannot suppress a material boundary module. So the budget a case is held to is the
# larger of that constant and the module count the case itself asserts as correct -- a case
# whose expected load is 3 because two of them are non-suppressible boundary modules is not
# bloat. Only loads beyond the asserted-correct set count as over-loading.
MODULE_BUDGET = 2
RESPONSE_KEYS = ("primary", "modules", "boundary_ids", "mode")
CASE_KEYS = (
    "expect_primary",
    "expect_modules",
    "expect_boundary_ids",
    "expect_mode",
    "forbid_modules",
    "negative",
)

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REFERENCES = os.path.join(REPO, "skills", "ai-engineer", "references")
HASHED_FILES = (
    "skills/ai-engineer/SKILL.md",
    "skills/ai-engineer/references/procedure-index.md",
)


class HarnessError(Exception):
    """Anything that makes a case unscoreable. Never a routing failure."""


# ---------------------------------------------------------------- providers


def make_fixture_provider(fixtures_dir):
    def provider(request, case_id, repeat):
        path = os.path.join(fixtures_dir, case_id + ".json")
        try:
            with open(path, encoding="utf-8") as fh:
                data = json.load(fh)
        except FileNotFoundError:
            raise HarnessError("missing fixture: %s" % path)
        except json.JSONDecodeError as exc:
            raise HarnessError("fixture is not valid JSON: %s: %s" % (path, exc))
        if isinstance(data, list):
            if not data:
                raise HarnessError("fixture list is empty: %s" % path)
            data = data[repeat % len(data)]
        return validate_response(data, "fixture %s" % path)

    return provider


def parse_command(spec):
    """argv for the runner. A JSON array is taken literally; a plain string is split.

    Splitting on whitespace is wrong the moment any path contains a space, which every
    Windows Python installation does: "C:/Program Files/Python313/python.exe runner.py"
    became ["C:/Program", "Files/Python313/python.exe", "runner.py"]. It appeared to work
    because Windows resolves an executable across a space leniently, so the process
    started -- with the rest of its own path handed to it as the script argument. Pass a
    JSON array to say exactly what you mean.
    """
    spec = spec.strip()
    if spec.startswith("["):
        try:
            argv = json.loads(spec)
        except ValueError as exc:
            raise HarnessError("--command looks like JSON but does not parse: %s" % exc)
        if not isinstance(argv, list) or not argv or not all(isinstance(a, str) for a in argv):
            raise HarnessError("--command JSON must be a non-empty array of strings")
        return argv
    return spec.split()


def make_command_provider(argv):
    def provider(request, case_id, repeat):
        try:
            done = subprocess.run(
                argv, input=request, capture_output=True, text=True, encoding="utf-8"
            )
        except OSError as exc:
            raise HarnessError("provider command failed to start: %s" % exc)
        out = done.stdout
        try:
            data = json.loads(out)
        except json.JSONDecodeError as exc:
            # stderr is not scored, but it is the only place a runner can say WHY it gave
            # up. Without quoting it, five identical "stdout is not valid JSON" lines are
            # all a report shows for a case that timed out, and the reason has to be
            # rediscovered by hand.
            why = (done.stderr or "").strip().splitlines()
            tail = " | ".join(why[-3:])[:400] if why else "(runner said nothing on stderr)"
            raise HarnessError(
                "provider stdout is not valid JSON for case %s: %s; runner stderr: %s"
                % (case_id, exc, tail)
            )
        return validate_response(data, "provider output for case %s" % case_id)

    return provider


def known_modules():
    """Module filenames that exist. Fails closed: an empty directory is a harness error, not
    an empty allow-set that makes every module name acceptable."""
    try:
        names = {f for f in os.listdir(REFERENCES) if f.endswith(".md")}
    except OSError as exc:
        raise HarnessError("cannot list module directory: %s" % exc)
    if not names:
        raise HarnessError("0 module files found in %s" % REFERENCES)
    return names


def validate_response(data, where):
    if not isinstance(data, dict):
        raise HarnessError("%s is not a JSON object" % where)
    missing = [k for k in RESPONSE_KEYS if k not in data]
    if missing:
        raise HarnessError("%s is missing keys: %s" % (where, ", ".join(missing)))
    for k in ("modules", "boundary_ids"):
        if not isinstance(data[k], list):
            raise HarnessError("%s: %s must be a list" % (where, k))
    # Module names are compared as raw strings by every module metric, so a name that is not
    # a real file silently escapes forbid_modules and module_recall ("context-prompt-engineering"
    # is not "context-prompt-engineering.md"). Unscoreable, not a wrong answer.
    unknown = sorted(set(data["modules"]) - known_modules())
    if unknown:
        raise HarnessError(
            "%s names module(s) that do not exist in skills/ai-engineer/references: %s"
            % (where, ", ".join(unknown))
        )
    return data


# ------------------------------------------------------------------ scoring

# Each checker returns True/False, or None when the metric does not apply to
# the case (excluded from that metric's denominator).


def label(value):
    """Procedure IDs and mode names are compared as labels, not as literals.

    A real run answers "Design" where the case says "design", and "ARC-01." with the
    sentence punctuation attached. Comparing raw strings scores that as a routing
    failure, which measures the reply's typography instead of its routing. Module
    names are NOT passed through here: those are filenames, and a filename that does
    not match exactly is a different file.
    """
    return str(value).strip().strip(".,;:").casefold()


def score_once(case, resp):
    expect_b = {label(b) for b in (case.get("expect_boundary_ids") or [])}
    got_b = {label(b) for b in resp["boundary_ids"]}
    modules = set(resp["modules"])
    expect_m = set(case.get("expect_modules") or [])
    forbid = set(case.get("forbid_modules") or [])
    negative = bool(case.get("negative"))
    return {
        # A negative case asserts that no module should open, not that no procedure ID may be
        # named. Naming the ID a concept question is about, while loading nothing, is the
        # behaviour the case wants; charging it primary_accuracy against an empty expectation
        # measured tact, not routing. negative_violation is what scores these cases.
        "primary_accuracy": (
            None
            if negative or not case.get("expect_primary")
            else label(resp["primary"]) == label(case.get("expect_primary"))
        ),
        # all-or-nothing: a partially fired boundary is an unfired boundary
        "boundary_recall": expect_b <= got_b if expect_b else None,
        "false_boundary_rate": bool(got_b - expect_b),
        # Without this, naming the right IDs while opening no procedure text scores a perfect
        # card: SELECT is the behaviour this layer exists to test.
        "module_recall": (expect_m <= modules) if expect_m else None,
        "over_loading_rate": len(modules) > max(MODULE_BUDGET, len(expect_m)),
        "forbidden_load_rate": bool(forbid & modules),
        "negative_violation": (len(modules) > 0) if negative else None,
        "mode_accuracy": label(resp["mode"]) == label(case.get("expect_mode")),
    }


METRICS = (
    "primary_accuracy",
    "boundary_recall",
    "false_boundary_rate",
    "module_recall",
    "over_loading_rate",
    "forbidden_load_rate",
    "negative_violation",
    "mode_accuracy",
)
# Metrics where True means "good"; the rest are rates where True means "bad".
GOOD_IS_TRUE = {"primary_accuracy", "boundary_recall", "module_recall", "mode_accuracy"}


def load_result_log(path):
    """{(case_id, repeat): score_or_error} already recorded. Missing file -> empty.

    A truncated final line is dropped rather than raising: the usual reason a line is
    half-written is that the process was killed mid-append, and losing one call is the
    correct cost of that. A corrupt line anywhere else is still a hard error, because
    silently skipping recorded results would let a resumed run report fewer repeats than
    it claims.
    """
    done = {}
    if not path or not os.path.exists(path):
        return done
    with open(path, encoding="utf-8") as fh:
        lines = fh.read().splitlines()
    for i, line in enumerate(lines):
        line = line.strip()
        if not line:
            continue
        try:
            rec = json.loads(line)
        except ValueError:
            if i == len(lines) - 1:
                continue  # killed mid-append
            raise HarnessError("result log line %d is not valid JSON: %s" % (i + 1, path))
        done[(rec["id"], rec["repeat"])] = rec
    return done


def run(cases, provider, n, jobs=1, result_log=None, resume=False):
    """-> (per_case, errors). per_case[i] = {id, fractions: {metric: frac|None}}.

    `jobs` runs (case, repeat) pairs concurrently. Every provider call is independent by
    contract -- one process per call, request on stdin -- so concurrency changes only how
    long the run takes. It must not change what the run says, which is why results are
    collected into a keyed table and assembled in case order afterwards rather than
    appended as they land; the selftest asserts jobs=1 and jobs=4 agree.

    Concurrency is bounded by whatever the provider talks to, not by this harness. Too
    many jobs against a rate-limited endpoint turns into throttling that reads as model
    slowness, so this stays an explicit operator choice with a default of 1.
    """
    recorded = load_result_log(result_log) if resume else {}
    # A harness error is not a measurement, so resuming re-runs it. Skipping it would let
    # a raised timeout or a fixed runner bug never get retried, and the report would keep
    # excluding the same cases from every denominator while looking complete.
    previous = {k: v for k, v in recorded.items() if v.get("error") is None}
    tasks = [
        (ci, case, r)
        for ci, case in enumerate(cases)
        for r in range(n)
        if (case["id"], r) not in previous
    ]
    if previous:
        print(
            "resuming: %d of %d calls already in %s"
            % (len(previous), len(cases) * n, result_log),
            file=sys.stderr,
        )
    scored = {}
    failed = {}
    # One lock for the append. Each write is a single line, so a reader always sees whole
    # records; without the lock two threads interleave partial lines and the log becomes
    # unparseable exactly when it matters, after a kill.
    import threading

    lock = threading.Lock()
    sink = open(result_log, "a", encoding="utf-8", newline="\n") if result_log else None

    def record(case_id, repeat, score, error):
        if sink is None:
            return
        rec = {"id": case_id, "repeat": repeat, "score": score, "error": error}
        with lock:
            sink.write(json.dumps(rec) + "\n")
            sink.flush()  # a buffered result is a lost result
            os.fsync(sink.fileno())

    def one(task):
        ci, case, r = task
        try:
            score = score_once(case, provider(case["request"], case["id"], r))
        except HarnessError as exc:
            record(case["id"], r, None, str(exc))
            return ci, r, None, str(exc)
        record(case["id"], r, score, None)
        return ci, r, score, None

    try:
        if jobs > 1:
            from concurrent.futures import ThreadPoolExecutor

            with ThreadPoolExecutor(max_workers=jobs) as pool:
                outcomes = list(pool.map(one, tasks))
        else:
            outcomes = [one(t) for t in tasks]
    finally:
        if sink is not None:
            sink.close()

    by_id = {case["id"]: ci for ci, case in enumerate(cases)}
    for (case_id, repeat), rec in previous.items():
        ci = by_id.get(case_id)
        if ci is None:
            continue  # the log holds a case no longer in the corpus; not this run's business
        if rec.get("error") is None:
            scored[(ci, repeat)] = rec["score"]
        else:
            failed[(ci, repeat)] = rec["error"]

    for ci, r, score, error in outcomes:
        if error is None:
            scored[(ci, r)] = score
        else:
            failed[(ci, r)] = error

    per_case, errors = [], []
    for ci, case in enumerate(cases):
        for r in range(n):
            if (ci, r) in failed:
                errors.append({"id": case["id"], "repeat": r, "error": failed[(ci, r)]})
        runs = [scored[(ci, r)] for r in range(n) if (ci, r) in scored]
        if not runs:
            continue  # every repeat errored; already recorded as a harness error
        fractions = {}
        for m in METRICS:
            vals = [x[m] for x in runs if x[m] is not None]
            fractions[m] = (sum(vals) / len(vals)) if vals else None
        per_case.append({"id": case["id"], "n_scored": len(runs), "fractions": fractions})
    return per_case, errors


def aggregate(per_case):
    """Metric -> {value, cases} over cases where the metric applies."""
    out = {}
    for m in METRICS:
        vals = [c["fractions"][m] for c in per_case if c["fractions"][m] is not None]
        out[m] = {
            "value": (sum(vals) / len(vals)) if vals else None,
            "cases": len(vals),
        }
    return out


def unstable(per_case):
    """Cases with any pass fraction strictly between 0 and 1."""
    out = []
    for c in per_case:
        shaky = {m: f for m, f in c["fractions"].items() if f is not None and 0 < f < 1}
        if shaky:
            out.append({"id": c["id"], "metrics": shaky})
    return out


# --------------------------------------------------------------- provenance


def sha256_file(rel):
    path = os.path.join(REPO, rel)
    try:
        with open(path, "rb") as fh:
            return hashlib.sha256(fh.read()).hexdigest()
    except FileNotFoundError:
        raise HarnessError("cannot hash missing file: %s" % rel)


def provenance(args):
    return {
        "provider": args.provider,
        "command": args.command if args.provider == "command" else None,
        "model": args.model,
        "effort": args.effort,
        "n": args.n,
        "jobs": args.jobs,
        "resumed_from": args.result_log if args.resume else None,
        "date": args.date,  # caller-supplied; the harness never reads a clock
        "sha256": {rel: sha256_file(rel) for rel in HASHED_FILES},
    }


# ------------------------------------------------------------------- report

NO_BAR = (
    "NO PASS MARK IS SET HERE. This harness reports measurements and exits 0 on any\n"
    "completed run. The maintainer sets the bar. Note for whoever does: on\n"
    "adverse-action and regulated cases, boundary_recall below 1.0 is a defect, not a\n"
    "percentage."
)


def report(prov, per_case, agg, errors, out=sys.stdout):
    p = lambda s="": print(s, file=out)
    p("== PROVENANCE ==")
    p("provider: %s" % prov["provider"])
    if prov["command"]:
        p("command:  %s" % prov["command"])
    p("model:    %s   (recorded as passed in, not chosen by the harness)" % prov["model"])
    p("effort:   %s   (recorded as passed in)" % prov["effort"])
    p("n:        %d" % prov["n"])
    p("date:     %s   (--date argument, not a clock read)" % prov["date"])
    for rel, digest in prov["sha256"].items():
        p("sha256    %s  %s" % (digest, rel))
    p()
    p("== METRICS (reported separately, never averaged) ==")
    for m in METRICS:
        v = agg[m]["value"]
        p("%-20s %s   (%d cases)" % (m, "n/a" if v is None else "%.4f" % v, agg[m]["cases"]))
    p()
    uns = unstable(per_case)
    p("== UNSTABLE (%d cases) ==" % len(uns))
    p("An unstable case is more dangerous than a failing one: it passes the demo and")
    p("fails in production.")
    for u in uns:
        p("  %s  %s" % (u["id"], ", ".join("%s=%.2f" % (m, f) for m, f in sorted(u["metrics"].items()))))
    p()
    p("== HARNESS ERRORS (%d) ==" % len(errors))
    p("Not scored as routing failures. A parse failure counted as a wrong answer")
    p("silently inflates the failure rate and hides the real defect.")
    for e in errors:
        p("  %s repeat %d: %s" % (e["id"], e["repeat"], e["error"]))
    p()
    p(NO_BAR)


# --------------------------------------------------------------------- main


def load_cases(path):
    try:
        with open(path, encoding="utf-8") as fh:
            lines = [ln for ln in (l.strip() for l in fh) if ln]
    except OSError as exc:
        raise HarnessError("cannot read cases file: %s" % exc)
    cases = []
    for i, ln in enumerate(lines, 1):
        try:
            c = json.loads(ln)
        except json.JSONDecodeError as exc:
            raise HarnessError("cases file line %d is not valid JSON: %s" % (i, exc))
        # Fail closed on the expectation keys too: a mistyped key would read as an absent
        # expectation and make the case permanently unpassable with no error printed.
        for k in ("id", "request") + CASE_KEYS:
            if k not in c:
                raise HarnessError("cases file line %d has no %r" % (i, k))
        cases.append(c)
    return cases


def check_cases(path, out=sys.stdout):
    """Case-corpus invariants + ID coverage. Returns (errors, printed counts).

    This lived in a throwaway script while the shards were written, and that is exactly how a
    case whose primary was repeated inside its own expect_boundary_ids reached the merged file:
    one shard's private validator asserted the convention, the others did not. It lives here
    now so every run can assert it.
    """
    p = lambda s="": print(s, file=out)
    errors = []
    index_path = os.path.join(REFERENCES, "procedure-index.md")
    try:
        with open(index_path, encoding="utf-8") as fh:
            index_text = fh.read()
    except OSError as exc:
        raise HarnessError("cannot read the procedure index: %s" % exc)
    ids = set()
    for line in index_text.splitlines():
        if line.startswith("|"):
            cell = line.strip().strip("|").split("|")[0].strip().strip("`")
            if len(cell) == 6 and cell[:3].isalpha() and cell[3] == "-" and cell[4:].isdigit():
                ids.add(cell.upper())
    if not ids:
        raise HarnessError("0 procedure IDs parsed from %s" % index_path)
    modules = known_modules()

    cases = load_cases(path)  # schema and key presence are asserted there
    seen = {}
    for c in cases:
        cid = c["id"]
        seen[cid] = seen.get(cid, 0) + 1
        if seen[cid] > 1:
            errors.append("%s: duplicate case id" % cid)
        for name in list(c["expect_modules"]) + list(c["forbid_modules"]):
            if name not in modules:
                errors.append("%s: module %r is not a file in references/" % (cid, name))
        if set(c["expect_modules"]) & set(c["forbid_modules"]):
            errors.append("%s: a module is both expected and forbidden" % cid)
        for bid in c["expect_boundary_ids"]:
            if bid not in ids:
                errors.append("%s: boundary id %s has no index row" % (cid, bid))
            if bid == c["expect_primary"]:
                errors.append(
                    "%s: %s is the expected primary and is repeated in its own "
                    "expect_boundary_ids; the boundary set excludes the primary, and scoring "
                    "one case both ways makes boundary_recall unsatisfiable corpus-wide"
                    % (cid, bid)
                )
        if c["negative"]:
            if c["expect_primary"] or c["expect_modules"] or c["expect_boundary_ids"]:
                errors.append("%s: negative case asserts a primary, a module or a boundary" % cid)
        elif not c["forbid_modules"]:
            errors.append("%s: no forbid_modules, so over-eager loading is unmeasured here" % cid)
        low = c["request"].lower()
        for token in sorted(ids):
            if token.lower() in low:
                errors.append("%s: request text names procedure ID %s -- string-matchable" % (cid, token))
        for name in sorted(modules):
            if name.lower() in low or name[:-3].lower() in low:
                errors.append("%s: request text names module %s -- string-matchable" % (cid, name))

    # The merged file is what gets scored and the shards are what get edited, so a shard edit
    # that never reaches the merge is invisible.
    shard_dir = os.path.join(os.path.dirname(os.path.abspath(path)), "cases")
    if os.path.isdir(shard_dir):
        shards = sorted(f for f in os.listdir(shard_dir) if f.endswith(".jsonl"))
        merged_lines = [ln for ln in open(path, encoding="utf-8").read().splitlines() if ln.strip()]
        shard_lines = []
        for f in shards:
            with open(os.path.join(shard_dir, f), encoding="utf-8") as fh:
                shard_lines += [ln for ln in fh.read().splitlines() if ln.strip()]
        if shard_lines != merged_lines:
            errors.append(
                "%s is not the concatenation of cases/%s; re-merge the shards"
                % (os.path.basename(path), ", ".join(shards))
            )

    covered = {c["expect_primary"] for c in cases if not c["negative"]}
    p("cases: %d   unique ids: %d   negatives: %d"
      % (len(cases), len(seen), sum(1 for c in cases if c["negative"])))
    p("index IDs: %d   covered as expect_primary: %d" % (len(ids), len(covered & ids)))
    p("UNCOVERED IDs: %s" % (sorted(ids - covered) or "none"))
    p("primary values with no index row: %s" % (sorted(covered - ids) or "none"))
    p("cases asserting a compound boundary: %d" % sum(1 for c in cases if c["expect_boundary_ids"]))
    p("ERRORS: %d" % len(errors))
    for e in errors:
        p("  " + e)
    return errors


def build_parser():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--cases", default="eval/cases.jsonl")
    ap.add_argument("--fixtures", default="eval/fixtures")
    ap.add_argument("--provider", choices=("fixture", "command"), default="fixture")
    ap.add_argument("--command", help="argv of the external provider; request on stdin, JSON on stdout")
    ap.add_argument("-n", type=int, default=1, help="repeats per case")
    ap.add_argument(
        "--jobs",
        type=int,
        default=1,
        help="run this many (case, repeat) pairs concurrently; results are identical to "
        "--jobs 1, only faster. Bound it by what your provider tolerates.",
    )
    ap.add_argument(
        "--result-log",
        help="append one JSON line per completed call. A 435-call run that dies at call 220 "
        "otherwise reports nothing at all: every score lives in memory until the end.",
    )
    ap.add_argument(
        "--resume",
        action="store_true",
        help="skip calls already present in --result-log instead of re-paying for them",
    )
    ap.add_argument("--date", help="run date, ISO (required; the harness never reads a clock)")
    ap.add_argument("--model", default="unspecified", help="recorded verbatim")
    ap.add_argument("--effort", default="unspecified", help="recorded verbatim")
    ap.add_argument("--json-out", help="write the full report as JSON here")
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument(
        "--check-cases",
        action="store_true",
        help="validate the case corpus and print ID coverage; no provider is called",
    )
    return ap


def main(argv=None):
    args = build_parser().parse_args(argv)
    if args.selftest:
        return selftest()
    if args.check_cases:
        try:
            return 1 if check_cases(args.cases) else 0
        except HarnessError as exc:
            print("HARNESS ERROR: %s" % exc, file=sys.stderr)
            return 2
    if not args.date:
        build_parser().error("--date is required (ISO form); a self-stamping report is unreproducible")
    try:
        if args.provider == "command":
            if not args.command:
                build_parser().error("--provider command requires --command")
            provider = make_command_provider(parse_command(args.command))
        else:
            provider = make_fixture_provider(args.fixtures)
        prov = provenance(args)
        cases = load_cases(args.cases)
        per_case, errors = run(
            cases, provider, args.n, args.jobs, args.result_log, args.resume
        )
    except HarnessError as exc:
        print("HARNESS ERROR: %s" % exc, file=sys.stderr)
        return 2
    agg = aggregate(per_case)
    report(prov, per_case, agg, errors)
    if args.json_out:
        blob = {
            "provenance": prov,
            "metrics": agg,
            "per_case": per_case,
            "unstable": unstable(per_case),
            "harness_errors": errors,
            "no_pass_mark": NO_BAR,
        }
        with open(args.json_out, "w", encoding="utf-8", newline="") as fh:
            json.dump(blob, fh, indent=2)
    return 2 if errors else 0  # non-zero ONLY on harness error, never on numbers


# ----------------------------------------------------------------- selftest


def selftest():
    fix = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fixtures")
    provider = make_fixture_provider(fix)
    case = lambda cid, **kw: dict(
        {"id": cid, "request": "r", "expect_primary": "p", "expect_mode": "build"}, **kw
    )
    real = "data-rag-search.md"
    real2 = "security-governance.md"

    def frac(cid, metric, n=1, **kw):
        pc, errs = run([case(cid, **kw)], provider, n)
        assert not errs, errs
        return pc[0]["fractions"][metric]

    print("selftest: layer-2 routing eval harness")

    # 1. missing one expected boundary ID -> 0, not partial credit
    f = frac("st-boundary-partial", "boundary_recall", expect_boundary_ids=["b1", "b2"])
    assert f == 0.0, f
    print("  ok  1/12  one of two expected boundaries fired -> boundary_recall 0.0 (no partial credit)")

    # 2. unexpected boundary raises false_boundary_rate, recall stays 1.0
    kw = {"expect_boundary_ids": ["b1"]}
    r = frac("st-boundary-extra", "boundary_recall", **kw)
    fb = frac("st-boundary-extra", "false_boundary_rate", **kw)
    assert (r, fb) == (1.0, 1.0), (r, fb)
    print("  ok  2/12  unexpected boundary -> false_boundary_rate 1.0, boundary_recall still 1.0")

    # 3. negative case that loads a module is caught
    v = frac("st-negative-loads", "negative_violation", negative=True)
    assert v == 1.0, v
    clean = frac("st-clean", "negative_violation", negative=True)
    assert clean == 0.0, clean
    print("  ok  3/12  negative case loading one module -> negative_violation 1.0 (clean case 0.0)")

    # 4. three of five repeats -> 0.6 and lands in UNSTABLE
    c = case("st-flaky")
    pc, errs = run([c], provider, 5)
    assert not errs, errs
    got = pc[0]["fractions"]["primary_accuracy"]
    assert abs(got - 0.6) < 1e-9, got
    uns = unstable(pc)
    assert len(uns) == 1 and uns[0]["id"] == "st-flaky", uns
    assert abs(uns[0]["metrics"]["primary_accuracy"] - 0.6) < 1e-9
    print("  ok  4/12  3 of 5 repeats pass -> pass fraction 0.6, case listed in UNSTABLE")

    # 5. malformed provider output is a harness error, not a scoring failure
    pc, errs = run([case("st-malformed"), case("st-missing-fixture")], provider, 1)
    assert pc == [], pc
    assert len(errs) == 2, errs
    assert "not valid JSON" in errs[0]["error"], errs[0]
    assert "missing fixture" in errs[1]["error"], errs[1]
    agg = aggregate(pc)
    assert all(agg[m]["value"] is None for m in METRICS), agg
    print("  ok  5/12  malformed stdout + missing fixture -> 2 harness errors, 0 scored cases")

    # 6. loading nothing while naming the right IDs must not score a perfect card
    mr = frac("st-no-modules", "module_recall", expect_modules=[real])
    ok = frac("st-overload", "module_recall", expect_modules=[real])
    assert (mr, ok) == (0.0, 1.0), (mr, ok)
    print("  ok  6/12  correct ids but no module loaded -> module_recall 0.0")

    # 7. a module name that is not a real file is unscoreable, not a clean answer
    pc, errs = run([case("st-unknown-module", forbid_modules=["context-prompt-engineering.md"])], provider, 1)
    assert pc == [] and len(errs) == 1, (pc, errs)
    assert "do not exist" in errs[0]["error"], errs[0]
    print("  ok  7/12  module name that is not a real file -> harness error, not forbidden_load_rate 0.0")

    # 8. a case missing an expectation key is a harness error, not a silently unpassable case
    with tempfile.TemporaryDirectory() as td:
        bad = os.path.join(td, "c.jsonl")
        with open(bad, "w", encoding="utf-8", newline="") as fh:
            fh.write(json.dumps({"id": "x", "request": "r", "expect_primary": "p"}) + "\n")
        try:
            load_cases(bad)
            raise AssertionError("missing expectation key was accepted")
        except HarnessError as exc:
            assert "expect_modules" in str(exc), exc
    print("  ok  8/12  case line missing an expectation key -> harness error")

    # 9. IDs and modes are labels: a real reply capitalises the mode and punctuates the ID
    typo = score_once(
        {"expect_primary": "ARC-01", "expect_mode": "design", "expect_boundary_ids": ["SRC-01"],
         "expect_modules": [], "forbid_modules": [], "negative": False},
        {"primary": "arc-01.", "mode": "Design", "boundary_ids": ["src-01"], "modules": []},
    )
    assert typo["primary_accuracy"] and typo["mode_accuracy"], typo
    assert typo["boundary_recall"] and not typo["false_boundary_rate"], typo
    # but a module filename is a filename: no normalisation, no near-miss credit
    near = score_once(
        {"expect_primary": "ARC-01", "expect_mode": "design", "expect_boundary_ids": [],
         "expect_modules": ["architecture-decision-engine.md"], "forbid_modules": [],
         "negative": False},
        {"primary": "ARC-01", "mode": "design", "boundary_ids": [],
         "modules": ["Architecture-Decision-Engine.md"]},
    )
    assert near["module_recall"] is False, near
    print("  ok  9/12  ID/mode compared as labels; module filenames still compared exactly")

    # 10. a negative case is scored on what it loads, not on whether it named an ID
    neg = score_once(
        {"expect_primary": "", "expect_mode": "explain", "expect_boundary_ids": [],
         "expect_modules": [], "forbid_modules": [], "negative": True},
        {"primary": "ALG-01", "mode": "explain", "boundary_ids": [], "modules": []},
    )
    assert neg["primary_accuracy"] is None, neg
    assert neg["negative_violation"] is False and neg["mode_accuracy"], neg
    print("  ok 10/12  negative case: primary_accuracy not applicable, negative_violation scores it")

    # 11. --jobs must change only the wall clock. A concurrent run that appends results as
    # they land reorders per_case and reassigns repeats between cases; both produce a report
    # that looks fine and attributes scores to the wrong case.
    many = [case("st-flaky"), case("st-clean"), case("st-boundary-partial",
            expect_boundary_ids=["ARC-02", "HRN-02"])]
    seq_pc, seq_err = run(many, provider, 3, 1)
    par_pc, par_err = run(many, provider, 3, 4)
    assert seq_pc == par_pc, (seq_pc, par_pc)
    assert seq_err == par_err, (seq_err, par_err)
    assert [c["id"] for c in par_pc] == [c["id"] for c in many], par_pc
    print("  ok 11/12  --jobs 4 returns byte-identical per-case results and order as --jobs 1")

    # 12. a killed run must cost only the calls in flight, and a resume must not re-pay for
    # what is already recorded, nor silently report fewer repeats than it claims
    with tempfile.TemporaryDirectory() as td:
        logp = os.path.join(td, "results.jsonl")
        three = [case("st-clean"), case("st-flaky")]
        run(three, provider, 2, 1, logp, False)
        recorded = load_result_log(logp)
        assert len(recorded) == 4, recorded

        calls = {"n": 0}

        def counting(request, case_id, repeat):
            calls["n"] += 1
            return provider(request, case_id, repeat)

        resumed_pc, resumed_err = run(three, provider=counting, n=2, jobs=1,
                                      result_log=logp, resume=True)
        assert calls["n"] == 0, "resume re-paid for %d recorded calls" % calls["n"]
        fresh_pc, _ = run(three, provider, 2, 1)
        assert resumed_pc == fresh_pc, (resumed_pc, fresh_pc)

        # a line truncated by the kill is dropped; that call is simply re-run
        with open(logp, "a", encoding="utf-8", newline="\n") as fh:
            fh.write('{"id": "st-clean", "repe')
        assert len(load_result_log(logp)) == 4, "truncated tail was not dropped"
        # but a corrupt line in the middle must not be skipped in silence
        with open(logp, "a", encoding="utf-8", newline="\n") as fh:
            fh.write("\n" + json.dumps({"id": "st-clean", "repeat": 9, "score": None, "error": "x"}) + "\n")
        try:
            load_result_log(logp)
            raise AssertionError("corrupt mid-file line was accepted")
        except HarnessError:
            pass
    print("  ok 12/12  --result-log survives a kill; --resume re-pays nothing and agrees with a full run")

    # --check-cases must reject the two defects that reached the shipped corpus once already
    with tempfile.TemporaryDirectory() as td:
        good = case("c1", expect_primary="ARC-01", expect_modules=[real], forbid_modules=[real2],
                    expect_boundary_ids=["ARC-02"], expect_mode="design", negative=False,
                    request="a plain request")
        bad_self = dict(good, id="c2", expect_boundary_ids=["ARC-01"])
        bad_leak = dict(good, id="c3", request="apply ARC-01 to it")
        def written(rows):
            path = os.path.join(td, "%d.jsonl" % len(os.listdir(td)))
            with open(path, "w", encoding="utf-8", newline="") as fh:
                for row in rows:
                    fh.write(json.dumps(row) + "\n")
            return path
        sink = io.StringIO()
        assert check_cases(written([good]), out=sink) == [], sink.getvalue()
        self_errs = check_cases(written([bad_self]), out=io.StringIO())
        leak_errs = check_cases(written([bad_leak]), out=io.StringIO())
        assert len(self_errs) == 1 and "repeated in its own" in self_errs[0], self_errs
        assert len(leak_errs) == 1 and "string-matchable" in leak_errs[0], leak_errs
    print("  ok  --   --check-cases rejects a primary repeated in its own boundary set, and an ID leaked into a request")

    # over-loading and forbidden loads, plus the budget constant
    ol = frac("st-overload", "over_loading_rate")
    ol_ok = frac("st-overload", "over_loading_rate", expect_modules=["a", "b", "c"])
    fl = frac("st-overload", "forbidden_load_rate", forbid_modules=[real])
    assert (ol, ol_ok, fl) == (1.0, 0.0, 1.0), (ol, ol_ok, fl)
    assert MODULE_BUDGET == 2
    print("  ok  --   3 modules -> over_loading_rate 1.0; 3 expected -> 0.0; forbidden module -> 1.0")

    # provenance hashes are real file digests and no clock is read
    prov = provenance(build_parser().parse_args(["--date", "2026-08-21", "--model", "m", "--effort", "e"]))
    assert prov["date"] == "2026-08-21" and prov["model"] == "m" and prov["effort"] == "e"
    assert set(prov["sha256"]) == set(HASHED_FILES)
    assert all(len(h) == 64 for h in prov["sha256"].values()), prov["sha256"]
    print("  ok  --   provenance records provider/model/effort/n/--date plus 2 sha256 digests")

    print("selftest: all assertions passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
