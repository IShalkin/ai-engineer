#!/usr/bin/env python3
"""Turn a routing-eval result log into per-case failure explanations.

`run_routing_eval.py` reports rates. A rate tells you a metric moved; it never tells
you what the agent did instead, and a metric you cannot explain gets argued about
rather than fixed. This joins three things that already exist:

    --result-log     one line per (case, repeat) with the eight metric outcomes
    --cases          what each case asserts
    --transcripts    the raw stream-json the provider kept, named by request digest

and prints, per failing case, the expected sets beside the observed ones.

Two limits worth knowing before quoting anything from here:

* The provider names transcripts by request digest, so repeats of one case overwrite
  each other. The transcript shown is therefore ONE sample of that case, not the
  repeat that failed. When a case is unstable, the transcript may well be a passing
  run -- the metric fractions are authoritative, the transcript is a lead.
* Observed `boundary_ids`, `primary` and `mode` are what the model reported about
  itself. Only `modules` is observed from tool calls. A wrong self-report and a wrong
  decision are indistinguishable here.

    python eval/explain_failures.py --result-log run.jsonl \
        --cases eval/cases.jsonl --transcripts /path/to/transcripts [--metric module_recall]
"""

import argparse
import collections
import hashlib
import json
import os
import sys

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
# True is the good outcome for these; the rest are rates where True means "bad".
GOOD_IS_TRUE = {"primary_accuracy", "boundary_recall", "module_recall", "mode_accuracy"}
# Must match agent_provider.modules_from_tool_use: only Read loads a module body.
READ_TOOLS = ("Read",)


def load_jsonl(path):
    rows = []
    with open(path, encoding="utf-8") as fh:
        for i, line in enumerate(fh):
            line = line.strip()
            if not line:
                continue
            try:
                rows.append(json.loads(line))
            except ValueError:
                # A run killed mid-append leaves one partial line. Anywhere else this is a
                # real problem, and staying silent about it would understate the corpus.
                sys.stderr.write("%s: dropping unparseable line %d\n" % (path, i + 1))
    return rows


def transcript_for(request, directory):
    if not directory:
        return None
    digest = hashlib.sha1(request.encode("utf-8")).hexdigest()[:12]
    path = os.path.join(directory, digest + ".jsonl")
    return path if os.path.exists(path) else None


def read_transcript(path):
    """-> (observed_modules, reported_json, turn_count)."""
    modules, reported, turns = [], None, 0
    for line in open(path, encoding="utf-8", errors="replace"):
        line = line.strip()
        if not line.startswith("{"):
            continue
        try:
            event = json.loads(line)
        except ValueError:
            continue
        if event.get("type") == "assistant":
            turns += 1
            for block in event.get("message", {}).get("content", []):
                if block.get("type") == "tool_use" and block.get("name") in READ_TOOLS:
                    inp = block.get("input") or {}
                    raw = str(inp.get("file_path") or "")
                    raw = raw.replace(chr(92), "/")
                    if "references" in raw and raw.endswith(".md"):
                        base = os.path.basename(raw)
                        if base not in modules:
                            modules.append(base)
        elif event.get("type") == "result":
            text = str(event.get("result") or "")
            reported = last_json_object(text)
    return modules, reported, turns


def last_json_object(text):
    for start in range(len(text) - 1, -1, -1):
        if text[start] != "{":
            continue
        depth = 0
        for end in range(start, len(text)):
            if text[end] == "{":
                depth += 1
            elif text[end] == "}":
                depth -= 1
                if depth == 0:
                    try:
                        obj = json.loads(text[start : end + 1])
                    except ValueError:
                        break
                    if isinstance(obj, dict) and "primary" in obj:
                        return obj
                    break
    return None


def fractions(rows):
    """{metric: (bad_count, applicable_count)} for one case's repeats."""
    out = {}
    for metric in METRICS:
        vals = [r["score"][metric] for r in rows if r.get("score") and r["score"][metric] is not None]
        if not vals:
            out[metric] = None
            continue
        if metric in GOOD_IS_TRUE:
            bad = sum(1 for v in vals if not v)
        else:
            bad = sum(1 for v in vals if v)
        out[metric] = (bad, len(vals))
    return out


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--result-log", required=True)
    ap.add_argument("--cases", default="eval/cases.jsonl")
    ap.add_argument("--transcripts")
    ap.add_argument("--metric", help="explain only this metric")
    ap.add_argument("--json-out")
    args = ap.parse_args(argv)

    cases = {c["id"]: c for c in load_jsonl(args.cases)}
    by_case = collections.defaultdict(list)
    harness_errors = []
    for row in load_jsonl(args.result_log):
        if row.get("error"):
            harness_errors.append(row)
        else:
            by_case[row["id"]].append(row)

    wanted = (args.metric,) if args.metric else METRICS
    report = []
    for case_id in sorted(by_case):
        case = cases.get(case_id)
        if case is None:
            sys.stderr.write("result log holds unknown case %s; skipped\n" % case_id)
            continue
        fr = fractions(by_case[case_id])
        failing = {m: fr[m] for m in wanted if fr.get(m) and fr[m][0]}
        if not failing:
            continue
        entry = {
            "id": case_id,
            "repeats": len(by_case[case_id]),
            "failing": {m: "%d/%d" % v for m, v in failing.items()},
            "expected": {
                "primary": case["expect_primary"],
                "mode": case["expect_mode"],
                "modules": case["expect_modules"],
                "boundary_ids": case["expect_boundary_ids"],
                "forbid": case["forbid_modules"],
            },
            "request": case["request"],
            "note": case.get("note"),
        }
        path = transcript_for(case["request"], args.transcripts)
        if path:
            modules, reported, turns = read_transcript(path)
            entry["observed_one_sample"] = {
                "modules": modules,
                "reported": reported,
                "assistant_turns": turns,
                "transcript": os.path.basename(path),
            }
        report.append(entry)

    if args.json_out:
        with open(args.json_out, "w", encoding="utf-8") as fh:
            json.dump({"failing_cases": report, "harness_errors": harness_errors}, fh, indent=2)

    print("cases with at least one failing repeat: %d" % len(report))
    print("harness errors in log: %d" % len(harness_errors))
    print()
    for e in report:
        print("== %s  (%d repeats)" % (e["id"], e["repeats"]))
        print("   failing: %s" % ", ".join("%s %s" % (k, v) for k, v in sorted(e["failing"].items())))
        exp = e["expected"]
        print("   expect : primary=%s mode=%s modules=%s boundary=%s"
              % (exp["primary"] or "(none)", exp["mode"], exp["modules"], exp["boundary_ids"]))
        obs = e.get("observed_one_sample")
        if obs:
            rep = obs["reported"] or {}
            print("   sample : primary=%s mode=%s boundary=%s"
                  % (rep.get("primary"), rep.get("mode"), rep.get("boundary_ids")))
            print("            modules opened: %s (%d assistant turns)"
                  % (obs["modules"] or "(none)", obs["assistant_turns"]))
        else:
            print("   sample : no transcript kept for this request")
        print("   request: %s" % e["request"][:150])
        if e.get("note"):
            print("   note   : %s" % str(e["note"])[:200])
        print()

    # Never a gate. This explains a run; the maintainer decides what it means.
    return 0


if __name__ == "__main__":
    sys.exit(main())
