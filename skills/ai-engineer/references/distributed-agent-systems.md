# Distributed Agent Systems

**Decision invariant:** Agreement is not truth. A majority or quorum can satisfy a decision protocol while sharing the same false evidence, model bias, compromised retriever, or invalid assumption.

Load this module when multiple workers/agents share state, vote, retry effects, recover partial work, or operate under separate ownership.

## DST-01 — Fault, Membership, and Decision Model

1. Define safety and liveness properties before choosing a voting rule.
2. Specify crash, omission, delay, stale-state, Byzantine, injection, shared-hallucination, and correlated model/retrieval faults as applicable.
3. Define identities, membership change, authentication, duplicate/Sybil resistance, and authority.
4. Model correlation: shared model family, prompt, context, tools, retriever, or training lineage means votes are not independent.
5. Select quorum/arbitration against that model; weight evidence diversity and provenance, not only count.
6. Test split brain, coordinated false majority, unavailable minority, stale membership, and malicious evidence.

**Required output:** property/fault matrix, membership protocol, decision rule, independence evidence, adversarial tests, and non-guarantees.

## DST-02 — Causal State, Durable Log, and Replay

1. Give every command/event a stable ID, schema version, actor, causal parent, order, and provenance.
2. Append accepted transitions to a durable log before publishing derived state where required by the consistency model.
3. Build disposable projections/checkpoints and record log position plus code/prompt/model/data versions.
4. Track dependencies so invalidated assumptions identify affected descendants instead of forcing global restart.
5. Capture nondeterministic model/tool outputs as versioned observations for replay.
6. Test migration, corruption, duplicate, out-of-order, and partial replay.

**Required output:** event schema, consistency boundary, checkpoint/projection plan, causal invalidation rule, and replay test.

Event sourcing gives state history; it does not make external effects exactly once or reversible.

## DST-03 — Concurrency, Effects, and Partial Recovery

1. Define the owner and concurrency model for every mutable resource.
2. Use leases with fencing tokens when stale workers can continue after failover; reject older fences.
3. Attach idempotency keys to retried effects and persist the result at the effect boundary.
4. Classify steps as pure, idempotent, compensatable, or irreversible; approve irreversible steps.
5. Use compensation only with defined business reversal semantics; it is a new effect, not time travel.
6. On failure, compute the affected causal slice, stop conflicts, restore a valid checkpoint, replay safe steps, and reconcile external state independently.

**Required output:** ownership, lease/fence design, idempotency contract, compensation table, partial-recovery algorithm, and reconciliation evidence.
