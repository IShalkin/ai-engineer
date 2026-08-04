# Current documentation workflow

Version-sensitive recommendations can become stale even when the engineering principle remains valid. `ai-engineer` therefore separates stable methods from a current-document overlay.

## Workflow

1. Read the installed package or lockfile version.
2. Identify the exact provider, model, region, protocol, or framework behavior needed.
3. Optionally use Context7 MCP to resolve the library and retrieve a focused documentation excerpt.
4. Open the version-matched official documentation, specification, changelog, advisory, or primary paper.
5. Compare the verified behavior with `references/current-standards.md` and `references/current-corrections-2026.md`.
6. Apply the verified behavior to the task.
7. When authorized and the skill is writable, add or replace the canonical link and record the access date and reason.
8. If verification is unavailable, label the claim `UNVERIFIED` and use a conservative fallback.

## Context7 boundary

Context7 is useful for library resolution and focused retrieval. It is not a substitute for:

- matching the installed version;
- reading official migration or security guidance;
- checking provider/model/region-specific behavior;
- validating examples against the real dependency;
- recording a primary-source locator.

Official setup guidance: [Context7 MCP clients](https://context7.com/docs/resources/all-clients).

Never commit the Context7 API key to the skill or repository.

## Update record

Use one of these statuses:

```text
documentation_update_status: unchanged
documentation_update_status: added:<url>
documentation_update_status: replaced:<old-url>-><new-url>
documentation_update_status: proposed
```

For a replacement, record the old URL, new URL, target version, access date, reason, and whether the recommendation changed.
