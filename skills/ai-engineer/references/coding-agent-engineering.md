# Coding Agent Engineering

## COD-01 — Inspect, Patch, Verify

**Trigger:** an agent will modify a repository.

**Inputs:** requested behavior, repository instructions, workspace boundary, existing changes, test commands, allowed effects.

**Steps:**

1. Restate observable behavior, non-goals, and risk.
2. Read repository instructions and inspect version-control state without discarding user work. For unfamiliar or legacy code, recover why current behavior exists before proposing a change to it, and read across three kinds of source rather than one: what the system records (history, incidents, traces, tests), what people report, and what the documentation or model claims. One source yields only defects; the divergences between the three are what expose a stale document, an undocumented workaround, or a rule everyone follows and nobody wrote down. Order the causes you find by when each was introduced — in brownfield work the sequence usually is the diagnosis.
3. Search for the narrow implementation and test surface; read before editing.
4. Form a falsifiable diagnosis or a small implementation plan.
5. Apply the smallest coherent patch through a reviewable edit mechanism.
6. Run focused static checks/tests, then broader verification proportional to blast radius.
7. Inspect the final diff for unrelated, generated, secret, dependency, or migration changes.
8. Report files changed, evidence, residual risk, and rollback.

**Gates:** correct workspace; user changes preserved; behavior tested; no unexplained diff; external writes explicitly authorized.

## COD-02 — Generated-Code Release Gate

Split the gate into two phases; both are required, and passing the first is not evidence for the second.

**Phase 1 — mechanical:** code compiles/lints/types as applicable; focused behavior and regression tests pass; migrations and dependency changes are intentional and reversible.

**Phase 2 — semantic:** duplicated business logic across modules; layering/dependency-direction violations reached through concrete imports rather than the declared interface; assertions or debug-only constructs left in a production path; unused dependencies; inconsistencies between a contract (schema, API, tool spec) and its implementation. A linter checks syntax, not these — they need a reader who holds the intended design.

Additionally require: security-sensitive flows receive adversarial tests; generated code has ownership and maintainability review; runtime observability and failure behavior are defined; deployment has canary/rollback when risk warrants it.

Tests prove only what they assert. Inspect the changed behavior and surrounding invariants rather than accepting a green suite as sufficient evidence.

## Coding-Agent Tool Surface

Prefer distinct tools for search, read, patch, diagnostics, tests, VCS inspection, and bounded execution. Keep network, secrets, package installation, release, and destructive operations under separate policy. Record unsuccessful hypotheses to prevent loops.

## Failure Signals

Broad file reads before search, opaque rewrites, editing generated or vendored files by accident, using shell authority as a convenience, modifying tests to hide a defect, retrying the same failed command, and declaring completion without diff/effect inspection.
