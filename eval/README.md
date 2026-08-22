# Evaluation

Three layers. Each measures one thing and is honest about what it does not measure.
No layer sets a pass mark. Every bar in this repo is unset on purpose — see
"Thresholds" below.

## Layer 1 — static package checks (deterministic, no model)

`skills/ai-engineer/scripts/validate_public_skill.py` and
`skills/ai-engineer/scripts/validate_current_corrections.py`.

Measures: the skill package's internal consistency as text — every procedure ID is
addressed somewhere in `SKILL.md`, every canonical module is reachable from a router
row or a Context Loading Protocol step, every runtime module in `references/` is routed to,
every ID named in the router is named by at least one row that also loads the module defining
it, each `Required output` cell states a count or enumerates at least two named deliverables,
each procedure heading has a body of at least three statements, and the corrections file is
wired into the runtime files.

Does not measure: whether a model actually routes correctly, whether the procedure text
is any good, or whether the produced artifact is correct. A package can pass layer 1 and
route badly on every request.

```
python skills/ai-engineer/scripts/validate_public_skill.py
python skills/ai-engineer/scripts/validate_current_corrections.py
```

**Layer 1 was green on 2026-08-22.** Both scripts exit 0. The three findings the tightened checks surfaced on
first run — `FIN-02` and `ART-01` `Required output` cells that stated nothing countable, and a
`SEC-01` body under the statement bar — were fixed in the skill text, not exempted in the check.

## Layer 2 — routing eval (deterministic scoring, model in the loop)

`eval/run_routing_eval.py` against `eval/cases.jsonl` (merged from `eval/cases/part-*.jsonl`).

Measures, per case, by set comparison: did the run pick the right primary procedure, fire
exactly the expected compound boundaries, stay inside the initial module budget, avoid the
modules the case forbids, **actually load the expected modules**, load nothing at all on a
negative case, and pick the right mode. Eight metrics, reported separately, never averaged.

`module_recall` exists because the other metrics are all about names: without it, a run that
emits the right primary, mode and boundary IDs while opening no procedure text at all scores a
perfect card, and SELECT is the behaviour this layer exists to test. `over_loading_rate` counts
against `max(2, len(expect_modules))`: `SKILL.md` caps *task* modules at two initially and
states in the same breath that the discovery budget cannot suppress a material boundary module,
so a case whose expected load is three because two of them are non-suppressible boundaries is
not bloat. A module name in a response that is not a real file in `references/` is a **harness
error**, not a clean answer — raw-string set comparison would let `context-prompt-engineering`
walk past a `forbid_modules` entry of `context-prompt-engineering.md`.

Does not measure: the quality of the answer. A run can route perfectly and produce a
useless design. Nor does it measure whether the *expected* sets are right — those are
authored judgements, and where `SKILL.md` leaves a tie unresolved the case files say so in
their `note` field rather than inventing a winner.

```
python eval/run_routing_eval.py --selftest
python eval/run_routing_eval.py --check-cases
python eval/run_routing_eval.py --cases eval/cases.jsonl --date <YYYY-MM-DD> \
    --model <model-id-you-ran> --effort <effort-you-set> -n <repeats> \
    --json-out <report.json>
```

The default `fixture` provider reads `eval/fixtures/<case-id>.json`. Only the self-test
fixtures ship, so a full run reports every other case as a **harness error** with zero
scored cases and all metrics `n/a`. That is the designed behaviour: a missing or
unparseable provider response is not a routing failure, and scoring it as one would
inflate the failure rate and hide the real defect. Exit status is non-zero only for
harness errors — never because a metric came out low.

`--check-cases` calls no provider. It asserts the corpus invariants and prints ID coverage:
every schema key present, ids unique, every module name a real file, no module both expected and
forbidden, every boundary ID indexed, **no expected primary repeated inside its own
expect_boundary_ids** (the boundary set excludes the primary; a corpus that does it both ways
makes `boundary_recall` unsatisfiable), negatives empty, non-negatives carrying a forbid list, no
procedure ID or module filename appearing in a request (a case a substring match can pass tests
nothing), and `cases.jsonl` still equal to the concatenation of the shards it is merged from.

