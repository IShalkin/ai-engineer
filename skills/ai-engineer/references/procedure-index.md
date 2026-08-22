# Procedure Index

Use these stable IDs in plans, implementation notes, evaluations, and incident records. Each ID has one canonical home; source-book links are evidence, not duplicate procedures.

Required output is routing shorthand; where the module body also states it, the body wins. A missing Gates or Failure Signals section is not a claim that no gates apply.

| ID | Trigger | Canonical file | Required output |
|---|---|---|---|
| ARC-01 | New AI request or ambiguous requirement | architecture-decision-engine.md | 8 frame dimensions answered, baseline, smallest resolving experiment |
| ARC-02 | Choose system shape/topology | architecture-decision-engine.md | level chosen, adjacent levels rejected, evidence, reconsider trigger |
| ARC-03 | More than one agent/worker participates, or the design uses voting, arbitration, specialist roles, or correlated evidence | architecture-decision-engine.md | topology plus per-participant owner, authority, lineage, correlation |
| ARC-04 | Choose implementation framework | framework-selection.md | matrix scored on all 10 criteria, owner, lock-in escape path |
| ARC-05 | Route requests to a capability/model tier | architecture-decision-engine.md | route classes, labelled difficulty, tier rule, escalation triggers |
| ALG-01 | Decide whether AI/LLM is the right computational method | foundation-models-algorithms.md | 7 formalization items answered, non-LLM baseline, LLM justification |
| ALG-02 | Select search/planning/CSP/probabilistic/ML/RL method | foundation-models-algorithms.md | method, matched assumptions, evaluation criteria, assumption test |
| MLD-01 | Design or materially change a predictive/ML system | ml-system-design-lifecycle.md | document covering all 10 steps, 5 gates each passed |
| MLD-02 | Review an ML/AI design artifact or production readiness | ml-system-design-lifecycle.md | stage, evidence map, 10 graded dimensions, at least one attack question answered per graded dimension, ranked findings, fix plan |
| REV-01 | Check full request and boundary coverage | completeness-provenance.md | every requirement cell covered/NA/unknown/missing, severity, owner, findings first, each finding typed, each element traced to a driver |
| SRC-01 | Use a named source/case, make material factual claims, or depend on current/provider-specific behavior, APIs, cache/context economics, pricing, standards, or security guidance | completeness-provenance.md | `source_auto_load_status`; if loaded, identity plus claim label, locator, impact |
| ASM-01 | Claim a guarantee, independence, safety, or completeness | completeness-provenance.md | property, each assumption satisfied/violated/unknown, non-guarantees, monitor, residual risk, confidence and reachable basis surfaced to the recipient |
| PRM-01 | Build a reliable prompt interface | context-prompt-engineering.md | typed schemas, authority layer, abstention rule, versioned bundle, frozen tests |
| PRM-02 | Diagnose prompt failure | context-prompt-engineering.md | defect assigned to one of 6 categories, one layer changed, cases rerun |
| PRM-03 | Select a reasoning/decomposition strategy | context-prompt-engineering.md | mechanism chosen, bounds on candidates/depth/calls, named external verifier |
| CTX-01 | Assemble context for a model step | context-prompt-engineering.md | 5 layers in order, manifest rows for source, owner, trust, freshness, purpose |
| CTX-02 | Context exceeds useful budget | context-prompt-engineering.md | every item P0-P3, handoff packet, preservation ledger, budget, recovery test |
| CTX-03 | Many skills/tools/knowledge sources exist | context-prompt-engineering.md | registry rows per skill, activation and false-activation tests |
| HRN-01 | Convert an agent prototype into a controlled runtime | agent-harness-loop.md | contract covering all 8 steps, 5 gates, all 5 control axes answered separately |
| HRN-02 | Implement or review any loop/workflow that pauses, resumes, waits for approval, interrupts, cancels, or restarts | agent-harness-loop.md | states and transitions, all 8 terminal outcomes, a forward path per terminal state, loop escalation |
| HRN-03 | Add multi-agent collaboration | agent-harness-loop.md | justification per agent, data plane, control plane, one-agent comparison |
| DST-01 | Agents/workers vote, arbitrate, or may fail together | distributed-agent-systems.md | fault matrix, membership, decision rule, independence evidence, adversarial tests |
| DST-02 | Durable causal state, replay, or selective invalidation is required | distributed-agent-systems.md | event schema, consistency boundary, checkpoint plan, invalidation rule, replay test |
| DST-03 | Concurrent workers retry effects or recover partial work | distributed-agent-systems.md | ownership, lease/fence, idempotency contract, compensation table, reconciliation |
| TOL-01 | Expose an external capability | agents-tools-protocols.md | all 9 contract fields, phase split, result status/changes/evidence/retryability |
| TOL-02 | Use MCP or A2A | agents-tools-protocols.md | protocol justified, identity/authz/consent/tenancy, pinned definitions, effect audit |
| MEM-01 | Store or retrieve durable memory | agents-tools-protocols.md | store per kind; per write owner, scope, sensitivity, expiry, version, access policy, deletion |
| COD-01 | Agent changes a code repository | coding-agent-engineering.md | 8 steps executed, files/evidence/risk/rollback reported, 5 gates |
| COD-02 | Approve or release generated code | coding-agent-engineering.md | 3 mechanical checks, 5 semantic checks, 4 additional requirements, diff inspected |
| RAG-01 | Ingest a knowledge corpus | data-rag-search.md | versioned identity, parser, chunking, metadata, embedding, index; replay |
| RAG-02 | Retrieve evidence for an answer/action | data-rag-search.md | packet with query, filters, versions, ranked IDs, excerpts, provenance, authz |
| RAG-03 | Choose hybrid, graph, multimodal, or agentic RAG | data-rag-search.md | measured failure justifying the layer, ontology/modality provenance |
| SEA-01 | Design or tune OpenSearch | data-rag-search.md | versioned mappings, filter/query split, shard rationale, measured relevance |
| MOD-01 | Choose prompt, retrieval, tools, fine-tuning, or training | model-adaptation-training.md | causal gap located, layer chosen, cheaper layers rejected, frozen-eval evidence |
| MOD-02 | Build training/preference data | model-adaptation-training.md | behavior, population, rubric, rights, provenance, leakage-aware split, versioning |
| MOD-03 | Apply SFT, PEFT, or LoRA | model-adaptation-training.md | baselines, chosen adaptation, experiment-tuned settings, reversible canary |
| MOD-04 | Apply DPO, RLHF, RLVR, or tool-use RL | model-adaptation-training.md | constraints outside reward, disagreement measured, leakage and hacking tests |
| EVA-01 | Create an evaluation set | evaluation-testing.md | versioned normal/edge/adversarial/policy cases, dev/release split |
| EVA-02 | Evaluate an agent trajectory | evaluation-testing.md | 3 separate scores per case plus latency, cost, variance, trace completeness |
| EVA-03 | Use an LLM judge or issue a scored completeness/readiness verdict | evaluation-testing.md | findings, coverage, scores, verdict, additions in that order; 4 fields per addition |
| JDG-01 | A judge score gates a release, ranks two systems, or is reported as quality evidence | judge-bias-and-calibration.md | judge card: model/version, prompt hash, scale, attribute, order-swap policy, K, order-disagreement rate, agreement statistic, unmitigated biases |
| JDG-02 | Author or edit the rubric criteria text a judge scores against | judge-bias-and-calibration.md | versioned rubric: one affirmative predicate per criterion, count formulae, no-deduction clauses, scale anchors |
| JDG-03 | Before any judge output is trusted, and after every rubric or judge-prompt edit | judge-bias-and-calibration.md | minimal-pair results per criterion, agreement statistic with n, mitigations, blind spots |
| JDG-04 | Create an evaluation set or state a numeric release threshold on top of one | judge-bias-and-calibration.md | per failure class metric, threshold, n, SE/CI, blocking status, owner, set hash |
| SEC-01 | Threat-model an AI system | security-governance.md | actors, assets, boundaries, flows, abuse cases incl. injection, controls, and the catalogues checked with edition and check date |
| SEC-02 | Permit an external effect | security-governance.md | pre-effect binding of actor, tenant, resource, operation, policy, approval, key, expiry |
| SEC-03 | Conduct or reconstruct authorized offensive testing, passive/active boundaries, or security-testing limits | security-governance.md | signed scope with stop conditions, passive-first plan, stop record, ASM-01 audit |
| FIN-01 | AI participates in fraud, AML/sanctions screening, or credit-adjacent decisioning | financial-crime-model-risk.md | model-or-not determination with reasoning, full inventory entry |
| FIN-02 | Validation cannot precede use, or a deficiency is unfixable within the framework (the three elements themselves are FRD-01) | financial-crime-model-risk.md | the deficiency stated, rejection or the compensating controls in force, who was told, who accepted the residual risk |
| FIN-03 | Set or change a detection threshold or filtering criterion | financial-crime-model-risk.md | prior/new value, detection impact, both-side samples, approver, rollback value |
| FIN-04 | Choose metrics or labels for a rare-event decision system | financial-crime-model-risk.md | base-rate-valid metrics, cost-weighted point with owner, versioned labels |
| FIN-05 | Release or monitor a model facing an adapting adversary | financial-crime-model-risk.md | outcome-alerting drift monitors, probing controls, pre-approved fast path |
| FIN-06 | An automated decision produces an adverse action about a person | financial-crime-model-risk.md | reasons bound to version and scored features, both disclosures, cohort tests |
| FIN-07 | An agent could take an adverse action against a person autonomously | financial-crime-model-risk.md | all 4 of evidence, reviewability, reasons, appeal; else a human decides |
| FRD-01 | A model, prompt, or agent emits a decision-bearing score under formal model risk management | fraud-model-risk-guardrails.md | risk-tiered inventory entry, 3 validation elements, validator independence |
| FRD-02 | Design or tune a fraud, AML, or other rare-event detection system | fraud-model-risk-guardrails.md | cost-weighted point, capacity metrics, versioned labels, both-side samples |
| FRD-03 | An automated or agentic decision goes against a person | fraud-model-risk-guardrails.md | specific reason bound to the scored path, evidence, reviewer, appeal, cohort tests |
| FRD-04 | An agent acts rather than scores in a fraud or financial-crime path | fraud-model-risk-guardrails.md | authority map, 4 budget scopes, irreversible gate, idempotency plus compensation |
| REG-01 | Work falls inside a regulated regime for life sciences, healthcare, payments, or financial reporting | regulated-domain-controls.md | per regime: applies or not with reasoning, obligation, control, named owner |
| REG-02 | An action, record, or decision must be evidenced for inspection or audit | regulated-domain-controls.md | event schema incl. model-actor fields, retention per class, export shown, reporting clocks with start conditions |
| REG-03 | Validate or change a regulated system, including a provider or model version change | regulated-domain-controls.md | intended use, risk assessment, frozen set passing run, trigger table, change record |
| REG-04 | Regulated or personal data enters a prompt, trace, index, or memory store | regulated-domain-controls.md | field classification and flow map, scope-exclusion argument, retention per class |
| REG-05 | Model output becomes an official record, signed record, or reporting input | regulated-domain-controls.md | official-output register, approval state machine, reviewer packet, decision schema |
| OPS-01 | Make execution durable | production-operations.md | typed state at boundaries, idempotency or compensation per effect, resume tests |
| OPS-02 | Release a version | production-operations.md | versioned artifacts, external secrets, canary promotion, rollback versions |
| OPS-03 | Observe production | production-operations.md | all 6 trace groups, SLO set with thresholds, outcome alerts, sampling rule |
| OPS-04 | Require sovereign/local/offline deployment | production-operations.md | 7 sovereignty requirements made testable, on-hardware benchmark, egress test |
| RUN-01 | An agent will run on a vendor-managed serverless agent runtime | managed-agent-runtimes.md | dated constraint sheet citing a source per limit, externalized state, 4 gates |
| RUN-02 | Place durable state, memory, or identity on managed runtime services | managed-agent-runtimes.md | state-placement table, caller-to-effect identity map, retention decision |
| RUN-03 | Operate, observe, or cost a managed-runtime agent | managed-agent-runtimes.md | correlated agent spans, audit/debug split, quota-sized design, cost drivers |
| EVL-01 | Repeated failures appear in trajectories | continuous-improvement.md | cluster with evidence, earliest failing layer, counterexample, scope, owner |
| EVL-02 | Improve official agent behavior | continuous-improvement.md | medium matched to cause, smallest reversible change, activation test, rollback |
| DBG-01 | System fails or underperforms | debugging-playbooks.md | check that failed on the symptom first, candidate causes, regression case |
| ART-01 | Formal engineering artifact is required | engineering-artifacts.md | template named, every one of its sections filled or marked NA, named owner |
| COV-01 | Exact source/technique lookup or source-pack extension is requested | source-extension.md | author/title, version, artifact SHA-256, locator, fidelity class, load status |

Do not copy entire book summaries into task context.

After changing routing or descriptions, walk the cases in [routing-checklist.md](routing-checklist.md).
