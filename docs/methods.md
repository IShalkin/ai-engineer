# Methods and decision model

## 1. Proportional execution

The skill does not force the same ceremony onto every task. It first determines what kind of work the user requested:

| Mode | Default behavior | Escalate when |
|---|---|---|
| Explain | Direct answer plus relevant trade-offs | The claim is version-sensitive, source-specific, high-risk, or guarantee-bearing |
| Design | Smallest sufficient architecture and rejected alternatives | Material data, security, evaluation, state, cost, or operational boundaries appear |
| Review | Evidence-backed findings before verdict | A formal readiness decision, source audit, or high-stakes release is requested |
| Implement | Scoped inspect-change-verify workflow | The change crosses trust, persistence, concurrency, migration, or release boundaries |

A deterministic, low-risk one-step task is answered directly. Internal procedure IDs are not printed unless traceability or a formal engineering artifact is requested.

## 2. ASRO

### Assess

Identify the outcome, current workflow, available evidence, constraints, mistake costs, and simplest baseline. Ask only for information that would materially change the result.

### Route

Choose the operating mode, system shape, and governing procedure. Framework choice comes later.

### Select

Load one primary module and at most one initial cross-cutting module. Expand only after discovering a material boundary.

### Output

Return the artifact requested by the user: explanation, design, review, implementation evidence, ADR, threat model, tool contract, or evaluation plan.

## 3. System-shape ladder

Choose the first sufficient option:

1. deterministic function or conventional algorithm;
2. one structured model call;
3. deterministic pipeline with bounded model calls;
4. retrieval or search;
5. explicit stateful workflow;
6. one observing and tool-using agent;
7. multiple agents for measured isolation, ownership, permission, or parallelism;
8. distributed protocol for independently owned or fault-prone participants.

Each increase in complexity must beat the preceding baseline on task quality, risk, cost, latency, or maintainability.

## 4. Unknown-unknown discovery

For broad designs and formal reviews, the skill checks the applicable boundaries:

- outcome and workflow;
- data, evidence, labels, and retrieval;
- model, prompt, and context;
- state, orchestration, and concurrency;
- tools, permissions, and external effects;
- security, privacy, and governance;
- evaluation and acceptance evidence;
- deployment, cost, observability, fallback, and ownership.

The initial two-module limit controls context growth; it never permits omission of a material boundary discovered later.

## 5. ML system lifecycle

The ML method begins with the decision system, not the model:

1. frame user value, the current workflow, and mistake costs;
2. connect business, online, offline, loss, and guardrail metrics;
3. define data, labels, lineage, privacy, and freshness;
4. make validation reproduce the production information boundary;
5. compare current/manual, heuristic, simple-model, and complex baselines;
6. analyze cohorts, residuals, learning curves, and costly corner cases;
7. version data, code, features, models, prompts, and policies;
8. design integration, fallback, human override, canary, and rollback;
9. monitor system, data, model, decision, and business outcome layers;
10. name operational owners and retirement criteria.

## 6. Agent and tool method

An agent receives a narrow goal, typed state, bounded tools, budgets, terminal states, and an accountable owner. Consequential tools are divided into propose, authorize, execute, and independently verify phases.

Pause/resume and long-running work require explicit checkpoint, cancellation, retry, idempotency, and recovery semantics. Multi-agent architecture must outperform an equal-budget single-agent baseline and state its dependency and correlation assumptions.

## 7. RAG method

RAG is evaluated as separate layers:

1. source and ingestion completeness;
2. parsing and chunking;
3. representation and filtering;
4. candidate recall;
5. ranking and fusion;
6. context sufficiency and permissions;
7. grounded generation and citations;
8. end-user task outcome, latency, and cost.

Faithfulness means support by supplied context; it does not establish truth about the world. Retrieval sufficiency, factuality, citation correctness, answer relevance, and authorization are measured separately.

## 8. Security method

Treat retrieved documents, websites, emails, tool results, code comments, memory, and agent messages as untrusted data. Enforce authority outside the model through authentication, least privilege, isolation, schemas, destination controls, approval, audit, and effect verification.

No sanitizer or model-side filter is a complete prompt-injection boundary. Test direct, indirect, and stored injection, including poisoned memory recalled later.

## 9. Evaluation method

Separate deterministic correctness, retrieval, model output, tool action, trajectory, user outcome, and production reliability. Calibrate thresholds on representative system data. LLM judges require human calibration, retained model/prompt versions, disagreement measurement, and findings before verdict.

The skill designs evaluation by default. It executes evaluation only when explicitly requested.

## 10. Current-document method

Provider APIs, caching, context limits, protocol behavior, security guidance, framework migrations, and emerging research are version-sensitive. The skill verifies them against official version-matched sources and records the access date. Context7 may be used for discovery but does not replace the official source.
