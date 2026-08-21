# Managed Agent Runtimes

Deploying an agent onto a vendor-managed serverless agent runtime. State the vendor-neutral contract first, then bind a provider. These surfaces move and their docs are largely unversioned: every quota, default, and field name below is a snapshot. Re-verify against current primary documentation; route version-sensitive claims through `SRC-01`.

## Managed-Runtime Contract

`ENGINEERING_SYNTHESIS`, each element observed in more than one provider:

- Two tiers: configuration-only managed loop, or your container/archive with the vendor owning endpoint, scaling, and identity.
- A caller-supplied session identifier is the state-routing key, and the runtime does not authenticate the user behind it. That binding is the customer's control.
- Compute is ephemeral; durable state is a separate managed service, written out explicitly.
- Auth is two-sided: inbound token validation, outbound credential brokerage from a vault. No static keys in the agent.
- The agent is a distinct platform principal, not an impersonation of the caller.
- OpenTelemetry is the telemetry contract, session to trace to span; default telemetry is thin.
- Sandboxed code execution and browser automation are separate isolated services.
- Platform versioning, publish/promote, and rollback are the change-control surface.
- Metering is compute-time plus per-call plus per-stored-record, so audit trail and policy gate are recurring variable cost.

## RUN-01 - Runtime Contract

**Trigger:** an agent will run on a vendor-managed serverless runtime rather than a process the team controls.

1. Produce a dated constraint sheet citing the source per value: protocol/port/path, health semantics, idle and maximum session lifetime, synchronous timeout, async ceiling, payload and streaming limits, CPU/memory ceiling, CPU architecture, image size, rate and concurrency quotas, and which are adjustable.
2. Externalize all state that must survive the process; local disk and in-process memory die with the environment, and a persistent session mount is not a system of record.
3. Make every handler resumable from the session identifier alone; never assume a previous request reached the same instance.
4. Convert any wait that can exceed the request timeout into a durable pause: persist an interrupt record, return, resume through a fresh authenticated invocation (`HRN-02`, `OPS-01`).
5. Report busy distinctly from healthy, and never emit a status-changed timestamp on every probe: an environment that always looks freshly updated never goes idle, runs to maximum lifetime, and exhausts the session quota.
6. Normalize throttling across protocols; quota exhaustion carries different codes and shapes on REST, streaming, and JSON-RPC transports.
7. Record which artifact version serves an in-flight session; long sessions keep the code deployed at environment creation.

**Gates:** no state existing only in the process; no handler requiring a warm predecessor; no in-process wait longer than the request timeout; every limit backed by a test, an alarm, or an accepted-risk note.

## RUN-02 - State, Memory and Identity

| Class | Lifetime | Store |
|---|---|---|
| Working state | one turn | rebuilt per invocation |
| Conversation thread | one session | checkpointer over managed store |
| Episodic memory | per actor, cross-session | managed long-term memory |
| Semantic knowledge | corpus lifetime | index or retrieval service (`RAG-01`) |
| Preferences, profile | account lifetime | authoritative product database |

1. Bind the checkpointer to the managed state service, never a local file or in-process dictionary. Expect a required thread/session key **and** actor key; actor identity is what an audit trail needs anyway.
2. Carry the acting principal explicitly through invocation, memory write, tool call, and trace; never infer it from the session key. An actor may be a person, another agent, or a system: record which, and never attribute an agent's action to a person.
3. Separate inbound from outbound auth. Inbound: validate the token against the provider's discovery metadata, asserting audience, client, scope, and required group/role claims. Outbound: vaulted per-resource credentials scoped to the agent-and-user pair, client-credentials for machines, user-consent flow for user data.
4. Never place tokens, keys, or refresh material in prompts, tool arguments, conversation state, or memory records; inject at the call boundary.
5. Enforce tenant and actor isolation with platform authorization conditions on the retrieval call, not naming discipline in a key prefix. Use trailing separators so one tenant's prefix cannot match another's.
6. Decide retention before the first write. Event-store retention is commonly per record at write time and not extensible later, and expired records are unrecoverable; confirm that, and whether deleting a raw event cascades to derived records, before relying on either for an obligation.
7. Design the approval pause for days. Persist proposal, evidence, operation, target, idempotency key, and expiry outside the process. On resume, authenticate the caller independently, re-authorize against current policy, re-check preconditions, and validate the decision payload; never trust a client-supplied approved flag (`SEC-02`).

