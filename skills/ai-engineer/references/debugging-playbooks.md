# DBG-01 — Debugging Playbooks

Find the earliest failing layer, capture evidence, change one cause, and turn the case into a regression. Do not tune generation while source, parsing, permission, state, or tool behavior remains unverified.

Before changing any cause, build a deterministic check that fails on the reported symptom and run it at least once — a fix whose check never failed first is unfalsifiable. State three to five candidate causes with the observation each one predicts, then probe them one variable at a time. A symptom that cannot be reproduced is the first finding, not a licence to start editing.

## RAG Failure

1. Confirm source exists and caller may access it.
2. Inspect parser output and chunk boundaries.
3. Run retrieval without generation on the frozen query.
4. Check filters, embedding model, distance and index freshness.
5. Inspect candidate recall, then reranking.
6. Verify context ordering, redundancy and truncation.
7. Check whether generation ignored or contradicted evidence.
8. Add the case to the failing layer's regression set.

## Agent Loop or Wrong Tool

1. Inspect state before each decision.
2. Confirm tool names/descriptions and schemas are mutually distinct.
3. Check whether successful results are written back to state.
4. Validate routing and termination conditions.
5. Enforce hard budgets and repeated-call detection.
6. Replace model choice with deterministic routing where possible.
7. Test a one-agent or workflow baseline.

## High Latency or Cost

Build a trace waterfall. Count model, retrieval and tool calls. Identify sequential independent I/O, retries, oversized context, slow rerankers, large models and duplicate work. Optimize the largest measured contributor; verify quality after each change.

## Production-Only Failure

Compare offline and production input distributions, permissions, index/model/prompt versions, concurrency, dependency latency and feature flags. Confirm traces contain the same component metrics as evaluation. Reproduce from a sanitized trace; turn the incident into a regression case.

## Unsafe Action

Revoke or contain first. Preserve audit evidence. Identify instruction source, authority check, tool permission, validation, approval and effect boundary. Fix the earliest missing control; add adversarial tests and review similar tools/agents.

## Multi-Agent Stalemate

Inspect task contracts, ownership, shared-state conflicts, arbitration and termination. Remove agents with identical context/tools. Add a coordinator or deterministic merge only when evidence conflicts. Bound debate/reflection rounds.