### Provider contract (wiring a real model)

```
python eval/run_routing_eval.py --cases eval/cases.jsonl --provider command \
    --command "<argv of your runner>" --date <YYYY-MM-DD> \
    --model <model-id> --effort <effort>
```

The command is run once per case per repeat with no arguments appended. The case request
is written to its stdin, stdin is closed. It must write exactly one JSON object to stdout:

```json
{"primary": "ARC-02", "modules": ["architecture-decision-engine.md"],
 "boundary_ids": ["HRN-02"], "mode": "design"}
```

Anything else on stdout is a harness error for that case. Exit status is ignored; stderr is
not scored either, but its last lines are quoted into the harness error, because it is the
only channel a runner has for saying why it gave up. Without that, five repeats of a case
that timed out read as five identical "stdout is not valid JSON" lines and the cause has to
be rediscovered by hand. The harness ships no default command, embeds no model name, and
reads no credential. Model identity and effort are **recorded verbatim from `--model`/`--effort`,
never chosen by the harness** — the harness cannot know what your runner called, so a
number without those flags is a number you cannot attribute. `--date` is required for the
same reason: no clock is read, so a report cannot self-stamp.

### The shipped runner: `eval/providers/agent_provider.py`

One runner honouring that contract ships. It starts a real Claude Code session with read-only
tools, then reads `modules` **off the transcript's `Read` calls** rather than asking the model
what it would have read. Only `Read` counts: `Glob` returns filenames and no content, and
`Grep` returns matching lines against a directory, so neither establishes that a procedure
body entered the context. An agent that greps for a control instead of opening the module
therefore scores `module_recall` 0, which is the intended reading — a matched line is not the
procedure. That distinction is the whole point of the runner:
a single chat completion can only collect a declaration, which would turn `module_recall`
into an eighth name-matching metric instead of evidence that procedure text entered the
context. `primary`, `boundary_ids` and `mode` stay self-reported — no tool call reveals them.

The package under test is loaded as a session-scoped plugin built from this repository, and
user settings are switched off (`--setting-sources ""`), so the operator's installed hooks,
memory files, and any same-named installed copy of the skill are outside the measurement.
Nothing in the operator's own configuration is read or written.

Everything machine-specific comes from the environment, so no account, model, or credential
is committed here:

| Variable | Meaning |
|---|---|
| `EVAL_MODEL` | required; no default, the runner refuses to guess |
| `EVAL_EFFORT` | default `medium` |
| `EVAL_CLAUDE_SETTINGS` | optional settings JSON holding whatever provider/credential env the CLI needs on this machine; keep it outside this repository |
| `EVAL_TIMEOUT` | per-case seconds, default 600 |
| `EVAL_KEEP_TRANSCRIPT` | directory for the raw `stream-json` of each run |

Two things this runner does **not** measure. It invokes the skill explicitly, so
*auto-activation* from the `description` alone is untested — a separate question needing its
own cases. And it appends one instruction asking for the final JSON, so the reply format is
prompted; the routing decisions inside it are not.

A transcript is named by a digest of the request, so it joins back to `cases.jsonl`; a
transcript named after a process cannot be tied to a case, which is the one job it has. On a
timeout the partial stream is kept as `<digest>.timeout.jsonl`, because "what was it doing for
twenty minutes" is answerable only from that file. Repeats of one case share a digest and
therefore overwrite each other: a kept transcript is one sample, never the repeat that failed.

### Surviving a long run

87 cases at n=5 is 435 sessions and several hours, and anything that takes hours gets
interrupted. Three pieces exist only because of that:

```
python eval/run_until_done.py --result-log run.jsonl --json-out report.json \
    --date 2026-08-22 -n 5 --jobs 6
```

`--result-log` appends one fsync'd line per completed call, so an interruption costs the calls
in flight instead of the whole run. `--resume` skips what the log holds, and deliberately
**retries calls recorded as errors** — a harness error is not a measurement, and skipping it
would mean a raised timeout or a fixed runner bug never gets retried while the report keeps
excluding the same cases from every denominator and looking complete. `run_until_done.py`
re-invokes until the log is full, ignoring the child's exit status because a killed child
reports failure having recorded real work; the log is the only authority. `progress.py` is the
shared counter.

The loop refuses to start without `EVAL_MODEL`, and stops as soon as an attempt records no new
results. Both guards come from one incident: an earlier shell version of the loop ran with
`EVAL_MODEL` unset — on that machine `sh` does not inherit exported variables — and produced
4127 failed calls across eight attempts, burying 137 real results. A retry loop is only
justified while retrying achieves something; an attempt that records nothing means the failure
is configuration rather than interruption.

### Explaining a failure

```
python eval/explain_failures.py --result-log run.jsonl --transcripts <dir> [--metric module_recall]
```

Prints, per failing case, the asserted sets beside what the agent actually opened and reported.
Rates say a metric moved; they never say what happened instead, and an unexplained metric gets
argued about rather than fixed. It states its own limits: the transcript is one sample, and
`primary`/`mode`/`boundary_ids` are self-reported, so a wrong self-report and a wrong decision
are indistinguishable there.

### First live run (8 of 87 cases, n=1)

Recorded so the numbers below are attributable and so nobody reads them as a release
verdict. `us.anthropic.claude-sonnet-5`, effort `medium`, `-n 1`, `--date 2026-08-21`,
8-case subset: `primary_accuracy` 0.75, `boundary_recall` 0.00 (1 case), `false_boundary_rate`
0.25, `module_recall` 0.57 (7 cases), `over_loading_rate` 0.00, `forbidden_load_rate` 0.00,
`negative_violation` 0.00, `mode_accuracy` 0.75. Zero harness errors, zero unstable cases —
and with n=1 the UNSTABLE column cannot mean anything, which is why n=1 is a smoke test and
not a measurement.

What the failures actually were, read off the transcripts rather than inferred:

- **A contradiction inside the package, now fixed.** A request to loosen an alerting cutoff
  routed to `FRD-02` where the case expects `FIN-03`. The model was following the text: the
  boundary sentence in `fraud-model-risk-guardrails.md` claimed threshold governance was
  stated *in full* there, while `procedure-index.md` made `FIN-03` canonical for a threshold
  change. Both boundary sentences now state the precedence — tuning during design is `FRD-02`,
  changing a live value is `FIN-03`.
- **Answering from the index row instead of the module.** Two cases produced a fluent, largely
  correct answer having opened `procedure-index.md` only — one opened nothing at all. This is
  the exact failure `module_recall` was added to catch, and it would have scored a clean card
  on the other seven metrics. `SKILL.md` step 1 now says a `Required output` cell is a routing
  label and not the procedure.
- **A metric mis-scope, now fixed.** The negative case answered a concept question directly and
  loaded nothing, which is precisely what it asks for, yet was charged `primary_accuracy` for
  naming `ALG-01` against an empty expectation. `primary_accuracy` no longer applies to a
  negative case; `negative_violation` is what scores it.