**Output:** state-placement table, identity propagation map from caller to downstream effect, and a retention/deletion decision with verification status.

## RUN-03 - Operations and Observability

1. Instrument agent-level spans yourself; default telemetry is service metrics plus a few built-in spans, so model calls, tool calls, retries, and decisions are absent unless emitted.
2. Correlate on session, trace, and actor in every span; propagate the runtime's session header inbound and carry the session id in telemetry baggage elsewhere.
3. Separate audit from debug. Audit: actor, tenant, authenticated identity, policy decision, tool and resource, argument class, idempotency key, artifact and prompt versions, outcome, approval record. Debug: prompts, retrieved content, raw payloads, reasoning, sampled and short-lived.
4. Never log credentials or sensitive tool arguments by default; record hashes, classifications, or identifiers.
5. Route logs and spans to per-agent destinations where offered; that scopes access control, encryption keys, and retention per agent, and changing a destination does not migrate existing data.
6. Treat quotas as a design input: per-actor write throughput, per-session extraction budgets, tool-search rates, and concurrent session counts each cap a design. Size against the tightest non-adjustable limit.
7. Classify failures before retrying: transient infrastructure, session provisioning conflict, rate throttling, quota exhaustion, container-returned error, model refusal or malformed output, authorization denial, fatal misconfiguration. Back off only the first three; quota exhaustion needs a limit increase or shed load, not a retry loop.
8. Budget cold start: a stable session identifier keeps a warm environment, a fresh one per request guarantees cold start, so set the latency SLO against the cold path.
9. Deploy through platform version, publish, and rollback primitives, versioning prompts, tool schemas, policies, and eval sets with the code (`OPS-02`).
10. Model cost by driver, not token count: resident compute time, context size per turn and reread frequency, stored memory records, retrieval calls, per-tool policy checks, telemetry volume (`CTX-02`, `OPS-03`).

## Worked Example - Bedrock AgentCore

`CURRENT_PRIMARY` against the AgentCore developer guide and named package index at verification time unless labelled otherwise. Those pages carry no version or date; verify before implementation. Snapshot source: [AgentCore developer guide](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/what-is-bedrock-agentcore.html) and its [runtime service contract](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/runtime-service-contract.html).

