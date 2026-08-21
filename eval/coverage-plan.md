# Coverage plan — proportionality of imported patterns

Status: plan only. Nothing here is implemented, and no case or criterion below has been run.

## The gap

Several module bodies carry architectural recommendations imported from systems observed
elsewhere and generalized — a shared runtime seam for agent plumbing, prompt storage as its own
boundary, a fan-out/merge/human-point/gate pipeline shape, registry-based capability extension,
platform-layer observability. All five are labelled `ENGINEERING_SYNTHESIS`. Three of the five —
the seam, the prompt boundary, the registry extension — state a threshold, a cost and a
non-application condition. The pipeline shape states its n=1 provenance and its per-transition
obligations but no cost; platform observability states a trigger and a non-application clause but
no cost. Those two gaps are real and unclosed.

Coverage by layer:

- **Layer 1** checks that procedure IDs, modules and router rows stay consistent. These
  recommendations are prose inside module bodies with no ID, so nothing addresses them.
- **Layer 2** compares routing sets — primary, boundaries, modules, mode. It never reads the
  answer, so it cannot see whether a loaded module's advice was applied at the wrong scale.
- **Layer 3** reaches some of them already, and the earlier version of this plan overstated the
  gap. C1 scores against the `Required output:` cell, and where that cell carries a
  proportionality element the pattern is already scored: `HRN-03`'s cell requires the
  **one-agent comparison**, which is exactly what an unjustified fan-out topology fails, and
  `ARC-02` requires **adjacent levels rejected**. The genuinely unreached ones are the seam, the
  prompt boundary and the registry extension, whose modules' cells carry no proportionality
  element. C3 is not the answer for those: it asks whether an alternative was named and rejected,
  not whether an adopted pattern met its stated threshold.

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

Draft cases below. `--check-cases` is necessary and **not sufficient** for vetting them: its
boundary loop iterates the IDs a case declares, so a case that *omits* a required boundary passes
with `ERRORS: 0`. A missing boundary is findable only by re-reading `SKILL.md`'s compound-boundary
paragraph and the trigger invariants in the canonical modules against each request. Two further
mechanics to know before running it: the shard-concatenation invariant derives its shard directory
from the cases file's own directory, so pointing `--cases` at any file in `eval/` other than
`cases.jsonl` produces a spurious concatenation error — draft outside `eval/` — and every request
below deliberately avoids naming a procedure ID or module filename.

```json
{"id": "prop-single-agent-1", "request": "We get about thirty support emails a day and want each one tagged with a category and an urgency before a human reads it. What should we build?", "expect_primary": "ARC-02", "expect_modules": ["architecture-decision-engine.md"], "forbid_modules": ["distributed-agent-systems.md", "agent-harness-loop.md"], "expect_boundary_ids": [], "expect_mode": "design", "negative": false, "source": "authored", "note": "Largely redundant: route-arc-01-1 already forbids agent-harness-loop.md on a support-inbox request, and route-prm-01-1's note already claims to catch inflation into a multi-agent design. Retained only for the ARC-02-over-ARC-01 tie: the workflow here is not yet written down, which is ARC-01 territory, but the ask names a determinate task, so the shape ladder applies. Delete this case if the tie is settled elsewhere."}
{"id": "prop-prototype-obs-1", "request": "I want to find out whether a model can do this task at all — throwaway script, my laptop, this week. What do I need in place before I start?", "expect_primary": "ARC-01", "expect_modules": ["architecture-decision-engine.md"], "forbid_modules": ["production-operations.md", "managed-agent-runtimes.md"], "expect_boundary_ids": [], "expect_mode": "design", "negative": false, "source": "authored", "note": "Exploratory, single process, no production intent. Catches platform-layer observability and runtime constraints applied to a prototype. Tie: 'find out whether a model can do this task at all' is ALG-01's trigger verbatim and shares a router row with ARC-01; ARC-01 is expected because the ask is what to have in place before starting, not whether an LLM is the right method. Unsettled — if a run picks ALG-01 the case is the thing to reconsider first."}
{"id": "prop-single-app-prompt-1", "request": "One service, one prompt, and we keep breaking it whenever we edit it. How should we manage that?", "expect_primary": "PRM-01", "expect_modules": ["context-prompt-engineering.md"], "forbid_modules": ["production-operations.md", "agent-harness-loop.md"], "expect_boundary_ids": [], "expect_mode": "design", "negative": false, "source": "authored", "note": "One caller, so versioning the prompt with its code is the sufficient design. No tie found: PRM-02 covers diagnosing a prompt failure, and this asks how to manage change, which is PRM-01's versioned contract. Layer 2 can only confirm the routing stays local; whether the answer proposes a separate prompt service is C5's question."}
{"id": "prop-two-agents-1", "request": "We have two small assistants, one drafts replies and one checks them against policy. Should they share a common framework layer?", "expect_primary": "HRN-03", "expect_modules": ["agent-harness-loop.md", "architecture-decision-engine.md"], "forbid_modules": ["distributed-agent-systems.md"], "expect_boundary_ids": ["ARC-03"], "expect_mode": "design", "negative": false, "source": "authored", "note": "Tie: the question asked is about a shared implementation seam (HRN-03), but a drafter plus a reviewer is two participants, and the ARC-03 trigger invariant in architecture-decision-engine.md fires on reviewers explicitly and forbids treating HRN-03 as a substitute. Resolved as HRN-03 primary with ARC-03 as a fired boundary, so authority and independence mapping is not dropped. An earlier draft expected HRN-03 alone with no boundary, which would have scored correct ARC-03 routing as a failure. Layer 2 cannot see premature abstraction at n=2; that is C5's question."}
```

