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

## The fork skills

Three narrower skills route into the same modules and run in their own context, so a deep analysis
does not crowd the calling conversation. Each is a routing body, not a second copy of the knowledge:

| Skill | Use it for | Loads |
|---|---|---|
| `ai-eval` | metrics, graders, LLM judges, eval-set design, thresholds, release gates, required n | `evaluation-testing.md`, `judge-bias-and-calibration.md` |
| `ai-agent-design` | graph/topology, node boundaries, tool specs, memory, HITL pauses, resume, cancellation, loop termination | `agent-harness-loop.md`, `agents-tools-protocols.md`, `architecture-decision-engine.md` |
| `ai-regulated` | regulated regimes, audit trails, validation evidence, official records, accountable approval, kill switches | `regulated-domain-controls.md`, `completeness-provenance.md` |

They rely on `skills/ai-engineer` being installed as a sibling directory, because their bodies link
into `../ai-engineer/references/`. Install all four together or the links break.

## The two agents

| Agent | Role | Tools |
|---|---|---|
| `ai-engineer` | produces work: designs, implements, verifies | read, write, edit, shell |
| `ai-engineer-critic` | refutes work already produced, reports findings, never fixes | read-only |

Both preload `SKILL.md` through their `skills:` frontmatter field. That is the mechanism that matters:
an instruction in an agent body telling it to invoke a skill is a request the model can silently
decline, and did. Only `SKILL.md` is preloaded; the modules stay on demand, which is the point.

Install them into the agents directory your harness reads (`~/.claude/agents/` for Claude Code).

## Hook-free profile

This package ships hook-free, because some environments forbid hooks by policy. Everything the skills
and agents rely on — `skills:` preloading, `context: fork` with `agent:`, `effort`, `memory: user`,
`tools` — is frontmatter, not a hook, and ports unchanged. Two guarantees are weaker:

| Mechanism | Hook-free replacement | What it gives, and what it does not |
|---|---|---|
| Read-only critic | `Bash`, `Write` and `Edit` are absent from the critic's `tools`. A tool the agent was never granted is a real mechanism, not an instruction | Holds without any hook installed. The cost is capability, not safety: the critic cannot mutation-test or run a suite, so it hands the caller an exact command with CONFIRM/REFUTE criteria instead. One residual gap is documented in the agent file itself — it holds `Skill`, and a skill may run under a wider grant |
| Review debt | One rule in `SKILL.md`'s invariants and one in the `ai-engineer` agent body. The skill body is preloaded and survives the session | Weaker than a hook, honestly. Nothing enforces it and a model can decline. Where hooks are permitted, a `PostToolUse`/`Stop` hook that tracks control-touching edits is the stronger design |

`validate_public_skill.py` enforces the first row: the critic's `tools` must stay inside a read-only
allowlist, and the build fails on `Bash`, `Write`, `Edit`, `MultiEdit` or `Task` appearing there.

### Why there is no command-filtering guard in this package

An earlier version shipped a `PreToolUse` hook that read each Bash command and denied the mutating ones,
so the critic could keep a shell. It was measured and deleted. It passed `curl -o file`, `wget -O file`,
`tar -xzf -C dir`, `unzip -o` and `git config`, and falsely refused a legitimate write to a temp path.
A filter over a surface as large as a shell is best-effort, and a best-effort control documented as a
boundary is precisely the defect this critic is built to find in other people's systems.

If you want the critic to have a shell, buy it with isolation instead: run the review against a
throwaway copy, a container, or a git worktree it may wreck, and keep the reviewed artifact out of
reach. A shell is then safe because nothing valuable is in range.

## Add organizational constraints

Place organization-specific policies in a separate skill or source pack. Route them by name and keep their ownership, sensitivity, version, and provenance explicit. Do not paste every policy into the global `SKILL.md`.