- **Components.** Harness, Runtime, Memory, Gateway, Identity, Code Interpreter, Browser, Observability, Payments, Evaluations, Optimization, Policy, Registry, usable independently; the frequent "seven components" framing is stale.
- **Runtime.** HTTP 8080 `/invocations` (`/ws` optional), MCP 8000 `/mcp`, A2A 9000 `/`, AG-UI 8080; containers bind `0.0.0.0` and target ARM64. Health is `GET /ping` returning `Healthy` or `HealthyBusy`, plus an optional `time_of_last_update` set only on an actual status change. Synchronous request timeout 15 min, streaming 60 min, async job 8 h, payload 100 MB, image 2 GB, 2 vCPU/8 GB per session, none adjustable.
- **Sessions.** One microVM per session id, memory sanitized on termination; a stopped session resumes on a new microVM with a fresh lifecycle window until the runtime is deleted. Idle timeout must be less than or equal to maximum lifetime (defaults 15 min and 8 h, both configurable, range 60-28800 s); the idle timer resets per invocation, the maximum-lifetime timer cannot be reset. The service does **not** enforce session-to-user mapping. A microVM keeps the artifact version deployed at its creation.
- **Memory.** Immutable timestamped events plus long-term records in hierarchical namespaces, keyed by actor id and session id, where an actor may be a user, agent, or system. **No long-term records are extracted unless a strategy is configured**; a self-managed strategy owns its own record schema, so record shape is not uniform across strategy types. Namespaces are templated slash paths with `actorId`, `sessionId`, and strategy-id placeholders, trailing slash advised against multi-tenant prefix collisions; isolation is enforced with IAM condition keys for exact namespace and namespace-prefix on the retrieval action.
- **Retention one-way door.** Event expiry applies per event at write time, 7-365 days: a change affects only later events, existing events keep their original expiry and cannot be extended, expired events cannot be recovered. Whether deleting a raw event cascades to derived long-term records is `UNVERIFIED`, as are extraction latency and read-after-write.
- **Framework binding.** `langgraph-checkpoint-aws` (1.2.0 at verification) provides a saver that maps LangGraph `thread_id` to the memory session id and requires an explicit `actor_id` in the same runtime config.
- **Identity.** Inbound SigV4 or OAuth 2.0 JWT, never both on one runtime; the same authorizer config serves Runtime and Gateway: an OpenID discovery URL plus at least one of allowed audiences, clients, scopes, or typed claim validations. OAuth returns 401 with a bearer challenge to protected-resource metadata, SigV4 returns 403 with none. A user-id request header exists for callers without an IdP token; it is an unverified opaque value gated only by a distinct IAM action, so treat it as caller-asserted, not authenticated. Outbound uses a token vault documented as reachable only by the agent-and-user combination that obtained the credential; an agent access token carries workload plus user identity downstream.
- **Gateway.** Converts OpenAPI, Smithy, and Lambda targets into MCP tools, fronts other agents and HTTP services as passthrough targets, injects per-tool credentials, and offers semantic tool selection, rate-limited far tighter than direct tool invocation (search-based tool-call quota is per minute where tool-call is per second). Request interceptors are the documented place for per-tool authorization logic. AgentCore Policy, authored in natural language or Cedar, is documented as intercepting Gateway tool calls before execution; behavior when the engine is unavailable is `UNVERIFIED`, and Policy covers Gateway traffic only, so a caller that reaches a target directly is unpoliced unless the runtime restricts invocation to the gateway principal.
- **Observability.** Built-in metrics cover runtime, memory, gateway, built-in tools, and identity; service-provided spans require enabling tracing per resource, and agent-level spans require the AWS OpenTelemetry distribution SDK in the container - the collector is not supported for agent observability. Transaction Search must be enabled once account-wide or tracing cannot work. Runtime creates its log group automatically; memory, gateway, and built-in-tool log destinations must be configured. The per-agent span destination is an environment-variable override, is ignored below a minimum distribution version, and does not move existing spans.
- **Metered dimensions** (no figures): runtime, browser, and code-interpreter compute-time; gateway, identity, and Policy invocations; memory events, stored records, and retrievals; telemetry volume.

## Porting to Other Clouds

- **Microsoft Foundry Agent Service** (`CURRENT_PRIMARY`; naming volatile): config-only versus hosted agents, dedicated directory identity per agent, session state with bring-your-own document database, VM-isolated sandboxes, bring-your-own network, tool auth by key or managed identity or on-behalf-of passthrough, a versioned tool bundle behind one MCP endpoint, version snapshots and rollback, agent registry.
- **Vertex AI Agent Engine** (`CURRENT_PRIMARY` for component names only; a Gemini Enterprise rebrand is live): managed runtime for several frameworks, sessions service, memory bank of persistent long-term memories, sandboxed code execution and computer use, example store, service-account identity, platform trace and logging. Field names, extraction behaviour, and retention semantics are `UNVERIFIED`.

The port is mechanical when the design targets the contract: swap the session header, memory client, identity binding, and telemetry destination. It is a rewrite when durable state, actor identity, or the approval path depends on a vendor's field names.

Use [agent-harness-loop.md](agent-harness-loop.md) for the pause/resume state machine, [production-operations.md](production-operations.md) for durability and release, [security-governance.md](security-governance.md) for the authority gate, and [agents-tools-protocols.md](agents-tools-protocols.md) for tool and memory contracts.
