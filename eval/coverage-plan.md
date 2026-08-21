# Coverage plan — proportionality of imported patterns

Status: plan only. Nothing here is implemented, and no case or criterion below has been run.

## The gap

Several module bodies carry architectural recommendations imported from systems observed
elsewhere and generalized — a shared runtime seam for agent plumbing, prompt storage as its own
boundary, a fan-out/merge/human-point/gate pipeline shape, registry-based capability extension,
platform-layer observability. Each now states a threshold, a cost, and a non-application
condition, and each is labelled `ENGINEERING_SYNTHESIS`.

None of them is measured, by any layer:

- **Layer 1** checks that procedure IDs, modules and router rows stay consistent. These
  recommendations are prose inside module bodies with no ID, so nothing addresses them.
- **Layer 2** compares routing sets — primary, boundaries, modules, mode. It never reads the
  answer, so it cannot see whether a loaded module's advice was applied at the wrong scale.
- **Layer 3** scores an artifact against the procedure's `Required output:` cell. These
  recommendations appear in no `Required output:` cell, so C1 does not reach them, and C3 asks
  whether an alternative was named and rejected — not whether an adopted pattern met its stated
  threshold.

The failure this leaves open: an agent reads a module for a legitimate reason, then imports a
pattern whose threshold the situation does not meet — a shared base class for two agents, a
prompt service for one application, a fan-out topology where one agent suffices. Every routing
metric scores clean while the advice makes the design worse.

## Deliberately not creating new procedure IDs

An ID with no case behind it reads as routable and measured when it is neither. That is the
defect the SHA-256 table was deleted for. These stay in-module until there is coverage that
justifies promoting them.

## Part A — Layer 2, what is observable today

Over-reach is visible to layer 2 only when it forces a *module or primary* that the case
forbids. That holds for two of the five patterns and not for the other three; the split is
stated rather than smoothed over.

| Pattern | Layer-2 signal | Observable |
|---|---|---|
| Pipeline shape | routing a one-agent task to a multi-participant primary | yes |
| Platform observability | loading production-operations for exploratory work | yes |
| Shared runtime seam | the module legitimately loads either way | no — Part B |
| Prompt storage boundary | the module legitimately loads either way | no — Part B |
| Registry extension | inside a legitimately loaded module | no — Part B |

Draft cases, to be checked with `--check-cases` before use (boundary IDs unverified against the
index; every request deliberately avoids naming any procedure ID or module filename):

```json
{"id": "prop-single-agent-1", "request": "We get about thirty support emails a day and want each one tagged with a category and an urgency before a human reads it. What should we build?", "expect_primary": "ARC-02", "expect_modules": ["architecture-decision-engine.md"], "forbid_modules": ["distributed-agent-systems.md", "agent-harness-loop.md"], "expect_boundary_ids": [], "expect_mode": "design", "negative": false, "source": "authored", "note": "Volume and task shape are served by one model call behind ordinary code. Catches a selector that reaches for a participant topology because the module body names one."}
{"id": "prop-prototype-obs-1", "request": "I want to find out whether a model can do this task at all — throwaway script, my laptop, this week. What do I need in place before I start?", "expect_primary": "ARC-01", "expect_modules": ["architecture-decision-engine.md"], "forbid_modules": ["production-operations.md", "managed-agent-runtimes.md"], "expect_boundary_ids": [], "expect_mode": "design", "negative": false, "source": "authored", "note": "Exploratory, single process, no production intent. Catches platform-layer observability and runtime constraints applied to a prototype."}
{"id": "prop-single-app-prompt-1", "request": "One service, one prompt, and we keep breaking it whenever we edit it. How should we manage that?", "expect_primary": "PRM-01", "expect_modules": ["context-prompt-engineering.md"], "forbid_modules": ["production-operations.md", "agent-harness-loop.md"], "expect_boundary_ids": [], "expect_mode": "design", "negative": false, "source": "authored", "note": "One caller, so versioning the prompt with its code is the sufficient design. Layer 2 can only confirm the routing stays local; whether the answer proposes a separate prompt service is C5's question."}
{"id": "prop-two-agents-1", "request": "We have two small assistants, one drafts replies and one checks them against policy. Should they share a common framework layer?", "expect_primary": "HRN-03", "expect_modules": ["agent-harness-loop.md"], "forbid_modules": ["distributed-agent-systems.md"], "expect_boundary_ids": [], "expect_mode": "design", "negative": false, "source": "authored", "note": "The question is genuinely about multi-agent structure, so the module load is correct. Layer 2 only confirms it does not escalate to consensus/fault machinery; premature abstraction at n=2 is C5's question."}
```

