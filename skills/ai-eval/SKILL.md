---
name: ai-eval
description: Design or repair how an AI system is measured — metrics, graders, LLM judges, eval-set construction, thresholds, release gates, required n. Use when someone proposes a quality number, when a gate has to decide pass or fail, or when a judge's score is about to be trusted. Runs in its own context so the analysis does not crowd the main conversation.
context: fork
agent: ai-engineer
background: false
effort: max
---

Load these two before deciding anything, in this order:

- [evaluation-testing.md](../ai-engineer/references/evaluation-testing.md) — EVA-01/02/03: eval-set
  design, graders, release gates
- [judge-bias-and-calibration.md](../ai-engineer/references/judge-bias-and-calibration.md) —
  JDG-01…04: judge bias, rubrics, calibration, numeric gates

Add [completeness-provenance.md](../ai-engineer/references/completeness-provenance.md) only if the
task asserts a guarantee, an independence claim, or completeness (ASM-01).

Then produce the evaluation *design*. Do not execute an evaluation unless the caller explicitly asked
you to run it and the target, data and authority are all present — EVA is a design procedure, and a
number produced from a set nobody agreed on is worse than no number.

## What this task usually turns out to be

Four failures recur, and each has a cheaper answer than the one first proposed:

- **A percentage with no denominator.** "≥90% quality" is not a metric: it does not say what is
  measured, on which slice, by whom, or how many items are needed to distinguish 90% from 85%.
  Compute the required n and say it out loud. If n is larger than the eval set anyone will build,
  the threshold is undeliverable and that is the finding.
- **A single LLM judge as the gate.** Measured judge agreement rules this out for anything
  consequential. Either the gate is deterministic, or the judge is one vote among several with a
  unanimity or majority rule, and the residual disagreement rate is published.
- **Human approval treated as a clean label.** Approved material fails its own standards routinely.
  An approval is evidence that no one objected, not that the artefact is correct.
- **A count reported as coverage.** A green suite means previously-found bugs stay fixed. It says
  nothing about the class nobody has thought of. Never let a passing count stand in for a measured
  rate.

## What to return

The metric, the threshold, the slice, the required n, who owns each, and what the design is **blind
to** — stated as a blind spot rather than omitted. A gate that does not publish its coverage
denominator will be read as complete.

Refuse thresholds that are not yours to set. A number that encodes a business or regulatory
tolerance belongs to whoever carries that risk; name them and leave the value unset.
