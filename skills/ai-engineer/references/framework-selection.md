# ARC-04 — Framework Selection

## Decision Matrix

| Need | Default candidate | Why | Avoid when |
|---|---|---|---|
| Simple model/tool application | Provider SDK plus ordinary code | Minimum abstraction and easiest debugging | State graphs or many integrations dominate |
| Composable model/retriever/tool components | LangChain | Broad integrations and standard components | Abstractions obscure a small application |
| Explicit state, branching, checkpointing, interrupts | LangGraph | Durable graph execution and human-in-loop | A linear deterministic pipeline is enough |
| Retrieval/NLP pipeline with typed components | Haystack | Strong pipeline/component model | Team is standardized on another runtime |
| Role-oriented collaborative agents | CrewAI | Fast role/team prototyping | Fine-grained control and durability dominate |
| Conversational multi-agent experiments | AutoGen | Flexible agent conversation patterns | Production control and predictable state are primary |
| Search plus lexical/vector analytics | OpenSearch | Hybrid retrieval, scale and operations | A lightweight local/vector store is sufficient |
| Relationship-centric retrieval | Neo4j/graph store plus vector retrieval | Explicit paths and graph queries | Relations are incidental |

## Selection Criteria

Score candidates on:

1. required control-flow visibility;
2. state persistence and migration;
3. tool/schema model;
4. human interruption and resume;
5. tracing and evaluation integration;
6. deployment and scaling model;
7. security and tenancy boundaries;
8. framework lock-in and portability;
9. team experience and operational ownership;
10. version stability and ecosystem fit.

Choose the smallest abstraction that keeps critical state, permissions and failure behavior visible. Keep domain logic, tool schemas, evaluation cases and policies outside framework-specific code.

Record the scored matrix, dependency/version assumptions, operating owner, lock-in escape path, and a thin compatibility spike. A framework is selected only after the system shape is known.

## Migration Guardrails

- In LangChain v1 code, evaluate `langchain.agents.create_agent` first and use official middleware for supported customization. Keep `langgraph.prebuilt.create_react_agent` only for a pinned legacy dependency and a tested migration boundary.
- Treat middleware as application orchestration, not as an authorization, sandbox, or network-egress security boundary.
- Wrap provider models behind a narrow application interface.
- Keep state in typed application schemas, not framework message objects alone.
- Keep tools as ordinary tested functions/services with adapters.
- Export traces and metrics to vendor-neutral telemetry when possible.
- Pin dependencies and maintain one compatibility test for each external integration.

Load [current-corrections-2026.md](current-corrections-2026.md) and verify current official migration documentation before emitting framework-specific code.