Two of these four carry a note saying layer 2 cannot decide the thing the case is named after.
That is the honest state, not a defect in the case — it is why Part B exists.

## Part B — Layer 3, a new criterion

**C5 — Proportionality of an adopted pattern.**

Predicate: *every architectural pattern the artifact adopts either meets the threshold the
source module states for it, or the artifact states why it applies despite the threshold.*

| Level | Anchor |
|---|---|
| Absent | The artifact adopts a pattern whose stated threshold the described situation does not meet, and neither the threshold nor a reason for applying it anyway appears. |
| Partial | The threshold is acknowledged but not resolved against the situation, or the situation is borderline and the artifact picks a side without saying which fact decided it. |
| Complete | Every adopted pattern either meets its stated threshold on a fact present in the artifact, or is adopted with an explicit reason that names the cost being accepted. |

Harness requirement: C5 needs the module's threshold and non-application sentences supplied
verbatim as the reference, the way C1 receives the `Required output:` cell. Without that
reference the judge is scoring against its own idea of proportionality — refuse instead.

Inherits every rule in `judge/artifact-rubric.md`: one criterion per judge call, evidence quoted before
the level, no deduction where the artifact states a gap or declines to adopt a pattern, and
`REFUSE-TO-SCORE` wherever the level would need a fact outside the judge's context.

Not scorable as a deterministic check: whether a threshold was met is a reading of the described
situation, which is exactly what a judge is for and exactly what layers 1 and 2 cannot do. Per
JDG-03, C5 produces nothing trustworthy until minimal-pair calibration has run against it, and
there is still no layer-3 harness in this repo — so C5 is a specification, not a measurement.

## Sequence

1. Run `--check-cases` on the four draft cases; fix ids, boundary sets and forbid lists until the
   corpus invariants hold.
2. Run them against a real agent with `-n` high enough that UNSTABLE means something.
3. Read failures off transcripts before changing any module text — a case may be wrong.
4. Leave C5 unimplemented until a judge harness, a cross-family judge choice, and a calibration
   seed set exist. Specifying it earlier is cheap; running it uncalibrated is not.

## A fourth axis worth adding: does the package teach?

Layers 1–3 measure structure, routing and artifact quality. None asks whether a reader who
only has this package can act correctly from it — which is the property that matters once other
people use it.

Shape: start a fresh session with the package and no other context, put questions to it whose
answers exist only in the module bodies, and score in two parts — a mechanical floor over terms
that must appear, with a non-zero exit when it is missed, and a judgement pass archived separately
rather than folded into the same number.

Three separate reasons the two must not mix, none of them stylistic. `JDG-01`'s anchoring row:
a judge scoring a second attribute in the context where it scored the first has its second score
all but fixed by the first, so a judge shown a green mechanical result rates the judgement
dimension higher — two reports of one signal, presented as two-dimensional evidence. `JDG-04`
step 6: the mechanical floor is a blocking gate, and averaging a blocking gate into a composite
is exactly how a failing stratum gets washed out. And the module's closing rule: a judge
dimension that duplicates a deterministic check is wasted cost and an invitation to override a
fact that was already decided.

Distinct from the layers above: layer 2 asks whether the right module was opened, layer 3 whether
the produced artifact was good. This asks whether the text, read cold, is sufficient to produce a
correct answer at all — the failure it catches is a module that is accurate, routable, and
unusable by anyone who was not present when it was written. Pruning text until it is just
sufficient for a strong model is exactly what makes this axis go dark, which is the same concern
the honest-limitation note at the end of `README.md` raises about model strength.

Unresolved: it needs an interactive session per run, so it is manual until something can drive one
headlessly. No threshold is proposed here; the maintainer owns the floor as everywhere else.

## What this plan still will not measure

Auto-activation. Every case invokes the skill explicitly, so the `description` field that decides
whether any of this is reached in a real session remains untested here, as it is everywhere else
in `eval/`.

No pass mark, tolerance or minimum n appears above. The maintainer owns every bar.
