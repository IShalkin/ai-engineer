# Security, Privacy, and Governance

## SEC-01 — Threat Model

Model actors, assets, trust boundaries, data flows, tools, identities, external effects and recovery. Include direct and indirect prompt injection, agent goal hijacking, tool misuse, identity/privilege abuse, supply-chain compromise, unexpected code execution, memory/context poisoning, data leakage, denial of service, insecure inter-agent communication, cross-session persistence through startup services, scheduled tasks, shell profiles or agent config files, human-agent trust exploitation where agent output is shaped to mislead the approving human, and unsafe autonomy.

Name a control per abuse case, or record that the case is accepted and who accepted it; an abuse case with neither is an open finding, not a documented risk. Threat-model output is a versioned artifact reviewed when the actor set, the tool set, or any of the five control axes in [agent-harness-loop.md](agent-harness-loop.md) changes, not a one-time document. Keying the review to a single notion of "autonomy level" misses the case where approval authority is loosened and autonomy is not.

## SEC-02 — Authority and External-Effect Gate

Classify the action before gating it: **deterministic-only** (no model in the decision path), **advised** (model proposes, a human decides and acts), or **approval-gated** (model prepares the effect but may execute only after the binding below). Route accordingly instead of applying one uniform gate to actions of different consequence.

1. **Identity** - authenticate users, agents, services and tools.
2. **Authorization** - enforce least privilege on each resource and action; never rely on prompt instructions.
3. **Isolation** - sandbox code/tools; isolate tenants, secrets, memory and indexes.
4. **Input controls** - classify trust, validate schema, scan content and preserve provenance.
5. **Decision controls** - policy engine, budgets, confidence/evidence thresholds and approval gates.
6. **Output controls** - validate, encode, redact and restrict destinations before effect.
7. **Audit** - record actor, policy, evidence, tool, resource, decision and outcome.
8. **Response** - revoke, contain, replay, notify and learn from incidents.

Before an effect, bind authenticated actor, tenant, objective, target resource, requested operation, current preconditions, policy decision, approval if required, idempotency key, and expiry. After execution, observe the destination independently and record actual outcome. The model may propose an action but may not grant itself authority.

**Enforce where the paths converge.** Enumerate every surface through which the effect can be reached — each API, each chat or agent interface, each protocol, each scheduled or internal caller — and show that each one traverses the check. Place the control at the runtime layer they all pass through, not at the surface built first: an HTTP layer is a surface adapter, not a security boundary, and a second surface added later inherits nothing. A path that reaches the effect without entering that layer is a bypass whether or not anyone has used it yet; name it as a known gap before the surface ships. `ENGINEERING_SYNTHESIS`

**A disabled control must be disabled on purpose.** Enforcement has three states — on, off, and off-by-accident — and only the first two are designs. Assert at startup that the enforcement path is reachable from the call path and log the mode; a permit-by-default branch, a config module that documents fail-closed while being imported by nothing, or a check whose evaluation endpoint no longer exists all read as enforcement and enforce nothing. Config that documents behaviour must drive that behaviour, and a test must prove the wiring. `ENGINEERING_SYNTHESIS`

**Match the enforcement layer to the constraint, not to the strongest layer available.** Review, CI lint, commit gate, post-action hook, pre-action gate, static analysis, runtime constraint — each fits a different kind of rule. Formatting belongs in a linter; a layering or dependency-direction rule belongs in static analysis; a state-machine invariant belongs in a runtime constraint that cannot be reasoned around. Over-enforcing is a real cost, not caution: a rule enforced at a layer that cannot see what it needs produces false failures, and the team learns to bypass the mechanism. State the mechanism for every constraint; a constraint whose only enforcement is "reviewers will notice" should say so rather than imply more. `ENGINEERING_SYNTHESIS`

## SEC-03 — Authorized Offensive Assessment

Always pair `SEC-03` with `ASM-01` when describing or reconstructing authorization, safety, passive/active classification, scope containment, stop conditions, or non-guarantees. These properties depend on assumptions about identity, written authority, target ownership, network interaction, third-party impact, timing, enforcement, and human control; safe wording alone is not evidence.

1. Obtain explicit scope: systems, identities, methods, time window, data rules, rate limits, contacts, and stop conditions.
2. Verify authorization before every phase; deny scope expansion by inference.
3. Begin with passive discovery and the least intrusive technique.
4. Store findings, commands/tool calls, timestamps, evidence, and affected assets as reviewable artifacts.
5. Require a separate gate before active probing, exploitation, persistence, data access, or disruptive tests.
6. Use an out-of-band kill switch and monitor target health.
7. Stop on ambiguity, unexpected sensitive data, third-party impact, or threshold breach.
8. Report reproducible evidence, impact, confidence, remediation, cleanup, and residual risk.

This procedure applies only to authorized defensive work. It does not widen the user's authority.

## Prompt Injection Rule

Treat retrieved documents, websites, emails, tool results, tool descriptions and schema field descriptions, code comments and agent messages as untrusted data. Do not allow them to redefine system policy or authority. Separate instructions from content structurally; minimize data exposed to each call; verify consequential actions against trusted policy and user intent.

Regex/pattern sanitization and repeating system instructions may provide telemetry or catch known strings, but neither is a security boundary. Do not mutate evidence until it loses meaning. Enforce isolation, authorization, constrained tools/destinations, policy checks, approval, and effect verification outside model interpretation.

There is no single sanitization gateway. Separate untrusted content, sensitive access, and consequential external effects where possible; require approval when they must meet. Enforce destination and egress allowlists, least privilege, sandboxing, memory quarantine, and provenance. Test direct, indirect, and stored prompt injection, single-turn payloads and multi-turn escalation across a conversation, including poisoned memory recalled in a later thread. Product-specific filters are optional defenses, never authority boundaries.

## MCP and Protocol Security

- Validate token audience and issuer; prohibit token passthrough.
- Request narrow scopes and explicit consent.
- Never log credentials or sensitive tool arguments/results by default.
- Bind calls to tenant, user and resource context.
- Rate-limit, time-limit and size-limit messages.
- Sign or otherwise verify trusted server/package provenance where available.
- Pin the tool descriptions, schemas and annotations the client approved; re-verify them on every listing and re-request consent on change. A definition fetched remotely at call time, or one that varies by date or caller, is an unapproved tool.

## Data Governance

Define classification, lawful/approved purpose, minimization, region, encryption, retention, deletion, access review, lineage and incident process. Version prompts, policies, model/data cards, eval evidence and approvals. Ensure traces can be useful without becoming a second uncontrolled sensitive-data store.

## Human Authority

Require preview and approval for irreversible, externally visible, financial, privileged or safety-relevant actions. Show exact intended action, destination, evidence and uncertainty. Support approve, edit and reject; persist both proposal and decision.

This is an external-effect boundary; a separate one governs documents that themselves function as rules. No agent may approve or delete a normative document (see [ART-01](engineering-artifacts.md)) on its own authority — it may draft or propose a change, but adoption and deletion require the named human owner, independent of whether the change touches any external system.
