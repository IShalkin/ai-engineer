# Continuous Improvement

## EVL-01 — Failure-to-Cause Pipeline

**Trigger:** production traces or evaluations show repeated failure.

1. Preserve sanitized trajectories, versions, environment outcome, and user correction.
2. Deduplicate and cluster by observable failure—not by guessed cause.
3. Score three levels separately: environment outcome; process/policy/authorization; artifact quality.
4. Locate the earliest failing layer: requirement, source, context, retrieval, reasoning, tool, permission, effect, evaluator, or operations.
5. Form a causal hypothesis and counterexample.
6. Add representative and boundary cases to a versioned development set; protect held-out release tests.

**Output:** failure cluster with evidence, causal confidence, affected scope, and owner.

## EVL-02 — Smallest Safe Update

Choose the update medium by cause:

| Medium | Use for | Main risk |
|---|---|---|
| Knowledge/experience base | facts, precedents, exceptions, sources | retrieval misses or stale evidence |
| Prompt/skill | explainable scoped decisions and procedures | bloat, conflict, failure to activate |
| Program/harness | deterministic rules, workflow, validation, hard constraints | engineering/maintenance cost |
| Model parameters | implicit high-dimensional capability or style | cost, opacity, regressions |

1. Change the smallest local, auditable, reversible object.
2. Test artifact quality **and** runtime activation/application.
3. Use ablation against the previous version and cheaper alternatives.
4. Run frozen normal, boundary, adversarial, and held-out cases.
5. Approve independently, canary, monitor the same metrics, and retain rollback.

Online agents collect evidence; they do not directly publish changes to their official prompt, skills, evaluator, permissions, or model. Keep evaluators, authority policy, delayed outcomes, and held-out tests outside the mutable area.

## Failure Signals

Live self-modification, self-approved data, visible release tests, changing several layers at once, storing a new rule without testing retrieval, endless prompt accumulation, reward gaming, and promotion without provenance or rollback.

## Source Depth

Deeper variants live in book-derived source packs this package does not ship. Route through [source-extension.md](source-extension.md) (COV-01) and report `blocked_missing_source` if none is installed.
