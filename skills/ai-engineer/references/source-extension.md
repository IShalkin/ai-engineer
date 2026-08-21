# COV-01 — Source-Pack Extension

This skill is operational synthesis, and that is its finished form - no source pack is missing from it. This procedure runs only when a caller wants an exact citation out of a specific artifact they supply.

## Add a source safely

1. Keep the source in a separate skill or approved artifact store.
2. Record author/title, edition or version, artifact SHA-256, and ownership/licensing boundary.
3. Give every precise claim a chapter/page/section locator.
4. Classify each extracted unit as `source_verified`, `source_specific_unverified`, or `needs_review`.
5. Expose a compact registry containing source identity, triggers, exclusions, available chapters, fidelity state, and location.
6. Route a named-source request to the exact pack; never substitute this skill's synthesis for a missing book source.
7. Keep current framework/API/security corrections in the public operational overlay rather than rewriting the historical source.

## Runtime statuses

```text
source_auto_load_status: loaded:<skill>
source_auto_load_status: blocked_missing_source:<artifact-or-skill>
source_auto_load_status: blocked_missing_identity:<needed-fields>
source_auto_load_status: not_applicable
```

Only a verified source identity, artifact hash, and locator can support a `BOOK` claim.