Two of these four carry a note saying layer 2 cannot decide the thing the case is named after.
That is the honest state, not a defect in the case — it is why Part B exists.

## Part B — Layer 3, a new criterion

**C5 — Proportionality of an adopted pattern.**

Predicate: *every architectural pattern the artifact adopts either meets the threshold the
source module states for it, or the artifact states why it applies despite the threshold.*

**Split it in two, because half of it is arithmetic.** `judge/protocol.md` bars the judge from
scoring "anything with a canonical form — IDs, hashes, counts, file paths", and the thresholds
here are counts: how many agents share the plumbing, how many independently deployed callers share
the prompt. Handing a count to a judge replaces a decidable fact with an opinion that can override
it, which is the override channel `protocol.md` exists to close.

- **C5a, deterministic:** extract the count the threshold names — participants, callers, capability
  owners — and compare. No judge.
- **C5b, judged:** only where the artifact adopts a pattern below its threshold *and* offers a
  reason. The judged question is whether that reason names a fact of this problem, not whether the
  count was met.

| Level (C5b) | Anchor |
|---|---|
| `not-applicable` | The artifact adopts no pattern carrying a stated threshold. Record it and do not score — an artifact that adopts nothing is not thereby proportionate, and scoring it `Complete` would make an empty answer indistinguishable from a reasoned one. |
| Absent | A pattern is adopted below its threshold and no reason for applying it anyway appears. |
| Partial | A reason appears but is a generic property of the pattern ("cleaner", "more scalable") rather than a fact of this problem, or the artifact picks a side of a borderline case without saying which fact decided it. |
| Complete | Every below-threshold adoption carries a reason resting on a stated constraint, cost, or boundary of this problem, and names the cost being accepted. |

Governed by `judge/protocol.md` first and `judge/artifact-rubric.md` second; where either
contradicts the modules, the module wins and C5 is the defect. Inherits one criterion per judge
call, evidence quoted before the level, no deduction where the artifact states a gap or declines a
pattern, and `REFUSE-TO-SCORE` where the level needs a fact outside the judge's context.

**C5b refuses on all three Part-B patterns as those thresholds are currently written, and that is
the finding.** The seam threshold is "the number of agents actually sharing the plumbing **and
observed drift between them**"; the registry threshold is "capabilities added **by people other
than the orchestrator's owner**"; the prompt threshold says "**several** independently deployed
callers". Observed drift and who adds capabilities are facts about an organisation, not about a
design document, and "several" needs the judge to guess a reading. So C5b returns
`REFUSE-TO-SCORE` on all three — a harness finding routed to the maintainer, not a measurement.
The fix is upstream: make those thresholds artifact-observable, or accept that Part B measures
nothing until they are. C5a is unaffected where a count is stated.

Per `JDG-03`, C5b produces nothing trustworthy before minimal-pair calibration, and no layer-3
harness exists here. C5 is a specification, not a measurement.

## Sequence

1. Run `--check-cases` on the four draft cases from a path outside `eval/`, and treat a clean run
   as necessary only. Separately, walk each request against `SKILL.md`'s compound-boundary
   paragraph and the trigger invariants in the canonical modules, because an omitted required
   boundary is exactly what the checker cannot see.
2. Run them against a real agent with `-n` high enough that UNSTABLE means something.
3. Read failures off transcripts before changing any module text — a case may be wrong.
4. Leave C5 unimplemented until a judge harness, a cross-family judge choice, and a calibration
   seed set exist. Specifying it earlier is cheap; running it uncalibrated is not.

## A fourth axis worth adding: does the package teach?

Layers 1–3 measure structure, routing and artifact quality. None asks whether a reader who
only has this package can act correctly from it — which is the property that matters once other
people use it.

Shape: start a fresh session with the package and no other context, put questions to it whose
answers exist only in the module bodies, and score in two parts kept apart.

The mechanical half asks each question in a form with a determinate answer the module states — the
option it mandates, the state it requires, the count in a `Required output` cell — and compares the
answer to that. **Not a terms-must-appear check:** name-dropping "checkpointer" or "terminal state"
without using either correctly clears a keyword floor, which is the substring test this repo
already rejects for cases, and a heading matching an element name is scored `missing` by
`judge/artifact-rubric.md` for the same reason. **Exit stays 0 on a miss**, with the miss recorded:
non-zero is reserved repo-wide for harness error, so that a crashed runner and a low score are not
the same signal.

Three separate reasons the two halves must not be folded into one number, none of them stylistic.
`JDG-01`'s anchoring row measures a judge scoring a second attribute in the context where it
scored the first: the second score is all but fixed by the first, r = 0.979 against r = 0.315 for
humans. That row covers judge-produced anchors; extending it to an externally supplied
deterministic result as the anchor, and predicting the direction, is `ENGINEERING_SYNTHESIS` — the
measurement does not cover this configuration and no study isolating it was located, so cite no
paper for the direction. `JDG-04` step 6: the mechanical half is a blocking gate, and averaging a
blocking gate into a composite is how a failing stratum gets washed out. And the module's closing
rule: a judge dimension duplicating a deterministic check is wasted cost and an invitation to
override a fact already decided.

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
