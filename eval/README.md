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

**Layer 1 is green.** Both scripts exit 0. The three findings the tightened checks surfaced on
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

Anything else on stdout is a harness error for that case. Exit status and stderr are
ignored. The harness ships no default command, embeds no model name, and reads no
credential. Model identity and effort are **recorded verbatim from `--model`/`--effort`,
never chosen by the harness** — the harness cannot know what your runner called, so a
number without those flags is a number you cannot attribute. `--date` is required for the
same reason: no clock is read, so a report cannot self-stamp.

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
