# Procedure Index

Use these stable IDs in plans, implementation notes, evaluations, and incident records. Each ID has one canonical home; source-book links are evidence, not duplicate procedures.

| ID | Trigger | Canonical file | Required output |
|---|---|---|---|
| ARC-01 | New AI request or ambiguous requirement | architecture-decision-engine.md | requirement frame |
| ARC-02 | Choose system shape/topology | architecture-decision-engine.md | decision with rejected alternatives |
| ARC-03 | More than one agent/worker participates, or the design uses voting, arbitration, specialist roles, or correlated evidence | architecture-decision-engine.md | topology, ownership, dependency, and independence map |
| ARC-04 | Choose implementation framework | framework-selection.md | scored framework decision |
| ARC-05 | Route requests to a capability/model tier | architecture-decision-engine.md | calibrated route and escalation policy |
| ALG-01 | Decide whether AI/LLM is the right computational method | foundation-models-algorithms.md | formal problem class and baseline |
| ALG-02 | Select search/planning/CSP/probabilistic/ML/RL method | foundation-models-algorithms.md | algorithm and evaluation criteria |
| MLD-01 | Design or materially change a predictive/ML system | ml-system-design-lifecycle.md | living ML system design document with evidence gates |
| MLD-02 | Review an ML/AI design artifact or production readiness | ml-system-design-lifecycle.md | evidence-mapped, stage-aware scorecard and fix plan |
| REV-01 | Check full request and boundary coverage | completeness-provenance.md | requirements-to-evidence matrix and independent verdict |
| SRC-01 | Use a named source/case, make material factual claims, or depend on current/provider-specific behavior, APIs, cache/context economics, pricing, standards, or security guidance | completeness-provenance.md | provenance-labelled claim ledger with locators and explicit verification gaps |
| ASM-01 | Claim a guarantee, independence, safety, or completeness | completeness-provenance.md | guarantee-assumption audit and residual risk |
| PRM-01 | Build a reliable prompt interface | context-prompt-engineering.md | versioned prompt contract |
| PRM-02 | Diagnose prompt failure | context-prompt-engineering.md | failure category and smallest change |
| PRM-03 | Select a reasoning/decomposition strategy | context-prompt-engineering.md | bounded reasoning interface and verifier |
| CTX-01 | Assemble context for a model step | context-prompt-engineering.md | ordered context manifest |
| CTX-02 | Context exceeds useful budget | context-prompt-engineering.md | preservation ledger and compact state |
| CTX-03 | Many skills/tools/knowledge sources exist | context-prompt-engineering.md | progressive-discovery registry and activation tests |
| HRN-01 | Convert an agent prototype into a controlled runtime | agent-harness-loop.md | harness contract |
| HRN-02 | Implement or review any loop/workflow that pauses, resumes, waits for approval, interrupts, cancels, or restarts | agent-harness-loop.md | explicit state machine, terminal/cancellation states, checkpoint and recovery contract |
| HRN-03 | Add multi-agent collaboration | agent-harness-loop.md | context topology, data plane, control plane |
| DST-01 | Agents/workers vote, arbitrate, or may fail together | distributed-agent-systems.md | fault/membership/decision model and adversarial tests |
| DST-02 | Durable causal state, replay, or selective invalidation is required | distributed-agent-systems.md | event schema, log/checkpoint, and replay design |
| DST-03 | Concurrent workers retry effects or recover partial work | distributed-agent-systems.md | fencing/idempotency/compensation and reconciliation design |
| TOL-01 | Expose an external capability | agents-tools-protocols.md | typed, bounded tool specification |
| TOL-02 | Use MCP or A2A | agents-tools-protocols.md | protocol and trust-boundary design |
| MEM-01 | Store or retrieve durable memory | agents-tools-protocols.md | memory lifecycle and access policy |
| COD-01 | Agent changes a code repository | coding-agent-engineering.md | inspect-patch-verify evidence |
| COD-02 | Approve or release generated code | coding-agent-engineering.md | diff, tests, risks, rollback |
| RAG-01 | Ingest a knowledge corpus | data-rag-search.md | replayable versioned ingestion contract |
| RAG-02 | Retrieve evidence for an answer/action | data-rag-search.md | retrieval trace and evidence packet |
| RAG-03 | Choose hybrid, graph, multimodal, or agentic RAG | data-rag-search.md | measured retrieval architecture |
| SEA-01 | Design or tune OpenSearch | data-rag-search.md | mapping/index/query/operations decision |
| MOD-01 | Choose prompt, retrieval, tools, fine-tuning, or training | model-adaptation-training.md | adaptation decision and cheaper rejected layers |
| MOD-02 | Build training/preference data | model-adaptation-training.md | versioned, accepted dataset with provenance |
| MOD-03 | Apply SFT, PEFT, or LoRA | model-adaptation-training.md | adapter/model candidate and regression evidence |
| MOD-04 | Apply DPO, RLHF, RLVR, or tool-use RL | model-adaptation-training.md | reward/preference contract and safe training gate |
| EVA-01 | Create an evaluation set | evaluation-testing.md | versioned cases and failure taxonomy |
| EVA-02 | Evaluate an agent trajectory | evaluation-testing.md | outcome/process/quality scores with evidence |
| EVA-03 | Use an LLM judge or issue a scored completeness/readiness verdict | evaluation-testing.md | findings-first evaluation record, independent scores, verdict, and provenance-labelled additions |
| JDG-01 | A judge score gates a release, ranks two systems, or is reported as quality evidence | judge-bias-and-calibration.md | judge card with model/prompt versions, order-swap policy, repeat count, agreement statistic, unmitigated biases |
| JDG-02 | Author or edit the rubric criteria text a judge scores against | judge-bias-and-calibration.md | versioned rubric of affirmative predicates with count formulae, no-deduction clauses, and scale anchors |
| JDG-03 | Before any judge output is trusted, and after every rubric or judge-prompt edit | judge-bias-and-calibration.md | judge validation record with minimal-pair results, agreement statistic and n, mitigations, residual blind spots |
| JDG-04 | Create an evaluation set or state a numeric release threshold on top of one | judge-bias-and-calibration.md | gate specification per failure class with metric, threshold, n, SE/CI, blocking status, owner, frozen-set hash |
| SEC-01 | Threat-model an AI system | security-governance.md | assets, boundaries, abuse cases, controls |
| SEC-02 | Permit an external effect | security-governance.md | authenticated, authorized, validated action record |
| SEC-03 | Conduct or reconstruct authorized offensive testing, passive/active boundaries, or security-testing limits | security-governance.md | signed scope, passive-first plan, artifacts, stop record, and ASM-01 non-guarantee audit |
| FIN-01 | AI participates in fraud, AML/sanctions screening, or credit-adjacent decisioning | financial-crime-model-risk.md | model/tool classification and inventory entry |
| FIN-02 | Validate or govern a model under formal model risk management | financial-crime-model-risk.md | three-element validation record with independence evidence |
| FIN-03 | Set or change a detection threshold or filtering criterion | financial-crime-model-risk.md | approved threshold change record with both-side test evidence |
| FIN-04 | Choose metrics or labels for a rare-event decision system | financial-crime-model-risk.md | cost-weighted metric set and label-latency/feedback design |
| FIN-05 | Release or monitor a model facing an adapting adversary | financial-crime-model-risk.md | drift/probing monitors, fast-path change policy, shadow-canary plan |
| FIN-06 | An automated decision produces an adverse action about a person | financial-crime-model-risk.md | attribution-bound reason codes and cohort/disparity test evidence |
| FIN-07 | An agent could take an adverse action against a person autonomously | financial-crime-model-risk.md | evidenced, reviewable, explainable, appealable gate or human decision |
| FRD-01 | A model, prompt, or agent emits a decision-bearing score under formal model risk management | fraud-model-risk-guardrails.md | tiered inventory entry and three-element validation record with independence evidence |
| FRD-02 | Design or tune a fraud, AML, or other rare-event detection system | fraud-model-risk-guardrails.md | cost-weighted operating point, both-side threshold-change record, adversarial-drift monitors |
| FRD-03 | An automated or agentic decision goes against a person | fraud-model-risk-guardrails.md | attribution-bound reason set, evidence record, human reviewability, appeal path, cohort test evidence |
| FRD-04 | An agent acts rather than scores in a fraud or financial-crime path | fraud-model-risk-guardrails.md | typed-tool authority map, budgets, irreversible-action gate, idempotency/compensation and confidentiality partitioning |
| REG-01 | Work falls inside a regulated regime for life sciences, healthcare, payments, or financial reporting | regulated-domain-controls.md | applicability frame naming regime, obligation, control, and named owner |
| REG-02 | An action, record, or decision must be evidenced for inspection or audit | regulated-domain-controls.md | audit-event schema, immutability and retention mechanism, reviewer and cadence, human-readable export |
| REG-03 | Validate or change a regulated system, including a provider or model version change | regulated-domain-controls.md | risk assessment, frozen eval set with thresholds, revalidation-trigger table, per-change control record |
| REG-04 | Regulated or personal data enters a prompt, trace, index, or memory store | regulated-domain-controls.md | field classification and data-flow map, scope-exclusion argument, de-identification residual risk, per-class retention map |
| REG-05 | Model output becomes an official record, signed record, or reporting input | regulated-domain-controls.md | official-output register, approval state machine, reviewer packet, approve/edit/reject schema, approved-source integrity check |
| OPS-01 | Make execution durable | production-operations.md | checkpoint/idempotency/recovery design |
| OPS-02 | Release a version | production-operations.md | gated canary and rollback plan |
| OPS-03 | Observe production | production-operations.md | traces, SLOs, alerts, sampling plan |
| OPS-04 | Require sovereign/local/offline deployment | production-operations.md | threat, residency, capability, and operating design |
| RUN-01 | An agent will run on a vendor-managed serverless agent runtime | managed-agent-runtimes.md | dated constraint sheet with sourced limits, statelessness and resumability gates |
| RUN-02 | Place durable state, memory, or identity on managed runtime services | managed-agent-runtimes.md | state-placement table, caller-to-effect identity map, retention/deletion decision with verification status |
| RUN-03 | Operate, observe, or cost a managed-runtime agent | managed-agent-runtimes.md | span and audit/debug split, quota-sized design, retry classification, version/rollback and cost-driver model |
| EVL-01 | Repeated failures appear in trajectories | continuous-improvement.md | causal failure cluster |
| EVL-02 | Improve official agent behavior | continuous-improvement.md | smallest safe versioned update |
| DBG-01 | System fails or underperforms | debugging-playbooks.md | earliest failing layer and regression case |
| ART-01 | Formal engineering artifact is required | engineering-artifacts.md | selected artifact with decision evidence |
| COV-01 | Exact source/technique lookup or source-pack extension is requested | source-extension.md | source identity, locator, fidelity status, and uncertainty |

## Procedure Application Record

For non-trivial work record:

```text
procedure_ids:
trigger:
inputs:
decisions:
gates_passed:
outputs_or_artifacts:
evidence:
residual_risk:
```

This record is the precise internal reference. Do not copy entire book summaries into task context.

After changing routing or descriptions, run the cases in [routing-tests.md](routing-tests.md).
