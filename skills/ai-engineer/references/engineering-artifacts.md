# ART-01 — Engineering Artifacts

Tag every artifact with a regime: **normative** (prescribes a decision or rule others must follow), **traceability** (records what actually happened, as evidence), or **projection** (derived from another artifact and authoritative nowhere). A projection is generated from its source so it cannot drift from it — a readout, a summary, a rendered view — and editing one directly is the defect, because the edit is lost on the next generation and contradicts the source until then. If a summary is worth trusting downstream, derive it; if it is hand-written alongside its source, it is a second normative document that will disagree with the first. Do not let a traceability record silently start functioning as a rule, or a normative document decay into an unmaintained history nobody re-reads. A model may draft either; per the Human Authority rule in [security-governance.md](security-governance.md), only a named owner may approve or delete a normative one.

**Authority flows one way.** Anything that enforces — a lint rule, a hook, a CI gate, an agent instruction, a runtime check — cites the decision record it implements and may not author authority of its own. An enforcement layer with no record to cite is the smell: either the decision was never made and should be recorded and accepted first, or it was made elsewhere and this layer has drifted from it. Superseding a record obliges review of everything implementing it, in the same change. `ENGINEERING_SYNTHESIS`

**An accepted normative record is immutable.** Change it by writing a superseding record and marking the old one superseded, atomically and with references in both directions; never by editing accepted content in place. Identifiers are never reused. An agent re-reading a mutated record cannot tell whether the rule it is now following is the one that was actually accepted, and a cached reference that silently resolves to different content is worse than a dangling one — the dangling reference fails loudly. `ENGINEERING_SYNTHESIS`

Adopt this artifact set incrementally, matched to project maturity: a small or exploratory project needs only the artifacts a live decision depends on; add the rest as team size, blast radius, or audit exposure grows. Record a decision when someone outside the work would need to know it; keep a choice that matters only locally in the work's own notes. This is not tidiness: a corpus that models later retrieve from degrades as it grows, so a record set inflated with local choices makes the governing decisions harder to find than no record set at all. A minimal repository, a throwaway prototype, or a project with no stable owner to review these documents is a case where the full set is the wrong fit — name the gap instead of producing unread paperwork.

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

## Gate Contract

Declare these before writing or changing the evaluator, not after a case trips it:

- What the gate must accept
- What it must reject
- What metadata must be present for it to evaluate at all — distinct from reject, and the state to return when it is missing
- The scope it is limited to, and what it deliberately does not judge
- Owner, version, and the evaluation record it emits

The oscillation this prevents: a gate ships with implicit criteria, a real case trips it, someone loosens the evaluator, a different case trips the other way, someone tightens it, and the gate now accepts and rejects with no readable contract. **If the contract did not change but the evaluator did, that is the defect** — either the contract was wrong and should have been amended first, or the evaluator has drifted from it. A property test over the contract catches this; a passing suite over the evaluator does not. `ENGINEERING_SYNTHESIS`

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
