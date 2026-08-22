# Evaluation and Testing

## Operating Boundary

Use this module to explain or design evaluation datasets, metrics, graders, experiments, benchmarks, and release gates for the user's AI system. By default, return the requested evaluation plan or specification. Execute an evaluation only when the user explicitly asks to run it and the target system, data, tools, budget, and authority are available. The maintainer regression files referenced at the end test this skill itself and are not part of ordinary user-task execution.

## Contents

- Evaluation Model
- ML System Evaluation Discipline
- EVA-01 Evaluation Dataset Lifecycle
- EVA-02 Three-Level Agent Evaluation
- EVA-03 LLM-as-Judge Discipline
- Agent Tests
- Release Gate
- Completeness, Grounding, and Anti-Sycophancy Gates

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

For the normal bucket specifically, simulating a user is an alternative to writing cases by hand: define personas with role, goal, starting context and a turn budget, run them against the system, and keep the transcripts. Multi-turn traces produced this way carry the interruptions, restatements and partial answers a hand-written case often omits. A transcript is an input, not a case: it becomes one only when a human sets its acceptable outcome and forbidden behavior, because the system's own output is not a label and scoring against it measures agreement with the generator (JDG-01). Generated cases inherit the generator's distribution, so record per-case provenance and hold them in the development split; they reach the frozen release set only by reviewed addition (JDG-04). The mechanism fills the normal bucket only: a simulated user of any temperament cannot produce a case its author did not conceive, so personas do not fill the edge, adversarial or policy strata, and a persona set built on the system's own assumptions inherits its blind spots. Version the persona set with the dataset; changing a persona changes the cases. `ENGINEERING_SYNTHESIS`

The adversarial and policy strata need an external source for the same reason. Published agentic-attack corpora carry cases nobody on the build team thought of - the OWASP FinBot CTF in [current-standards.md](current-standards.md) is one, with classes for recon, policy bypass, data exfiltration, destructive action and remote code execution. Import the attack pattern, not the case: a published case is contaminated by construction, so restate it against this system's own tools, data and authority boundaries, and record where it came from.

Its case format is worth copying whatever the source. One declarative file per case, carrying: a stable identifier; the objective in prose; success criteria written as conditions on system state; category and difficulty; labels against every external framework the case maps to, so a category revision is a diff rather than an audit; prerequisites naming the cases that must pass first, which makes the corpus ordered instead of a bag; and the name plus configuration of the check that decides the case, held separately from the case itself so one check serves many cases. A case in that shape is reviewable by someone who did not write it. Two further rules earn their place: where a case can also be passed by a generic attack that would pass every case, say so in the case and discount that path, or the corpus measures how well the generic attack works and stops distinguishing the specific defect each case was built for; and keep the graduated hints, if any, as data in the case, because how much scaffolding a system needs before it succeeds is itself a measurement. `ENGINEERING_SYNTHESIS`

## EVA-02 — Three-Level Agent Evaluation

For every agent case score separately:

1. environment/task outcome using deterministic evidence where possible;
2. trajectory, policy, authorization, and efficiency;
3. artifact quality against a task-specific rubric.

Then record latency, cost, variance, retries, escalation, and trace completeness. A scalar aggregate may support ranking but never replaces the diagnostic dimensions.

Write the outcome criterion as a condition on system state wherever the environment can be observed, not as a condition on the answer text: not "the reply contains X" but "this record moved from rejected to active, and reached it through more than one transition". A string match passes a system that narrates the right thing while doing the wrong one, fails a system that does the right thing in unexpected words, and cannot see a multi-step path where no single step looks wrong. Two checks are involved and they are not the same: a per-case check answers whether this case's condition held in this run, and an aggregate check answers a question over the whole history - whether the behavior recurred, across how many runs, since when - which a per-run assertion cannot express. Give both the same result shape: the boolean, the evidence that decided it as a retained audit trail, and a confidence that is 1.0 for a deterministic condition and lower only where a pattern match or a judge was involved. A reader who cannot tell which kind of check produced a verdict cannot tell how much the verdict is worth. `ENGINEERING_SYNTHESIS`

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

Write a narrow rubric with observable criteria. Calibrate against human labels, measure disagreement, score both orders and count a win only when preference holds in both (JDG-01), prevent the judge from seeing irrelevant identifiers, and retain judge model/prompt/version. Use deterministic checks whenever possible. Do not let the same model architecture define, produce and solely judge success on high-risk tasks.

`temperature=0` may reduce sampling variance but does not guarantee deterministic or unbiased judgment. Repeat material stochastic evaluations, monitor variance, and escalate disagreement to human adjudication; multi-judge ensembles are unproven cost (JDG-03).

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
- cross-tenant isolation: the same case run as two tenants, leaking in neither direction;
- inter-agent protocol spoofing and replay: a forged or re-sent message from a peer agent is rejected, not acted on;
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

While maintaining this public skill, use [routing-checklist.md](routing-checklist.md) as the behavior boundary and run `scripts/validate_public_skill.py`. Keep any private or organization-specific evaluation packages outside the distributed skill. Do not load or run maintainer artifacts merely because a user asks about evaluation. Use REV-01, SRC-01, and ASM-01 only when their review, source, or guarantee boundaries apply.

Use [MLD-02](ml-system-design-lifecycle.md) for stage-aware review.
