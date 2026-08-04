# Completeness, Provenance, and Assumption Control

Load this module for explicit audits/readiness reviews, broad or high-stakes designs, named-source work, and material guarantee claims. It prevents a locally plausible answer from being mistaken for a complete or source-supported one. It is not a universal response wrapper: ordinary explanations and bounded implementation tasks should surface only the material gaps or provenance boundaries they actually encounter.

## REV-01 — Requirement and Cross-Domain Completeness Review

1. Convert the request into atomic requirements and acceptance evidence.
2. Build a coverage matrix with one row per requirement and columns for design, implementation, verification, evidence, and owner.
3. Scan applicable boundaries: workflow, data, model/reasoning, context, tools/effects, state/concurrency, security, evaluation, operations, cost, governance, and human control.
4. Mark each cell `covered`, `not applicable` with reason, `unknown`, or `missing`. Silence never means covered.
5. Rank findings independently of the candidate's wording or self-rating. Assign the score only after findings.
6. Re-run the matrix after changes and report remaining gaps.

**Required output for a formal review/readiness decision:** requirements-to-evidence matrix, cross-domain gaps, severity, fix owner, and residual risk. For a design task, use the matrix internally and expose only the rows needed to support the requested decision unless the user asks for the full artifact.

**Gate:** a `Critical` or `Major` gap forbids “ready”, “complete”, “excellent”, or a maximum score.

**Ordered formal review record:** findings/omissions and contradictions → factor coverage/evidence → independent dimension scores → verdict → additions. Apply this order when issuing a scored review or readiness verdict, not to ordinary explanations. Never preview the verdict before findings. Each addition records `reason`, `source_class`, `required`, and `changes_verdict_to_incomplete`; Optional additions cannot change completeness unless evidence reclassifies them as required.

## SRC-01 — Source-Grounded Routing and Claim Ledger

| Label | Meaning | Required evidence |
|---|---|---|
| `BOOK` | supported by a processed book/source skill | exact source skill plus chapter/page/section locator |
| `CURRENT_PRIMARY` | current, version-sensitive, or emerging claim | official documentation, specification, or primary paper plus access date/version |
| `ENGINEERING_SYNTHESIS` | reasoned design recommendation assembled from inputs | assumptions and rationale; do not attribute it to a source |
| `ASSUMPTION` | necessary but not yet verified | owner and validation method |
| `UNVERIFIED` | plausible claim lacking adequate evidence | no reliance in a release decision |

1. A named author, book, chapter, framework, or case routes to that exact source before answering. Emit one mandatory routing field: `source_auto_load_status: loaded:<skill> | blocked_missing_source:<artifact-or-skill> | blocked_missing_identity:<needed fields> | not_applicable`. When the source pack is not installed, stop exact reconstruction and report `blocked_missing_source`; do not invent a book-backed answer from the synthesis layer.
2. Start every loaded named-source reconstruction with an artifact identity record: author/title, edition or source version, exact source skill, source artifact SHA-256, and chapter/page/section locator. A locator without the artifact hash is not sufficient for precise claims.
3. Verify each case component, stage, metric, number, quotation, and lesson. If absent, omit it or label it synthesis/unverified.
4. Use `CURRENT_PRIMARY` for provider behavior, APIs, standards, security guidance, and research newer than the corpus. Provider-specific prompt caching, context limits, retention, pricing, and eviction semantics are always version-sensitive; if primary verification is unavailable, record an explicit verification gap and use `UNVERIFIED` rather than a generic caveat.
5. A structural summary or unverified source-pack chapter cannot support `BOOK` claims until its source identity, artifact hash, and locator are verified.
6. Keep source reconstruction and recommendation in separate sections.

### Current-document maintenance loop

Run this loop whenever `SRC-01` is activated by a framework, provider, protocol, standard, security control, or version-sensitive implementation claim:

```text
identify package/provider + installed/target version
  -> discover candidate documentation (Context7 optional)
  -> open the official primary page/specification/changelog
  -> compare claim, version, URL, and access date with the skill registry
  -> use the verified rule in the task
  -> add/replace the canonical link in current-standards or the corrections overlay
  -> record old link, new link, reason, access date, and verification status
```

1. Prefer the installed lockfile/runtime version over an assumed latest version. Check migration notes when the target and latest versions differ.
2. If Context7 MCP is available, use it for discovery and version-targeted excerpts: resolve the library ID, request the exact API/behavior, and retain the returned library/version identity. Context7 is optional and is not itself the final provenance boundary.
3. Confirm the material claim on an official vendor/project page, dated specification, changelog, or primary paper. If Context7 and the official page disagree, the official version-matched source wins and the discrepancy is recorded.
4. When the canonical URL, version, or recommendation is stale or missing, update [current-standards.md](current-standards.md) or [current-corrections-2026.md](current-corrections-2026.md) in the active skill; never rewrite the book/source skill. Preserve a stable canonical URL when possible and add the access date/version.
5. If the skill is read-only or changing it is outside the authorized task scope, emit `documentation_update_status: proposed` with the exact old/new entry instead of silently mutating it. Otherwise emit `documentation_update_status: unchanged | added:<url> | replaced:<old-url>-><new-url>`.
6. A search result, generated snippet, Context7 excerpt, blog, or secondary update pack alone cannot earn `CURRENT_PRIMARY`.

**Required output when SRC-01 is activated:** `source_auto_load_status`; when loaded, artifact identity plus claim ledger with label, claim, locator, confidence, and decision impact; when blocked, missing identity fields and no reconstructed claims. Do not emit this field for ordinary non-source-routed work.

## ASM-01 — Guarantee and Assumption Audit

For every claim equivalent to *guarantees*, *exactly once*, *fault tolerant*, *safe*, *independent*, or *complete*:

1. State the property and scope.
2. Enumerate required assumptions: fault type, independence/correlation, membership/identity, timing, trust, persistence, authorization, and external-effect behavior as applicable.
3. Mark each assumption `satisfied`, `violated`, or `unknown` with evidence.
4. State what the mechanism does **not** guarantee.
5. Replace the absolute with the strongest defensible conditional claim.
6. Add tests or monitoring that expose assumption failure.

**Required output:** guarantee-assumption table, violations, non-guarantees, test/monitor, and residual risk.

## Mandatory Final Gate for Formal Reviews and Source/Guarantee Claims

- For a formal review, map every requirement or mark it explicitly unresolved.
- Give every precise/source/current claim a valid provenance label and locator.
- Give every guarantee an assumption audit.
- State material omissions and uncertainty.
- When scoring or issuing a readiness verdict, emit findings and omissions before scores or verdict.
- Keep any verdict and score consistent with finding severity.
- In a formal review record, give every optional or required addition a reason, provenance class, required flag, and verdict-impact flag.
