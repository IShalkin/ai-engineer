# Current Corrections Overlay (2026)

This operational overlay supersedes version-sensitive examples and defaults in the book corpus. It does not rewrite the source skills. Apply it with `SRC-01`, verify the relevant current primary source, and retain the book only as historical rationale.

## Update-input provenance

The following secondary update inputs were reviewed on 2026-08-04. Their claims become runtime rules only after primary-source verification.

| Input | SHA-256 |
|---|---|
| LangGraph and Context Engineering 2026 — Updated Resource Pack | `70B934263380AED8775277647BB8B8FEA74B16AE23A7F2763120153B4BD81492` |
| LangGraph Architecture Stress-Test 2026 | `E256E4CD96B891A38465E24E54A530D62714D4CB1E067170F54974397B59430A` |
| Fact-Check and Update: MAS, Memory, Retrieval, Security | `D76DE837BC198A866049E4A8A791110B4404C84F723CA900E6B5B400FD7DAF15` |
| Anthropic Prompt Caching, RRF Indexing and Faithfulness Gate | `E2A66D612E43E4553181E019E153CCFE83E51CC41B887EE4781726E952363BB6` |

## Replacement rules

| Deprecated or unsafe assumption | Current operational replacement | Required gate |
|---|---|---|
| Start new LangChain agents with `langgraph.prebuilt.create_react_agent` | For LangChain v1 projects, prefer `langchain.agents.create_agent`; verify installed versions and the official migration guide. Preserve old calls only for pinned legacy code. | Compatibility test + `SRC-01` |
| Customize LangChain agents only by graph surgery | Evaluate LangChain middleware as the standard extension point for model/tool wrapping, PII handling, summarization, and human review. Middleware is not an authorization, sandbox, or egress boundary. | Framework spike + external policy controls |
| Treat prompt caching as a universal static-prefix optimization | Model caching as a provider/model/region/version contract. Verify ordering, breakpoints, lookback, minimum cacheable size, TTL, pricing, and supported models in current provider docs. Never transfer Anthropic or OpenAI semantics to another provider. | `SRC-01` + measured cache telemetry |
| Use one fixed RRF constant, weight, rank origin, or top-k | Treat rank origin, `k`, weights, candidate depth, and score semantics as backend-specific. Tune on representative queries and pin the implementation contract. Raw scores are not portable across engines. | Retrieval benchmark + compatibility test |
| Treat RAG faithfulness as factual truth | Define faithfulness as support by the supplied/retrieved context. Measure world factuality, citation correctness, answer relevance, retrieval sufficiency, and permission correctness separately. | Metric contract + labeled calibration set |
| Use an uncalibrated universal faithfulness threshold | Calibrate thresholds and abstention/fallback policy on the system's own risks and data. If using a real-time judge, measure judge variance, false decisions, latency, cost, and retrieval sufficiency separately. | Release calibration + fallback test |
| Check only whether generated claims have evidence | Decompose into atomic claims and measure both decomposition precision and recall; classify each claim as supported, contradicted, or not mentioned. | Claim ledger + human-calibrated sample |
| Use needle-in-a-haystack as the long-context test | Add same-task focused-versus-bloated-context regressions at several fill levels; compare quality, cost, latency, and lost constraints. | Context-bloat regression |
| Add multi-agent architecture by default | Start with an equal-compute or equal-thinking-token single-agent baseline. Add agents only for measured isolation, permission, ownership, parallelism, or independent-evidence benefit. Sequential work and high tool counts are explicit risk cases. | `ARC-03` + baseline + ablation |
| Generalize a paper's MAS percentage or scaling factor | Record paper version, benchmark, topology, budget, model mix, statistical uncertainty, and exact imported claim. Never promote research numbers to universal defaults. | `CURRENT_PRIMARY` + `ASM-01` |
| Treat a vector database as complete memory | Design memory by purpose: working/thread state, episodic/temporal records, semantic knowledge, relationships, and preferences. Add vector, graph, relational, or archival stores only when that purpose requires them. | `MEM-01` + retention/authorization tests |
| Treat a LangGraph checkpointer as cross-thread memory | Use a checkpointer for thread-scoped execution state. Use Store or an application-owned durable service for cross-thread memory. Define retention, cleanup, tenancy, schema migration, and deletion explicitly. | Persistence/recovery test + current docs |
| Solve prompt injection with one sanitizer or model-side filter | There is no single sanitization gateway. Use defense in depth: structural instruction/data separation, least privilege, sandboxing, destination/egress control, approval for consequential effects, memory quarantine, provenance, and direct/indirect/stored-injection tests. | `SEC-01`/`SEC-02` threat model |
| Default to LangSmith, a named reranker, vector store, or observability vendor | Select products from requirements and representative benchmarks. Keep trace/eval schemas portable and record the operating owner and exit path. | Scored decision record |

## Primary routes verified 2026-08-04

- [LangChain v1 migration guide](https://docs.langchain.com/oss/python/migrate/langchain-v1) — `create_agent` migration and v1 changes.
- [LangChain middleware](https://docs.langchain.com/oss/python/langchain/middleware) — supported middleware extension model.
- [LangGraph persistence](https://docs.langchain.com/oss/python/langgraph/persistence) — checkpoints, threads, and Store distinctions.
- [Anthropic prompt caching](https://docs.anthropic.com/en/docs/build-with-claude/prompt-caching) — provider-specific caching behavior; recheck before implementation.
- [Azure AI Search RRF](https://learn.microsoft.com/en-us/azure/search/hybrid-search-ranking) — one concrete backend contract, not a portable default.
- [Ragas faithfulness](https://docs.ragas.io/en/stable/concepts/metrics/available_metrics/faithfulness/) — context-supported claims ratio.
- [DeepEval RAG metrics](https://deepeval.com/docs/metrics-introduction) — separate retrieval and generation metrics; recheck metric APIs before use.
- [Towards a Science of Scaling Agent Systems](https://arxiv.org/abs/2512.08296) — scoped experimental MAS findings, not universal guarantees.

## Release prohibitions

Do not recommend an obsolete API, fixed cache policy, fixed RRF parameter, universal faithfulness threshold, default multi-agent topology, vector-only memory, checkpointer-as-global-memory, single prompt-injection filter, or vendor product default without current primary evidence and workload-specific measurement. If verification is unavailable, mark the recommendation `UNVERIFIED`, state the conservative fallback, and keep the gap open.

Run the `SRC-01` current-document maintenance loop for every version-sensitive use. Context7 MCP may resolve and query library documentation, but the agent must still verify material claims against the version-matched official primary source and update the canonical link registry when authorized.
