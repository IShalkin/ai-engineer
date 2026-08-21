# Layer 3 Artifact Rubric

Governed by `protocol.md` in this directory; authority is JDG-01..JDG-04 in
`skills/ai-engineer/references/judge-bias-and-calibration.md`. **If this rubric contradicts the
module, the module wins.**

Version this file with the judge prompt hash and rubric version in the run record; an edit here is a
behavioural change to the measurement (JDG-02 step 6).

## How to use it

- **One criterion per judge call.** Never score two criteria in one context (JDG-01 anchoring).
- **Evidence first, then the enumerated steps, then the level.** Quote the artifact span you relied
  on before naming a level (JDG-02 step 4; EVA-03 mandatory record order).
- **Reference.** The `Required output:` cell of the procedure under review is supplied verbatim as
  the reference for C1. Criteria are scored against *that cell*, never against general writing
  quality, polish, tone, or length.
- **No deduction for compliance.** A stated gap, an explicit "not applicable", a named uncertainty,
  an abstention, or a refusal to answer **may not lower any level** (JDG-02 step 2). An artifact that
  says "retrieval config unknown, assumption stated" is more complete than one that guesses.
- **The judge sees no identifiers.** Producing model, procedure name/ID, project, employer, product,
  file paths are stripped before the call (JDG-01 self-enhancement).
- **Levels are ordinal labels, not a total.** Do not sum them, do not average them into one quality
  number, do not compare a total across judge versions. **No level is a passing level.** The
  maintainer sets any bar, if any bar exists.

Level vocabulary, all four criteria: **Absent / Partial / Complete**, plus **REFUSE-TO-SCORE**.

---

## C1 — Required-output completeness

Predicate: *every element named in the reference `Required output:` cell is present in the artifact
as substance, or is explicitly marked missing or not applicable with a reason.*

Count, do not rate (JDG-02 step 3). Enumerate the reference cell's elements as `n`. For each, record
`present` (substantive content addressing it), `declared-absent` (explicitly named as missing/NA with
a reason — counts as covered), or `missing` (no mention). Emit the list and the counts
`present / declared-absent / missing` before the level.

| Level | Anchor |
|---|---|
| Absent | Two or more reference elements are `missing` with no mention anywhere in the artifact, **or** the artifact addresses a different subject than the reference cell. |
| Partial | Exactly one reference element is `missing`. All others are `present` or `declared-absent`. |
| Complete | Zero `missing`. Every reference element is `present` or `declared-absent` with a reason. |

Not evidence of completeness: a section heading matching the element name with no content under it —
score that heading `missing` and quote it. Length, formatting, and headings count for nothing here.

## C2 — Named assumptions

Predicate: *each assumption the artifact depends on is stated as an assumption, in its own sentence,
attributable to the decision it supports.*

An assumption is *named* when the artifact marks it (e.g. "assuming", "we assume", "unknown; taken
as", an Assumptions section) **and** the reader can tell which recommendation would change if it were
false. A factual-sounding sentence about an unverified input is **not** a named assumption; quote it
and record it as unnamed.

| Level | Anchor |
|---|---|
| Absent | No sentence in the artifact is marked as an assumption, while at least one unverified input is asserted as fact (quote it). |
| Partial | At least one assumption is marked, **and** at least one unverified input is still asserted as fact (quote both). |
| Complete | Every unverified input the recommendation rests on is marked as an assumption, and each is tied to the decision it supports. |

Score `Complete` where the artifact genuinely rests on no unverified input and says so. An empty
Assumptions section with no such statement is `Absent`.

## C3 — Rejected alternatives

Predicate: *at least one alternative that was actually available is named, and the reason for
rejecting it is given in terms of this problem.*

| Level | Anchor |
|---|---|
| Absent | No alternative is named — only the chosen approach appears. |
| Partial | An alternative is named but the rejection reason is missing, or is a generic property of the alternative ("too complex", "not scalable", "overkill") that does not reference anything in this problem. |
| Complete | An alternative is named **and** rejected on a stated property of *this* problem — a constraint, a cost, a data or latency fact, an ownership boundary, a risk named elsewhere in the artifact. |

If the reference `Required output:` cell does not call for alternatives, record
`not-required-by-reference` and do not score this criterion. Absence of an uncalled-for element is
not a defect.

## C4 — Mode match

Predicate: *the artifact is the mode that was requested* — Explain, Design, Review, or Implement, as
defined in the skill's Operating Modes.

Observable markers, quote one:

- **Explain** — answers the concept/trade-off; no build plan, no repo mutation.
- **Design** — produces the architecture/decision/plan artifact; interfaces, risks, ownership.
- **Review** — findings with evidence and severity **before** any verdict or score; does not mutate.
- **Implement** — a scoped change plus the verification of that change.

| Level | Anchor |
|---|---|
| Absent | The artifact is a different mode than requested — e.g. a Review request answered with a redesign, or an Explain request answered with a repository change. |
| Partial | The requested mode is present but a foreign mode's output is mixed in unrequested (e.g. Explain plus an unsolicited implementation plan), or a Review leads with a verdict/score before its findings. |
| Complete | The artifact is the requested mode, and a Review's findings precede its verdict. |

A Review that emits a verdict, score, praise, or summary judgment before its findings is at best
`Partial` regardless of whether the verdict is correct (EVA-03 mandatory record order).

---

## REFUSE-TO-SCORE

Emit `REFUSE-TO-SCORE` for a criterion, with the reason and what was missing, whenever the judge
cannot evaluate it from what it was given. **A forced score on insufficient evidence is worse than a
gap: it is indistinguishable from a real measurement downstream, and it silently becomes a data
point.** Refusal is the correct output and **never lowers any level** (JDG-02 step 2).

Refuse when any of these holds:

- The reference `Required output:` cell was not supplied, or was supplied empty or truncated (C1 has
  no reference).
- The artifact is empty, truncated mid-sentence, or a stub of headings only.
- The artifact is unreadable as delivered — encoding damage, interleaved unrelated content, an
  unresolved placeholder where the substance should be.
- The requested mode was not supplied to the judge (C4 has nothing to compare against).
- The criterion requires a fact outside the judge's context to decide — whether a cited identifier
  resolves, whether a number is right, whether a module was read, whether a file exists. That is a
  deterministic check, not a low-confidence score (JDG-01, `protocol.md` section 1).
- Deciding the level requires the judge to guess which of two readings of the request was intended.

Required refusal shape: `REFUSE-TO-SCORE | criterion | what was missing | what to supply to make it
scorable`. A refusal is a finding about the harness, routed to the maintainer, not a finding about
the artifact.

---

**Owner of every threshold, every level-to-outcome mapping, and any decision to aggregate these
criteria into a single number: the maintainer.** This rubric measures; it does not decide.
