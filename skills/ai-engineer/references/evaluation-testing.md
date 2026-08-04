# Evaluation and Testing

## Operating Boundary

Use this module to explain or design evaluation datasets, metrics, graders, experiments, benchmarks, and release gates for the user's AI system. By default, return the requested evaluation plan or specification. Execute an evaluation only when the user explicitly asks to run it and the target system, data, tools, budget, and authority are available. The maintainer regression files referenced at the end test this skill itself and are not part of ordinary user-task execution.

## Contents

- Evaluation model
- Dataset lifecycle
- Metrics by layer
- Judge discipline
- Agent tests
- Release gates

## Evaluation Model

Separate:

1. deterministic software correctness;
2. ingestion and retrieval quality;
3. model output quality;
4. tool/action correctness;
5. trajectory efficiency and safety;
6. end-user task outcome;
7. production reliability, latency and cost.

One aggregate score cannot diagnose these layers.

## ML System Evaluation Discipline

- Connect the business outcome, online/product metric, offline model metric, optimization loss, acceptance threshold, and guardrail metrics. Document where the causal bridge is assumed rather than demonstrated.
- Make train, validation, and test boundaries imitate what will actually be unknown at prediction time. Prefer time-, user-, group-, geography-, device-, or entity-aware splits when random splitting would leak identity or future information.
- Freeze a baseline ladder: current/manual workflow, constant or heuristic, simple statistical/ML model, then complex candidate. Compare quality together with latency, cost, operational burden, and failure behavior.
- Analyze learning curves, residuals, best/worst cases, costly errors, important cohorts, and corners before tuning or replacing the model. Route the earliest failing layer to data, labels, features, objective, validation, model, integration, or decision policy.
- Define how evaluation changes as data and behavior drift, how failures enter a reviewed regression set, and who owns each release threshold.

Use [MLD-01](ml-system-design-lifecycle.md) for the complete design sequence and [MLD-02](ml-system-design-lifecycle.md) for a stage-aware design review.

## EVA-01 — Evaluation Dataset Lifecycle

Create representative normal, edge, adversarial and policy cases. Preserve raw inputs, expected evidence, acceptable outcome/rubric, forbidden behavior, metadata and dataset version. Split development and release sets. Add production failures only after review and deduplication; avoid training graders on the hidden release set.

## EVA-02 — Three-Level Agent Evaluation

For every agent case score separately:

1. environment/task outcome using deterministic evidence where possible;
2. trajectory, policy, authorization, and efficiency;
3. artifact quality against a task-specific rubric.

Then record latency, cost, variance, retries, escalation, and trace completeness. A scalar aggregate may support ranking but never replaces the diagnostic dimensions.

### Metrics by layer

| Layer | Examples |
|---|---|
| Retrieval | recall@k, precision@k, ranking, permission correctness |
| Grounding | faithfulness, citation correctness, unsupported-claim rate |
| Output | schema validity, factuality, completeness, style constraints |
| Tool use | correct tool, arguments, authorization, side effect and recovery |
| Agent trajectory | success, steps, loops, unnecessary calls, escalation quality |
| Operations | latency percentiles, error rate, token/cost, saturation, fallback rate |
| Product | task completion, time saved, correction, abandonment, user trust |

Do not collapse retrieval and generation into one RAG score. Faithfulness is support by retrieved context, not truth about the world. Calibrate every threshold on representative system data and measure retrieval sufficiency independently. For long context, compare the same task with focused and progressively bloated context at several fill levels; track quality, missed constraints, latency, and cost.

## EVA-03 — LLM-as-Judge Discipline

Write a narrow rubric with observable criteria. Calibrate against human labels, measure disagreement, randomize position where comparisons are used, prevent the judge from seeing irrelevant identifiers, and retain judge model/prompt/version. Use deterministic checks whenever possible. Do not let the same model architecture define, produce and solely judge success on high-risk tasks.

`temperature=0` may reduce sampling variance but does not guarantee deterministic or unbiased judgment. Repeat material stochastic evaluations, monitor variance, and use multiple judges or human adjudication when disagreement matters.

### Mandatory judge record order

Do not lead with a verdict, score, praise, or summary judgment. Emit and decide in this order:

1. omissions, contradictions, and findings with severity, evidence, and fix;
2. required-factor coverage and explicit gaps;
3. independent scores by dimension;
4. verdict constrained by the findings;
5. optional additions.

Each optional addition must contain `reason`, provenance `source_class`, `required: true|false`, and `changes_verdict_to_incomplete: true|false`. An unrelated Optional item remains non-blocking. A response that says "not ready" before presenting its Major/Critical finding still violates the findings-first gate.

## Agent Tests

Test:

- tool schema validation and malformed output;
- denied permission and unavailable dependency;
- prompt injection inside retrieved/tool content;
- repeated or delayed tool responses;
- idempotent retry and partial completion;
- checkpoint, pause, edit, reject and resume;
- budget and termination enforcement;
- memory poisoning and stale context;
- conflicting agent results and arbitration;
- abstention and human escalation.

## Release Gate

Require task success above baseline; zero critical policy violations; acceptable worst-case cases; bounded latency/cost; tested fallback and rollback; trace completeness; and named operational owner. Canary before full rollout and compare the same metrics used offline.

## Completeness, Grounding, and Anti-Sycophancy Gates

- Freeze atomic requirements and required factors before reading a candidate's self-assessment.
- Derive and emit findings from artifacts/evidence first; only afterward emit severity-adjusted scores and the verdict. A correct verdict in the wrong order fails the judge protocol.
- Require every factor to be covered, explicitly not applicable, or reported missing.
- Require provenance and a locator for precise numbers, named cases, source claims, quotations, current API behavior, and guarantees.
- Cap the verdict below ready and prohibit a maximum score while any `Critical` or `Major` finding remains.
- Treat agreement with the candidate or other judges as neither evidence nor correctness.
- Keep hidden paraphrases that describe symptoms without leaking target technique names.

While maintaining this public skill, use [routing-tests.md](routing-tests.md) as the behavior boundary and run `scripts/validate_public_skill.py`. Keep any private or organization-specific evaluation packages outside the distributed skill. Do not load or run maintainer artifacts merely because a user asks about evaluation. Use REV-01, SRC-01, and ASM-01 only when their review, source, or guarantee boundaries apply.

## Source Depth

Use [MLD-02](ml-system-design-lifecycle.md) for stage-aware review. Add deeper book or organization-specific variants only through [source-extension.md](source-extension.md).
