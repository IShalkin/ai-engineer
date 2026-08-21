# Data, RAG, Graph, and Search

## Contents

- Ingestion contract
- Chunking
- Embeddings and stores
- Retrieval ladder
- Graph RAG
- OpenSearch decisions
- Evaluation and failure modes

## RAG-01 — Ingestion Contract

Version source identity, access policy, parser, transformation, chunking, metadata schema, embedding model and index. Preserve source URI, document version, section/page, timestamps and permissions through every stage. Make ingestion incremental and replayable; never mutate the only copy of source data.

## Chunking Decision

| Content | Prefer | Watch |
|---|---|---|
| Structured docs | heading/section-aware chunks | orphan headings and lost hierarchy |
| Narrative prose | recursive or semantic boundaries | excessive overlap and topic mixing |
| Tables | row groups plus headers/context | flattened cells without column meaning |
| Code | symbol/function/class boundaries | broken imports and detached definitions |
| Conversations | turns plus window and speaker metadata | pronoun loss and privacy |
| Long parent sections | child retrieval with parent expansion | duplicate evidence |

Choose chunk size from expected questions and evidence granularity. Test several configurations on a frozen query set; do not inherit a universal default.

## Embeddings and Store Selection

Evaluate domain fit, language, modality, dimensions, context limit, normalization, distance metric, latency, cost and update stability. Pin model versions and reindex deliberately.

Choose a store from required metadata filtering, hybrid lexical/vector search, index algorithms, update/delete behavior, scale, tenancy, backup, observability and team operations - not benchmark popularity.

Where the corpus carries governed terms — states, categories, entity kinds the system acts on — keep that set closed at ingestion as well as at generation; see the closed-vocabulary rule in [context-prompt-engineering.md](context-prompt-engineering.md). A corpus that models also write into is where an invented synonym becomes the next retrieval's evidence.

## RAG-02 — Retrieval and Evidence Packet

Apply the smallest technique that fixes a measured failure:

1. lexical/vector baseline;
2. metadata filtering;
3. hybrid lexical-vector fusion;
4. multi-query expansion;
5. HyDE when query and document language differ materially;
6. sentence-window or parent-document expansion when context is fragmented;
7. reranking when candidate recall is adequate but ordering is poor;
8. decomposition for multi-part questions;
9. routing across vector, SQL, graph, API or web sources;
10. auto-merging or iterative/agentic retrieval for complex evidence gathering.

Tune candidate retrieval for recall, then reranking/filtering for precision. Return an evidence packet with query, filters, retriever/index versions, ranked stable IDs, excerpts, provenance, authorization result, and uncertainty. Track the exact packet passed to generation.

Where the corpus carries authority — policies, decisions, standards, approved records — retrieval authorization is a function of lifecycle state and authorship, not of caller permission alone. An unadopted document is a different authority class, not a less relevant one; encode that in the index and the filter rather than in the ranker or the prompt, and state the matrix per status and per author class instead of letting one flag stand for all of them. `ENGINEERING_SYNTHESIS` A draft or proposal the system itself produced may be retrievable so it can see its own pending work, provided every excerpt carries its non-adopted status; a human's undecided proposal may be withheld entirely, because exposing it lets an agent act on a decision nobody made and quote it back to people as policy. Superseded and withdrawn states each need their own answer rather than inheriting the approved one.

Failure signal: an answer citing a real document with correct provenance for a rule that was never adopted.

For reciprocal-rank fusion, treat rank origin, fusion constant, weights, candidate depth, and score interpretation as backend-specific. Benchmark and pin them for each query class; do not transfer raw scores or a fixed `k` between engines.

## RAG-03 — Hybrid, Graph, Multimodal, and Agentic RAG

Use graphs when explicit relationships, paths, constraints or multi-hop reasoning are first-class. Define ontology, entity identity, relation semantics, provenance and update policy before graph construction. Test entity resolution and relation correctness separately from question answering. Combine graph traversal with vector retrieval when questions need both relations and semantic similarity.

Use multimodal retrieval only when meaning depends on layout, image, audio, or video evidence; retain modality, time/page/region coordinates, and cross-modal provenance. Use agentic/iterative retrieval only when query decomposition or route choice must respond to intermediate evidence; bound calls and compare against a planned retrieval workflow.

## SEA-01 — OpenSearch Decisions

- Treat mappings and analyzers as versioned API contracts; reindex behind aliases.
- Use filter context for exact constraints and query context for relevance.
- Design shard count from data size, write/query mix and recovery, not a fixed rule.
- Measure relevance and latency with representative queries before tuning heap, shards or replicas.
- Validate snapshots, restore, allocation awareness and failure recovery.
- Evaluate lexical and vector retrievers independently before hybrid fusion.

## Evaluation

Measure:

- ingestion completeness and parse defects;
- retrieval recall@k, precision@k, MRR/nDCG where appropriate;
- context relevance, redundancy and permission correctness;
- answer faithfulness/groundedness and citation correctness;
- task success, abstention and latency/cost.

Failure order: source missing -> parse/chunk defect -> representation mismatch -> filter/routing defect -> low recall -> poor ranking -> context overload -> generation misuse. Fix the earliest failing layer.

Faithfulness measures whether output claims are supported by the supplied context; it is not world factuality. Evaluate retrieval sufficiency, contextual precision/recall/relevance, answer relevance, factuality, citations, and permissions separately. For claim-level gates, decompose atomic claims, measure decomposition precision and recall, and classify each as supported, contradicted, or not mentioned. Calibrate thresholds and fallback on system-specific data; no universal score is a release standard.
