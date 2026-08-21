# Architecture Decision Engine

## Contents

- Requirement frame
- Complexity ladder
- Agent design canvas
- Topology rules
- Architecture review

## ARC-01 — Requirement Frame

Capture these before selecting a framework:

| Dimension | Questions |
|---|---|
| Outcome | What user/business decision or task changes? What is the current non-AI workflow and acceptance test? |
| Inputs | Which data is authoritative, private, time-sensitive, structured, or multimodal? |
| Output | Is the contract free text, JSON, a decision, a plan, or an external side effect? |
| Uncertainty | Which step requires semantic judgment rather than deterministic logic? |
| Risk | What can leak, be corrupted, cost money, or become irreversible? |
| Mistakes | What are false-positive, false-negative, abstention, delay, and second-order costs? Who absorbs them? |
| Scale | Requests/sec, corpus size, concurrency, latency and regional constraints? |
| Ownership | Who approves, operates, audits, and handles failure? |

Also record evidence source, prior internal/external attempts, build-versus-buy options, unknowns, irreversible decisions, and the smallest experiment that resolves the most important uncertainty. Define a current-workflow, constant/rule, or simple-model baseline. Complexity is justified only if the candidate improves an agreed metric enough to pay for its operating burden.

## ARC-02 — Complexity Ladder

1. **Deterministic function** - stable transformation, validation, calculation, routing.
2. **Single model call** - one bounded semantic task with structured output.
3. **Pipeline** - known sequence; models are isolated components.
4. **RAG** - generation requires attributable external evidence.
5. **Workflow graph** - branches, retries, checkpoints, approvals, or resumability matter.
6. **Single agent** - the model must choose the next bounded action.
7. **Multi-agent** - roles need materially different context, tools, permissions, or independent judgment.
8. **Distributed agent protocol** - independently owned agents need discovery and task exchange.

Move one level at a time. If a lower level fails, identify the failure category before escalating.

**Output:** selected level, rejected adjacent levels, evidence that the selected level is necessary, and conditions that would trigger reconsideration.

## ARC-03 — Agent Design Canvas and Topology

**Trigger invariant:** invoke ARC-03 whenever more than one agent or worker contributes to a decision, including voting, quorum, arbitration, parallel specialists, reviewers, or agents sharing a model/retriever/evidence lineage. Do not treat DST-01 or HRN-03 as a substitute: ARC-03 owns roles, topology, authority, and dependency/independence mapping.

Define:

- user outcome and non-goals;
- environment and authoritative observations;
- state schema and checkpoint boundaries;
- allowed actions and typed tools;
- policy: routing, thresholds, permissions, budgets;
- knowledge and memory by purpose;
- evaluator and acceptance thresholds;
- success, stop, escalation and fallback;
- human authority and override;
- telemetry, retention and incident owner.

For every participant record owner, authority, input/evidence lineage, model/prompt/retriever/tool dependencies, writable state, output consumer, and failure correlation. Names or personas are not evidence of independence.

### Topology rules

- Use a **router** when classes are known and routes have distinct handlers.
- Use a **planner-executor** when decomposition is useful but execution can be bounded and checked.
- Use **reflection/critic** only when the critic has a different rubric or evidence; self-review without new signal often adds cost, not accuracy.
- Use a **specialist team** when contexts or tools conflict; do not create persona theater.
- Use a **verifier** when an independent evidence path exists.
- Use **map-reduce** for decomposable corpora; define aggregation and conflict resolution.
- Use **event-driven orchestration** for long-running or external work; persist state and make consumers idempotent.

## Architecture Review

Reject or revise a design when:

- an agent selects steps that are already known;
- multiple agents share identical context, tools and success criteria;
- state lives only inside prompt text;
- retrieval and generation cannot be evaluated separately;
- tool permissions exceed the task;
- a retry can repeat a side effect;
- there is no hard budget or terminal state;
- production telemetry records only final text;
- fallback means silently returning an ungrounded answer.

## ARC-05 — Complexity-Based Capability Routing

**Trigger:** workloads vary enough that one model/tier wastes cost or misses quality.

1. Define route classes from observable task features and required capability—not from provider branding.
2. Build a strong-model baseline and label route difficulty from actual success evidence.
3. Start with deterministic rules or a cheap calibrated classifier/router.
4. Route to the cheapest tier that meets quality, safety, latency, modality, context, and tool requirements.
5. Add escalation on low confidence, validator failure, repeated tool errors, or high-risk actions.
6. Measure route accuracy, false down-routing, cost per success, latency, and distribution drift.

Bias toward stronger handling for consequential ambiguity, but do not systematically over-route every request. Keep permissions independent of model tier.

Use [MLD-01](ml-system-design-lifecycle.md) for the complete problem-to-ownership ML lifecycle.
