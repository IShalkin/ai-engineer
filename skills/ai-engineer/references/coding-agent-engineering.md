# Coding Agent Engineering

## COD-01 — Inspect, Patch, Verify

**Trigger:** an agent will modify a repository.

**Inputs:** requested behavior, repository instructions, workspace boundary, existing changes, test commands, allowed effects.

**Steps:**

1. Restate observable behavior, non-goals, and risk.
2. Read repository instructions and inspect version-control state without discarding user work.
3. Search for the narrow implementation and test surface; read before editing.
4. Form a falsifiable diagnosis or a small implementation plan.
5. Apply the smallest coherent patch through a reviewable edit mechanism.
6. Run focused static checks/tests, then broader verification proportional to blast radius.
7. Inspect the final diff for unrelated, generated, secret, dependency, or migration changes.
8. Report files changed, evidence, residual risk, and rollback.

**Gates:** correct workspace; user changes preserved; behavior tested; no unexplained diff; external writes explicitly authorized.

## COD-02 — Generated-Code Release Gate

Require:

- code compiles/lints/types as applicable;
- focused behavior and regression tests pass;
- security-sensitive flows receive adversarial tests;
- migrations and dependency changes are intentional and reversible;
- generated code has ownership and maintainability review;
- runtime observability and failure behavior are defined;
- deployment has canary/rollback when risk warrants it.

Tests prove only what they assert. Inspect the changed behavior and surrounding invariants rather than accepting a green suite as sufficient evidence.

## Coding-Agent Tool Surface

Prefer distinct tools for search, read, patch, diagnostics, tests, VCS inspection, and bounded execution. Keep network, secrets, package installation, release, and destructive operations under separate policy. Record unsuccessful hypotheses to prevent loops.

## Failure Signals

Broad file reads before search, opaque rewrites, editing generated or vendored files by accident, using shell authority as a convenience, modifying tests to hide a defect, retrying the same failed command, and declaring completion without diff/effect inspection.
