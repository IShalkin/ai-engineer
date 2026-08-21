# Production Operations

## OPS-01 — Durable Execution

Persist typed state at stable boundaries. Make side effects idempotent or attach compensating actions. Encapsulate nondeterminism inside recorded tasks so replay does not change control flow. Classify errors as transient, model-recoverable, user-fixable or fatal; give each class a distinct retry, correction, interrupt or escalation path.

Use durable storage for human interrupts and long-running work. Test crash after each side effect, resume, duplicate delivery, schema migration and disaster recovery.

**Degradation must be observable when it happens, not inferable afterwards.** Four shapes hide it: a swallowed exception; a fallback that succeeds without signalling that it fired; a permissive parser dropping fields it does not recognise; and a component reporting degraded health without a reason. The middle two matter most with a model in the loop — a silent fallback means the agent reports success for a path that did not run, and a tool that quietly discards an unrecognised argument leaves the agent believing it passed a parameter that never arrived, so the next decision rests on an input the system never had. Permissive parsing of a contract is a silent failure, not tolerance. Where a swallow is genuinely correct, the annotation names the specific condition it is safe for; "non-critical" and "just in case" are not reasons. `ENGINEERING_SYNTHESIS`

For LangGraph, distinguish thread-scoped checkpoint state from cross-thread Store/application memory. Specify retention, cleanup, thread identity, tenancy, schema migration, and deletion; verify behavior against the installed version and current persistence documentation rather than book examples.

## OPS-02 — Progressive Release

Package application code, prompts, policies and schemas as versioned artifacts. Keep secrets external. Separate ingestion workers, online serving, evaluation jobs and observability pipelines. Use queues for bursty or long work, health/readiness checks, controlled concurrency and graceful shutdown. Promote through offline tests, staging, canary and monitored rollout; retain rollback-compatible state/index versions.

## OPS-03 — Observability and SLOs

Trace:

- request and conversation/thread IDs;
- retrieval queries, filters, document IDs and ranks;
- model/provider/model version and token usage;
- tool name, validated argument class, result status and latency;
- agent/state transitions, retries, checkpoints and interrupts;
- evaluator scores, policy decisions and final product outcome.

Follow current OpenTelemetry GenAI conventions where stable/applicable. Treat content, tool arguments and results as potentially sensitive; record hashes, classifications, IDs or sampled/redacted content when full payloads are not justified.

For a multi-component system heading to production, wire metrics, tracing, log aggregation and queue/backlog monitoring into the platform layer rather than per component, so a new component becomes observable by joining it instead of through later instrumentation work. `ENGINEERING_SYNTHESIS` Observability added after an incident describes the next incident, not that one, and a component whose telemetry is optional is the one that will be dark when it matters. This is a platform-layer default, not a licence to build an observability stack around a single-process prototype or exploratory work, where structured logs and a trace of model calls are the proportional answer.

### SLO model

Define availability, task-success rate, policy-violation rate, p50/p95/p99 latency, cost per successful task, retrieval quality, fallback rate and human-escalation rate. Alert on user harm and outcome degradation, not only infrastructure errors.

## Cost and Performance

Optimize in this order:

1. remove unnecessary model/agent calls;
2. reduce retrieved/context content while preserving evidence;
3. cache stable embeddings, retrieval and model prefixes/results where safe;
4. route simple tasks to smaller models;
5. parallelize independent I/O with bounded concurrency;
6. batch offline operations;
7. tune indexes and infrastructure after locating the bottleneck.

Track cost by successful task and tenant, not only tokens/request. Load-test representative concurrency, corpus size and dependency latency.

## Production Readiness

Do not release without owner/on-call, dependency inventory, permissions, capacity estimate, quality and safety gates, dashboards/alerts, fallback, rollback, incident runbook, retention/deletion process and post-release sampling plan.

For predictive ML, monitor distinct failure layers: infrastructure and serving health; input schema, quality, freshness, and drift; label availability and delayed outcomes; model relevance, calibration, and cohort performance; prediction distributions and abstention/fallback; downstream post-processing and business outcomes. Every alert needs a decision threshold, response owner, runbook, and recovery or rollback action. Track bus factor, model/data lineage, retraining authority, review cadence, and retirement criteria as part of system ownership.

## OPS-04 — Sovereign, Local, or Offline Deployment

**Trigger:** data residency, disconnected operation, regulated control, latency, or supply-chain autonomy prohibits ordinary hosted inference.

1. Translate “sovereign” into testable requirements: data/process/telemetry residency, model and dependency custody, network boundaries, update authority, key ownership, audit, and exit plan.
2. Benchmark local candidates on the actual task, hardware, context length, concurrency, and energy/cost envelope.
3. Keep ingestion, indexes, state, traces, secrets, and evaluation inside the same approved boundary.
4. Mirror/pin models and dependencies with provenance, licenses, vulnerability review, and signed releases.
5. Design offline updates, rollback, incident response, capacity, and hardware failure recovery.
6. Reject hidden external calls and test egress controls.

Local deployment improves control but does not automatically deliver privacy, safety, quality, or availability.

Use [MLD-01](ml-system-design-lifecycle.md) for ML monitoring and ownership gates.
