# Agents, Tools, Memory, MCP, A2A, and Multi-Agent Systems

## Contents

- Agent boundary
- Tool contract
- State and memory
- MCP
- A2A
- Multi-agent rules
- Termination and failure

## Agent Boundary

Give every agent a narrow goal, typed input/output, explicit state, bounded tools, budgets, stop conditions, evaluator and accountable owner. Separate domain policy from framework callbacks so the design can survive library changes.

## TOL-01 — Tool Contract

Define for each tool:

- semantic name and one responsibility;
- typed arguments/results and validation, with every argument treated as attacker-influenced and checked again at each sink it reaches — shell, dynamic import or eval, SQL, filesystem path, outbound URL, deserializer — because a schema type is not a taint check;
- read versus write behavior;
- identity, authorization and resource scope;
- timeout, rate limit and cost;
- idempotency key or compensation;
- error taxonomy and retry eligibility;
- dry-run/preview and human approval policy;
- audit event and content-redaction rules.

Split consequential operations into propose/preview, authorize, execute, and independently verify phases. Return status, changed resources, evidence, partial-success state, and retryability. Never expose a broad shell, database or filesystem merely because a narrower tool is inconvenient.

## MEM-01 — State and Memory

| Kind | Purpose | Typical lifetime |
|---|---|---|
| Working state | Current plan, results and pending decisions | One execution/thread |
| Conversational | Recent interaction needed for coherence | Session/window |
| Episodic | Prior cases or outcomes | Retained with policy |
| Semantic | Domain facts and documents | Versioned knowledge base |
| Preference | User-approved durable settings | Until changed/deleted |

Store raw state rather than prompt-formatted prose. For every durable write classify owner, scope, sensitivity, expiry, confidence, source, version, and access policy; deduplicate or supersede old records and support correction/deletion. Use explicit retention tiers where scale warrants it: hot working state, warm session/project state, and cold durable knowledge/archive. Define promotion, consolidation, decay, eviction, and restore rules; “old” is not equivalent to “unimportant.” Retrieval from memory is a retrieval subsystem and must be evaluated for both relevance and authorization.

A vector database is one retrieval layer, not complete memory. Choose stores by purpose: thread/working state, episodic and temporal records, semantic knowledge, relationships, and preferences. Combine vector, graph, relational, event-log, or archival storage only when requirements justify each layer. In LangGraph, treat a checkpointer as thread-scoped execution state and use Store or an application-owned service for cross-thread memory; define retention, cleanup, migration, tenancy, and deletion.

## TOL-02 — MCP and A2A Protocol Boundaries

### MCP

Use MCP for standardized capability and context exposure, not as a substitute for security design. Separate client, server, resource, prompt and tool concerns. For remote HTTP servers, apply current authorization guidance, validate token audience, prohibit token passthrough, scope consent, isolate tenants, rate-limit calls and audit every external effect. For third-party servers, verify publisher, permissions, updates, dependency integrity and data destinations.

### A2A

Use A2A-style boundaries for independently owned agents that must discover capabilities and exchange tasks/artifacts without sharing internal state or tools. Define agent identity, capability metadata, task lifecycle, message/artifact schemas, streaming/cancellation, authentication, timeout, replay protection and cross-agent error semantics.

Use MCP primarily for agent-to-capability/context access and A2A for agent-to-agent delegation. Do not blur the trust boundaries.

## Multi-Agent Rules

Split only when at least one is true:

- contexts conflict or exceed useful size;
- tool permissions differ;
- teams/services own separate boundaries;
- independent verification adds evidence;
- tasks parallelize with a defined merge;
- specialized models materially improve quality/cost.

Define coordinator, task contract, shared-state ownership, conflict/arbitration rule, stop condition and per-agent budget. Measure the multi-agent design against a single-agent baseline.

Make that baseline equal-compute or equal-thinking-token where feasible. Sequential tasks and high tool counts are risk cases. Import research percentages only with the paper version, benchmark, topology, budget, model mix, uncertainty, and exact claim; never use them as universal defaults.

## Termination and Failure

Use explicit terminal states: success, insufficient evidence, rejected by policy, human escalation, dependency failure, or budget exhausted. Bound repeated planning/reflection. Make external effects idempotent; distinguish transient, model-recoverable, user-fixable and fatal errors. Persist state before interrupts and resume from checkpoints rather than replaying successful effects.

## Source Depth

Add deeper book or organization-specific variants only through [source-extension.md](source-extension.md); keep this module as the framework-independent runtime contract.
