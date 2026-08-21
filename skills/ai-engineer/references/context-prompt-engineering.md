# Context and Prompt Engineering

## PRM-01 — Versioned Prompt Contract

**Trigger:** a model must perform a bounded semantic task.

**Inputs:** user outcome, trusted instructions, untrusted content, typed input schema, output consumer, constraints, examples, evaluator.

**Steps:**

1. State the task as an observable outcome, not a persona.
2. Put authority and non-negotiable constraints in the trusted instruction layer.
3. Define inputs and outputs with explicit schemas and field semantics.
4. Delimit untrusted evidence; say what it may inform and what it cannot override.
5. Specify decision criteria, abstention/escalation, and forbidden effects.
6. Add the minimum examples needed to resolve ambiguity; cover a boundary case.
7. Version prompt, schema, model settings, and evaluator together.
8. Test direct instructions, paraphrases, missing data, conflicts, adversarial data, and output consumption.

**Gates:** schema-valid output; no instruction/data confusion; acceptance criteria measurable; caller handles refusal and malformed output.

**Output:** prompt interface plus frozen prompt tests.

## PRM-02 — Prompt Failure Diagnosis

Do not append more prose first. Classify the earliest defect:

1. unclear outcome or output contract;
2. missing/incorrect context;
3. conflicting priority or trusted/untrusted boundary;
4. model lacks capability;
5. task needs a tool, retrieval, workflow, or deterministic validation;
6. stochastic variance or evaluator defect.

Change one layer and rerun the same cases. Promote stable validation or business rules from prompt text into code.

## CTX-01 — Context Assembly

Build in this order to support stable prefixes and clear authority:

1. system policy and role;
2. applicable procedures and tool rules;
3. trusted task state and authoritative knowledge;
4. bounded retrieved evidence and recent observations;
5. current request and output schema.

Maintain a context manifest containing source, owner, trust, freshness, sensitivity, token cost, and purpose. Exclude content with no decision relevance.

## PRM-03 — Reasoning and Decomposition Strategy

Ask for outputs that can be checked: plan, assumptions, calculations, evidence, alternatives, confidence, or tool trace. Do not require or store private hidden chain-of-thought. Choose the mechanism from task structure:

- deterministic decomposition for known steps;
- model-generated plan with typed steps for open decomposition;
- ReAct-style observe/act loop for tool-dependent decisions;
- multiple candidate solutions/tree or beam search only when diversity plus an independent verifier improves results;
- established search/CSP/planning algorithms when the state space is formalizable.

Bound candidates, depth, tool calls, and reflection. Verification must add an external signal—tests, environment state, evidence, or a calibrated rubric—not merely ask the same model to “think again.”

## CTX-02 — Triage, Isolation, and Semantic Compaction

Classify material:

- **P0 pin verbatim:** authority, safety, hard constraints, exact identifiers, acceptance gates.
- **P1 preserve semantically:** architecture decisions, changed artifacts, verified results, unresolved risks.
- **P2 summarize:** reasoning narrative and tool results whose evidence is retained elsewhere.
- **P3 drop:** duplicated, obsolete, or non-actionable exploration.

Prefer isolation when a subtask will produce large or conflicting traces. Require a handoff packet with question, conclusion, evidence, artifacts, uncertainty, and next action. After compaction, test whether the next decision can be made and whether exact constraints/identifiers remain recoverable.

### Retention and provider-verification gate

Maintain a preservation ledger for pinned constraints, decisions, evidence pointers, cacheable artifacts, eviction eligibility, and recovery tests. Define a working-set budget and measure quality together with tokens, bytes reread, latency, and cost. Any claim about a provider's prompt caching, context limits, retention, pricing, eviction, or API behavior is version-sensitive: activate `SRC-01`, verify current primary provider documentation, and record version/access date. Without that evidence, label the behavior `UNVERIFIED`, keep provider verification as an explicit gap, and design the controller against a provider-neutral interface rather than assuming identical semantics.

Do not hardcode a universal cache prefix, breakpoint count, minimum size, TTL, lookback, or discount. Record the provider/model/region/version contract and test cache-hit tokens, quality, cost, latency, and eviction. Add a same-task focused-versus-bloated-context regression at multiple fill levels; a needle-in-a-haystack test alone is insufficient.

## CTX-03 — Progressive Discovery

Maintain a compact registry: capability, trigger, exclusions, expected input/output, location, version, and cost. Route by the current cognitive function and risk; load details only after selection. Test both artifact correctness and activation: the system must retrieve and follow the right skill under realistic phrasing while avoiding false activation.

## Failure Signals

Prompt bloat, unstable static prefixes, hidden conflicting instructions, copied raw traces, lost identifiers, summaries without evidence, every skill loaded globally, demanded hidden chain-of-thought, unbounded self-reflection, and fixes that pass the example but fail paraphrases.
