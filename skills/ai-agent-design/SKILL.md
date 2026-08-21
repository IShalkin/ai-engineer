---
name: ai-agent-design
description: Design or review an agent's runtime shape — LangGraph/StateGraph topology, node boundaries, tool specifications, memory layout, HITL and approval pauses, resume and cancellation, retry policy, loop termination, and deployment to a managed agent runtime. Use before writing a graph, and when a loop needs a terminal state or an interrupt has to survive a restart. Runs in its own context.
context: fork
agent: ai-engineer
background: false
effort: high
---

Load by what the task actually is, not all of them:

- [agent-harness-loop.md](../ai-engineer/references/agent-harness-loop.md) — HRN-01/02/03: harness
  contract, and **HRN-02 for anything that pauses, resumes, waits for approval, interrupts, cancels
  or restarts**
- [agents-tools-protocols.md](../ai-engineer/references/agents-tools-protocols.md) — TOL-01/02,
  MEM-01: typed tool specs, MCP/A2A trust boundaries, memory lifecycle
- [architecture-decision-engine.md](../ai-engineer/references/architecture-decision-engine.md) —
  ARC-01…05, and **ARC-03 whenever more than one agent, worker, vote or specialist role
  participates**
- [managed-agent-runtimes.md](../ai-engineer/references/managed-agent-runtimes.md) — RUN-01/02/03,
  only when deploying to a vendor-managed serverless runtime
- [framework-selection.md](../ai-engineer/references/framework-selection.md) — ARC-04, only when the
  framework is genuinely still open

## Climb the system-shape ladder before drawing a graph

Deterministic function → one structured model call → deterministic pipeline with bounded model calls
→ RAG/search → explicit workflow → one observing agent → several agents → distributed protocol. Take
the first rung that holds and say which rungs you rejected. A graph whose nodes are all deterministic
except one is a pipeline in a different coat — a coat that buys checkpoint boundaries and per-node
retry policy, which is a real reason, but say that is the reason.

## The edge that is almost always wrong

**An edge from a findings-returning gate back to the generator.** An agent handed its own failure
report learns to rewrite until it passes, which is the failure mode a gate exists to prevent. The
anti-pattern is a property of the edge, not of the framework. If a revision loop is genuinely
required, it needs an iteration cap stated as a number — `recursion_limit` defaults to 1000 in
LangGraph, not 25, so "the framework will stop it" is not a cap.

## State, checkpoints and undeclared keys

Every key a node returns must be **declared in the state schema**. An undeclared key is silently
discarded — no exception, no warning — so an audit trail returned but not declared works in the test
and vanishes in the graph. Anything a caller must see after the run is part of the schema, not a
convenience field.

Give every loop: a budget, terminal states, retry classes by failure type, an escalation path, and a
checkpoint that survives a crash. `RetryPolicy(max_attempts=1)` on a verification node is how you
enforce *retry the work, never retry the check* in configuration rather than in prose.

## What to return

The shape, the rejected rungs, the node boundaries with what each owns, the state schema, the
terminal and cancellation states, where effects are idempotent or compensatable, and the smallest
viable slice. Name what is deferred rather than building it.