- **Two boundary disagreements that are still open**, both listed under Outstanding: `SRC-01`
  did not fire on a framework-choice request (version-sensitive by the router's own rule),
  and an eval-set request fired `JDG-01/02/03` where the case expects none — while
  `procedure-index.md` gives `JDG-04` the trigger "create an evaluation set". The case and the
  index disagree; a precedence rule settles it, not a re-scored run.

### No judge in layer 2

Every layer-2 metric is a set comparison against an authored expectation: zero variance,
zero cost, and reproducible from the report alone. Handing that to a model would replace a
`==` with a sampled opinion — added variance and added spend on a question that already has
an exact answer, and per JDG-03 an uncalibrated judge score is a reading from an unknown
function, not a measurement. `eval/judge/protocol.md` forbids the judge scoring anything
checkable for the same reason.

### Repeats

Module selection is probabilistic, so one green run means nothing. `-n <repeats>` replays
each case and reports a pass *fraction*, and any case that neither always passes nor always
fails is listed under UNSTABLE. An unstable case is worse than a failing one: it passes the
demo and fails in production.

## Layer 3 — artifact judging (model, calibrated, not automated here)

`eval/judge/protocol.md` and `eval/judge/artifact-rubric.md`.

Measures: qualities of the produced artifact that no string comparison reaches — whether
required output elements are actually populated, whether rejected alternatives carry
reasons, whether a Review states findings before its verdict.

Does not measure: anything layers 1 and 2 already decide, which the protocol forbids the
judge from re-deciding. There is no runnable layer-3 harness in this repo — running one
needs a judge model, a cross-family choice, and a calibration seed set, all of which are
maintainer decisions.

## Outstanding (nobody has decided these; the eval does not hide them)

- Boundary sets that turn on whether an incidental mention of a trigger word activates a
  compound boundary: `route-dst-02-1` ("start the whole thing over" vs `HRN-02`),
  `route-dst-03-1` ("two workers" vs `ARC-03`), `route-reg-05-1` ("signed off" vs `HRN-02`),
  and the seven FIN/FRD cases against `REG-01`'s "payments" regime. Each case `note` states the
  reading it used. A precedence rule in `SKILL.md` settles all of them at once.
- `procedure-index.md` gives `SRC-01` the trigger "make material factual claims", far broader
  than `SKILL.md`'s version-sensitive/provider-specific/named-source reading. The cases use the
  narrow reading; the index text should be tightened to match, or `false_boundary_rate` will
  penalise correct behaviour.
- No precedence between `MEM-01` and `REG-04` for regulated data in agent memory, so no case
  covers that intersection.
- `procedure-index.md` gives `JDG-04` the trigger "Create an evaluation set", so an eval-set
  request arguably must fire a judge-calibration boundary — but `route-eva-01-1` and
  `route-eva-01-2` expect none. The first live run fired `JDG-01/02/03` there. Either the
  index trigger narrows to "state a numeric release threshold", or those two cases gain
  `JDG-04`. Until one of them happens, `false_boundary_rate` on the EVA cases is measuring an
  unsettled question rather than a defect.
- Nothing measures *auto-activation*: every case invokes the skill explicitly, so the
  `description` field — the only thing that decides whether the skill fires at all in a real
  session — is untested by all three layers.
- Architectural recommendations carried inside module bodies have no procedure ID, so no layer
  reaches them: layer 2 scores routing sets and never reads the answer, and layer 3 scores against
  a `Required output:` cell they do not appear in. An agent can route perfectly and still import a
  pattern at the wrong scale. Draft cases and a proposed C5 criterion: [coverage-plan.md](coverage-plan.md).
- The `command` provider passes no timeout, so a hung runner hangs the run. Whether a timeout
  belongs there, and what it would be, is a maintainer call.

## Thresholds

There is no pass mark, tolerance, minimum n, or acceptance number anywhere in `eval/`.
The tooling reports measurements. **The maintainer owns every bar** — which metrics block a
release, what value each must reach, how many repeats count as stable, and how large the
calibration set must be. A number that encodes a tolerance does not belong in this repo.

## Honest limitation

Measuring on one model tells you about that model, and nothing else. Skill text pruned
until it is just sufficient for a strong model can under-serve a weaker one: the strong
model infers the step that was cut, the weak model skips it. A lower-bound run on a small
model is a separate exercise with its own report — do not read a strong-model number as a
statement about the package.
