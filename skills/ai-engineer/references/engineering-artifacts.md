# ART-01 — Engineering Artifacts

## Living ML System Design Document

- Problem, current workflow, stakeholders, goals, antigoals, value, and cost of mistakes
- Prior work, build-versus-buy evidence, data feasibility, and unresolved assumptions
- Business/online/offline metric chain, optimization loss, thresholds, and guardrails
- Data sources, labels, metadata, lineage, quality, representativeness, privacy, and refresh policy
- Production-aware validation boundary, leakage controls, update policy, and uncertainty
- Current/manual, constant/rule, simple-model, and complex-candidate baselines
- Error analysis by learning curve, residual, cohort, best/worst case, and costly corner case
- Reproducible training, feature hypotheses, artifact/version lineage, and tests
- Experiment or rollout measurement, integration contract, fallback, override, and rollback
- Serving requirements, monitoring layers, owner/on-call, runbooks, review cadence, and retirement criteria

Keep decisions and their evidence current. For the full lifecycle use [MLD-01](ml-system-design-lifecycle.md); for a gradecard review use [MLD-02](ml-system-design-lifecycle.md).

## Architecture Decision Record

- Context and user outcome
- Constraints and risks
- Baseline
- Considered system shapes
- Decision and evidence
- State/data/tool/trust boundaries
- Consequences and reversal plan
- Evaluation gate

## Evaluation Plan

- Task and failure taxonomy
- Dataset sources, versions and splits
- Component and end-to-end metrics
- Human and model-judge rubrics
- Normal, edge, adversarial and policy cases
- Baseline and thresholds
- CI and canary gates
- Production sampling and owner

## Tool Specification

- Purpose and non-goals
- Input/output JSON schema
- Read/write effects
- Authentication and authorization
- Timeout/rate/cost limits
- Idempotency/compensation
- Error taxonomy and retry
- Approval policy
- Audit/redaction
- Unit, contract and adversarial tests

## Threat Model

- Assets, actors and trust boundaries
- Data/tool/agent flows
- Threats and abuse cases
- Preventive/detective/recovery controls
- Residual risk and owner
- Security tests and review cadence

## Production Readiness Review

- Versioned artifacts and dependency inventory
- SLOs and capacity
- Quality/safety/eval evidence
- Permissions/secrets/data retention
- Traces, dashboards and alerts
- Fallback, rollback and disaster recovery
- On-call and incident runbook
- Canary plan and stop conditions
