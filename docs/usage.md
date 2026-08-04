# Usage patterns

## Explain

```text
Use $ai-engineer to explain the difference between a deterministic workflow,
a tool-using agent, and a multi-agent system. Give selection criteria and one example.
```

Expected result: a direct explanation, trade-offs, and the smallest-sufficient-system rule. No benchmark or formal review is launched.

## Design a system

```text
Use $ai-engineer to design a customer-support RAG system.
Constraints: private documents, 2-second p95, EU data residency, human escalation,
and citations for every policy claim. Show the smallest vertical slice and rejected alternatives.
```

Expected result: requirements and assumptions, architecture decision, data/retrieval contracts, trust boundaries, evaluation approach, rollout, fallback, ownership, and unresolved decisions.

## Review an ML or AI design

```text
Use $ai-engineer to review this design document and repository for pilot readiness.
Report evidence-backed findings first. Distinguish missing evidence from defects.
Do not change files.
```

Expected result: stage-aware findings, evidence map, important missing factors, prioritized fixes, and a verdict consistent with finding severity.

## Implement a bounded change

```text
Use $ai-engineer to implement durable human approval in this agent workflow.
Support approve, edit, reject, timeout, cancellation, restart, and idempotent resume.
Run relevant tests and report residual risks.
```

Expected result: scoped repository changes, state-machine behavior, tests, affected artifacts, and rollback notes.

## Design evaluation without running it

```text
Use $ai-engineer to create an evaluation plan for this RAG service.
Include datasets, retrieval and generation metrics, adversarial cases,
threshold calibration, release gates, and production sampling. Do not execute it.
```

## Execute evaluation explicitly

```text
Use $ai-engineer to run the supplied evaluation cases against the local endpoint.
The endpoint, dataset, budget, and authorization are attached.
Save raw results and produce a findings-first report.
```

## Diagnose a failure

```text
Use $ai-engineer to diagnose why answer quality fell after reindexing.
Locate the earliest failing layer before proposing model or prompt changes.
```

## Check current framework behavior

```text
Use $ai-engineer to implement this with the installed LangChain version.
Check the lockfile, optionally use Context7 for discovery, verify the official migration docs,
and report whether the skill's canonical documentation link changed.
```

## Add organizational constraints

Place organization-specific policies in a separate skill or source pack. Route them by name and keep their ownership, sensitivity, version, and provenance explicit. Do not paste every policy into the global `SKILL.md`.
