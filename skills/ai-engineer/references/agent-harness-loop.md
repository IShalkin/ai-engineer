# Agent Harness and Loop Engineering

## HRN-01 — Harness Contract

**Trigger:** the model chooses actions across more than one observation.

**Inputs:** outcome, environment, authority, tools, state, evidence, budgets, evaluator, operator.

**Steps:**

1. Define typed state and lifecycle transitions.
2. Define context construction, skill/tool discovery, compaction, and provenance.
3. Expose narrow tools; enforce permission and validation outside the model.
4. Separate propose, prepare, execute, and verify phases for effects.
5. Classify errors and assign retry, correction, fallback, escalation, or termination.
6. Persist checkpoints before waits, approvals, and consequential effects.
7. Trace versions, observations, decisions, tools, state changes, cost, latency, and evaluation.
8. Assign a human/product owner and incident path.

**Gates:** no hidden mutable state; no unbounded loop; every effect attributable and recoverable; outcome externally checkable.

## HRN-02 — Bounded Agent State Machine

Use explicit states such as `ASSESS -> PLAN -> PREPARE -> AUTHORIZE -> ACT -> OBSERVE -> VERIFY -> COMPLETE|ESCALATE|FAIL`. Persist state transitions and artifacts. Re-observe the environment after action; do not infer success from a tool's optimistic prose.

Terminal states must distinguish success, insufficient evidence, policy denial, user input required, dependency failure, and budget exhaustion. Repeated identical action/state pairs trigger diagnosis or escalation.

## HRN-03 — Multi-Agent Context and Topology

Add agents only for isolation, parallelism, specialization, separate authority, independent verification, or failure containment. Choose independently:

- shared trajectory vs isolated contexts with explicit handoffs;
- peer, orchestrator-worker, hierarchy, or decentralized control transfer.

Define a **data plane** of private workspaces, bounded shared artifacts, external resources, and stable references. Define a **control plane** for assignment, messaging, status, cancellation, termination, scheduling, and ownership. Large results move by artifact reference; handoffs carry conclusion, evidence, validation, uncertainty, and next action.

Compare task success, cost, latency, duplication, and failure containment against one agent.

## Failure Signals

Autonomy for known deterministic steps, state only in chat, retry without classification, supervisor approval without independent evidence, persona-only agents, shared-context explosion, circular delegation, no cancellation, and no durable artifact ownership.

## Source Depth

Use sibling skills `li-ai-agents-in-depth`, `huang-designing-ai-agents`, `lanham-ai-agents-action-2e`, `albada-multiagent-systems`, `gfeller-crewai-mcp`, `koenigstein-ai-agents`, and `omahony-nonnenmacher-agent-platforms` for variants and examples.
