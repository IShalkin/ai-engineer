# Agent Harness and Loop Engineering

## HRN-01 — Harness Contract

**Trigger:** the model chooses actions across more than one observation.

**Inputs:** outcome, environment, authority, tools, state, evidence, budgets, evaluator, operator.

**Steps:**

1. Define typed state and lifecycle transitions.
2. Define context construction, skill/tool discovery, compaction, and provenance.
3. Expose narrow tools; enforce permission and validation outside the model.
4. Separate propose, prepare, execute, and verify phases for effects.
5. Classify errors and assign retry, correction, fallback, escalation, or termination.
6. Persist checkpoints before waits, approvals, and consequential effects.
7. Trace versions, observations, decisions, tools, state changes, cost, latency, and evaluation.
8. Assign a human/product owner and incident path.

**Gates:** no hidden mutable state; no unbounded loop; every effect attributable and recoverable; outcome externally checkable; each of the five control axes below answered separately for the action's consequence class as classified in [security-governance.md](security-governance.md) SEC-02 — deterministic-only, advised, or approval-gated — with a visible override/stop path — raised only through explicit authorization, never model preference.

### The five control axes

These are five independent questions. Answering one does not answer another, and a design that reports a single "level" has silently tied them together. `ENGINEERING_SYNTHESIS`

1. **Autonomy** — how much the system may decide and act on without a human in the path.
2. **Rigor** — how much verification and review the work carries, from a spot check to a full evidence trail.
3. **Approval authority** — who may pass the gate: nobody, the doer, a peer, a named owner, or a board.
4. **Drive** — who leads the work: a human with agent assistance, an agent with human oversight, or several agents.
5. **Involvement cadence** — how often a human is actually in the loop: never, at defined checkpoints, continuously, or at blocking gates.

Collapsing them is the common defect, and it fails in a specific direction: tying approval authority to autonomy grants the most autonomous path the weakest gate, and tying rigor to drive means work led by an agent is reviewed less precisely where it is understood least. Treat any single scale standing for more than one of these — a bare "risk level", "involvement level", "trust level" — as a naming defect to split, not shorthand to interpret.

## HRN-02 — Bounded Agent State Machine

Use explicit states such as `ASSESS -> PLAN -> PREPARE -> AUTHORIZE -> ACT -> OBSERVE -> VERIFY -> COMPLETE|ESCALATE|FAIL`. Persist state transitions and artifacts. Re-observe the environment after action; do not infer success from a tool's optimistic prose.

Terminal states must distinguish success, insufficient evidence, policy denial, user input required, dependency failure, and budget exhaustion. Repeated identical action/state pairs trigger diagnosis or escalation.

**Every terminal state carries a forward path.** Classifying a failure correctly is not handling it: a state that names what went wrong and offers nothing next is a dead end, and the dead end is the defect. Each one states what is still possible, what would unblock the rest, and how to correct or escalate — and correction cost is a design property, because an output nobody can cheaply fix discredits the next correct one. Two states are commonly missing: **a narrowed answer**, where confidence supports a smaller claim than the one requested and the system returns that subset instead of choosing between a confident overreach and a bare refusal; and **user disagreement**, which is not an error but a signal, recorded with its reason. `ENGINEERING_SYNTHESIS`

## HRN-03 — Multi-Agent Context and Topology

Add agents only for isolation, parallelism, specialization, separate authority, independent verification, or failure containment. Choose independently:

- shared trajectory vs isolated contexts with explicit handoffs;
- peer, orchestrator-worker, hierarchy, or decentralized control transfer.

Define a **data plane** of private workspaces, bounded shared artifacts, external resources, and stable references. Define a **control plane** for assignment, messaging, status, cancellation, termination, scheduling, and ownership. Large results move by artifact reference; handoffs carry conclusion, evidence, validation, uncertainty, and next action.

Name the topology as a shape, not as a count of agents. One observed shape: ordered stages, then a fan-out of independent workers, then a merge back into ordered stages, then a human decision point, then a final automated gate. `ENGINEERING_SYNTHESIS` — read off a single system, so it carries no evidence of being the right shape for another one, and it is not a starting template.

What transfers is the obligation each transition creates, independently of the shape: a fan-out needs per-worker isolation and a defined merge rule, a merge needs a conflict policy, a human decision point needs durable state across the wait, and a final gate must be able to reject work already approved upstream. Take the obligations; the one-agent comparison below still has to be lost before any multi-participant shape is justified.

A system that gains capabilities can add a participant plus its registry entry instead of a branch in a central orchestrator, which makes capability scope data that can be listed, permissioned and revoked. `ENGINEERING_SYNTHESIS` This pays once capabilities are added by people other than the orchestrator's owner, or often enough that the branch set stops being readable; for a fixed handful, the branch is the clearer artifact and a registry only adds indirection and a runtime lookup.

Compare task success, cost, latency, duplication, and failure containment against one agent.

## Failure Signals

Autonomy for known deterministic steps, state only in chat, retry without classification, supervisor approval without independent evidence, persona-only agents, shared-context explosion, circular delegation, no cancellation, and no durable artifact ownership.
