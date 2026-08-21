# Routing Review Checklist

A maintainer checklist, not an executable suite: there is no runner, and a human reads each case and judges the route by hand. Coverage is partial — 33 cases touch 46 of the 75 procedure IDs, so 29 IDs (ARC-04, ART-01, FIN-01 to FIN-07, FRD-01 to FRD-04, HRN-01, JDG-01 to JDG-04, MEM-01, OPS-02, PRM-03, REG-01 to REG-05, RUN-01 to RUN-03) have no case here. An ID absent from this file is unchecked, not correct.

Walk these cases after changing `SKILL.md`, descriptions, procedure IDs, or module boundaries. A case passes when the expected first procedures are selected and irrelevant source loading is avoided. Exact wording may vary; the boundary is the check.

| Case | Request signal | Expected first route | Must not load first |
|---|---|---|---|
| RT-01 | “Extract these fields from one message into JSON” | PRM-01 | multi-agent, RAG, platform |
| RT-02 | “The prompt ignores a rule in long transcripts” | PRM-02, CTX-01, CTX-02 | framework selection, RL |
| RT-03 | “Hundreds of skills exist and the agent misses the right one” | CTX-03, EVA-01 | all source skills at once |
| RT-04 | “Known approval process with pauses and retries” | ARC-02, HRN-02, OPS-01 | multi-agent by default |
| RT-05 | “Agent repeatedly calls a write tool after timeout” | TOL-01, HRN-02, OPS-01 | prompt-only fix |
| RT-06 | “Answer private policy questions with citations” | RAG-01, RAG-02, EVA-01, SEC-01 | fine-tuning as first step |
| RT-07 | “Reason across ownership relationships and paths” | RAG-03 | vector-only assumption |
| RT-08 | “Tune hybrid search relevance and shard design” | SEA-01 | general agent loop |
| RT-09 | “Agent should modify this repository safely” | COD-01, COD-02 | generic code-generation prompt only |
| RT-10 | “Compare two agent versions beyond final answer” | EVA-01, EVA-02 | one aggregate judge score |
| RT-11 | “Use an LLM to grade subjective proposal quality” | EVA-03 | deterministic equivalence claim |
| RT-12 | “Connect a remote MCP server with user data” | TOL-02, SEC-01, SEC-02 | protocol compatibility as authorization |
| RT-13 | “Parallel specialists with separate confidential context” | ARC-03, HRN-03 | shared trajectory by default |
| RT-14 | “Nightly agent should rewrite its own production skill” | EVL-01, EVL-02, SEC-01 | live self-publication |
| RT-15 | “Schedule staff under hard availability constraints” | ALG-01, ALG-02 | LLM/agent as solver |
| RT-16 | “Learn control behavior from simulator rewards” | ALG-02, EVA-01, SEC-01 | online unsafe exploration |
| RT-17 | “Find vulnerabilities in a client system” | SEC-03 | active testing before written scope |
| RT-18 | “Which book contains this exact technique?” | COV-01 | load every operational module |

| RT-19 | “The task varies from lookup to deep multi-hop work; route each request cheaply” | ARC-05, EVA-01 | one frontier model for every request |
| RT-20 | “Prompting and RAG still cannot produce a stable domain format; should we tune?” | MOD-01, MOD-02, MOD-03 | fine-tuning without held-out evidence |
| RT-21 | “Improve tool behavior from preference or verifiable reward data” | MOD-02, MOD-04, SEC-01 | unconstrained online self-training |
| RT-22 | “Deploy the agent fully offline with local models and data residency” | OPS-04, SEC-01, EVA-01 | cloud-only architecture assumption |
| RT-23 | “Review this ML design document and repository for production readiness” | MLD-02 | ordinary code review or implementation mutation |
| RT-24 | “Design a churn prediction system; the team already wants a deep model” | MLD-01, ARC-01, ALG-01 | model or framework selection before problem and baseline |
| RT-25 | “Random split scores highly, but the model fails on new users and later months” | MLD-01, EVA-01, DBG-01 | model tuning before leakage and cohort analysis |

| RT-26 | Fifteen similar agents converge, but shared evidence may make the majority wrong together | ARC-03, DST-01, ASM-01 | majority count as truth guarantee |
| RT-27 | A long coding session forgets constraints and repeatedly pays to reread context | CTX-02, OPS-03, SRC-01 | provider-independent cache claims |
| RT-28 | A late test invalidates one early assumption while most completed work remains usable | DST-02, DST-03, OPS-01 | global restart or magical rollback |
| RT-29 | Reconstruct a named book case and its reported metrics | SRC-01, REV-01 | canonical synthesis without exact source |
| RT-30 | Review says excellent while documenting a major missing safety boundary | REV-01, EVA-03 | maximum score or ready verdict |
| RT-31 | “Explain precision@k and when to use it” | EVA-02 | full readiness review or benchmark execution |
| RT-32 | “Design an evaluation plan for this RAG system” | EVA-01, RAG-02 | automatic benchmark execution or skill self-evaluation |
| RT-33 | “Run the supplied evaluation cases against this endpoint” | EVA-01, EVA-02 | plan-only response when execution artifacts and authority are available |

## Review Procedure

1. Paraphrase each case three ways, including one misleading framework keyword.
2. Record selected procedure IDs and initial files loaded.
3. Fail false positives as well as missed routes.
4. Check that no more than two task modules load initially unless the request crosses a clear boundary.
5. In the maintainer review record, capture trigger, selected procedures, initial modules, output mode, and evidence. Do not require these internal fields in the user-facing response.
6. Add real routing failures after deduplication, and add a case the first time an uncovered ID misroutes; keep a held-out paraphrase set.

7. As a maintainer check, run `python scripts/validate_public_skill.py`. Keep private target answers and organization-specific cases outside the distributed skill.

8. Assert compound trigger invariants independently of wording: multi-participant voting/correlated evidence includes ARC-03; provider-specific context/cache economics includes SRC-01 and an explicit current-primary verification result or gap; pause/resume/cancel/approval-wait/restart loops include HRN-02 rather than substituting OPS/DST; authorized-security source reconstructions include SEC-03, SRC-01, and ASM-01; every source route emits `source_auto_load_status` as loaded, blocked-missing-source, blocked-missing-identity, or not-applicable; formal review/judge output emits findings before score/verdict and gives every addition a source class.

## Negative Activation Rules

- A named framework does not automatically justify that framework.
- “Agent” in a request does not automatically justify autonomy or multiple agents.
- A long document does not automatically justify RAG if one bounded pass is enough.
- A successful final answer does not prove safe trajectory or correct authorization.
- A source-book question may load that source skill; ordinary implementation work should stay in canonical operational modules.
- Agent agreement does not establish independent evidence or correctness.
- The initial two-module budget is a discovery rule, not permission to omit a boundary found during completeness review.
- Fixed low-risk one-step deterministic work is answered directly without module loading or activation metadata; missing ordinary input does not convert it into a hyper-skill review task.
- A request to explain or design evaluation returns an explanation or evaluation specification by default; it does not trigger benchmark execution or evaluation of this skill.
- Evaluation execution requires an explicit request plus the target, data, tools, budget, and authority needed to run it.
- Procedure IDs remain internal unless traceability or a formal engineering artifact is requested.
