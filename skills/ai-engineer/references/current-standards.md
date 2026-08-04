# Current Standards and Version-Sensitive Guidance

Verified against primary sources on **2026-08-04**. Recheck when exact behavior matters and record the accessed version/date in architecture or security artifacts.

Use the maintenance loop in [completeness-provenance.md](completeness-provenance.md): optional Context7 discovery, mandatory version-matched official verification, then automatic canonical-link addition/replacement when the active skill is writable and the change is in scope. Context7 setup and client guidance: [official Context7 MCP clients](https://context7.com/docs/resources/all-clients); do not store its API key in this skill.

## Agent Runtime

- [LangChain v1 migration guide](https://docs.langchain.com/oss/python/migrate/langchain-v1) - for new v1 agents prefer `langchain.agents.create_agent`; treat `langgraph.prebuilt.create_react_agent` as a pinned legacy route unless current official guidance says otherwise.
- [LangChain middleware](https://docs.langchain.com/oss/python/langchain/middleware) - standard v1 extension point for agent behavior; it does not replace authorization, isolation, sandboxing, or egress controls.
- [LangGraph overview](https://docs.langchain.com/oss/python/langgraph/overview) - durable execution, streaming, human-in-loop and persistence.
- [LangGraph persistence](https://docs.langchain.com/oss/python/langgraph/persistence) - checkpoints, threads, memory, time travel and fault tolerance.
- [LangChain human-in-the-loop](https://docs.langchain.com/oss/python/langchain/human-in-the-loop) - approve/edit/reject policies and persistent checkpointers.
- [LangGraph interrupts](https://docs.langchain.com/oss/python/langgraph/interrupts) - pause/resume rules and idempotency around interrupts.

## Protocols

- [MCP specification 2025-11-25](https://modelcontextprotocol.io/specification/2025-11-25) - current dated protocol release at verification time.
- [MCP authorization specification 2025-11-25](https://modelcontextprotocol.io/specification/2025-11-25/basic/authorization) - HTTP authorization model: OAuth 2.1, Protected Resource Metadata, resource indicators/audience binding, discovery, PKCE, and scope challenges.
- [MCP security best practices](https://modelcontextprotocol.io/docs/tutorials/security/security_best_practices) - token audience validation and prohibited token passthrough.
- [A2A Protocol latest specification](https://a2a-protocol.org/latest/specification/) - version 1.0.0 at verification time; capability discovery, tasks, messages, artifacts, streaming, extensions, and protocol-version negotiation. Send the `A2A-Version` major.minor value and do not silently depend on 0.3 fallback.

## Security and Risk

- [OWASP Top 10 for Agentic Applications 2026](https://genai.owasp.org/2025/12/09/owasp-top-10-for-agentic-applications-the-benchmark-for-agentic-security-in-the-age-of-autonomous-ai/) - agent-specific threat categories and mitigations.
- [OWASP Agentic Security Initiative](https://genai.owasp.org/initiatives/agentic-security-initiative/) - practical MCP and agent-security resources.
- [NIST AI 600-1](https://www.nist.gov/publications/artificial-intelligence-risk-management-framework-generative-artificial-intelligence) - generative-AI lifecycle risk profile.

## Observability

- [OpenTelemetry GenAI semantic conventions repository](https://github.com/open-telemetry/semantic-conventions-genai) - the GenAI conventions moved out of the core semantic-conventions pages; inspect current models, stability, changelog, and sensitive-data rules before instrumenting.
- [OpenTelemetry general semantic conventions](https://opentelemetry.io/docs/specs/semconv/general/) - spans, metrics, logs and events.

## Context Cost and Prompt Caching

- [Anthropic prompt caching](https://docs.anthropic.com/en/docs/build-with-claude/prompt-caching) — verify current cache breakpoints, lifetime, minimum prefix, pricing, and supported models.
- [OpenAI Responses API reference](https://platform.openai.com/docs/api-reference/responses) — inspect current `prompt_cache_key`, `prompt_cache_retention`, and cached-token usage fields.
- Caching is provider/model/region/version specific. Measure cache-hit tokens, total cost, latency, quality, eviction churn, and retention constraints; never claim a stable prefix is always cached or discounted.

## Current Research Routing

- For emerging methods absent from books, search primary papers and label claims `CURRENT_PRIMARY`; distinguish experimental results from established guarantees.
- [Robust Multi-Agent LLMs under Byzantine Faults](https://arxiv.org/abs/2605.09076) and [Rethinking the Reliability of Multi-agent System](https://arxiv.org/abs/2511.10400) are current examples. Their results depend on stated graph, fault, benchmark, and agent assumptions; do not generalize them into “LLM voting is Byzantine-safe.”
- Record paper version/date, experiment, threat/fault model, baseline, and exact imported claim. Apply ASM-01 to guarantee language.

### BFT and agent consensus route

Route Byzantine fault tolerance (BFT), quorum, voting, correlated-agent error, and consensus claims through `DST-01` plus `ASM-01`. Record membership, identities, timing, fault bound/type, independence evidence, adversary, safety/liveness property, and non-guarantees. Never import `3f+1` or another threshold without the protocol's assumptions.

### Budget-aware reasoning route

Route adaptive model depth, inference-time compute, test-time scaling, search, or deliberation through `ARC-05`, `PRM-03`, and `EVA-01`. Define a budget policy over latency, tokens/cost, calls, tool use, and risk; calibrate escalation on held-out task difficulty; measure quality-cost frontiers and exhaustion behavior. Do not equate a longer trace with better reasoning.

## Version Rule

Treat book code and framework APIs as explanatory examples. Before implementation, verify package versions, migration notes, current official API syntax, deprecated behavior, security advisories, protocol versions, and telemetry-convention stability. Pin dependencies, negotiate protocol versions explicitly, and encode compatibility tests.

Apply [current-corrections-2026.md](current-corrections-2026.md) before importing any version-sensitive book recommendation.
