# Judge Bias and Gate Calibration

## Operating Boundary

[evaluation-testing.md](evaluation-testing.md) covers what to evaluate. This module covers the case where the measurement instrument is wrong: the judge is biased, the rubric mis-specified, or the eval set too small to support the gate stated on top of it. Use it whenever a judge score blocks a release or is reported as quality evidence.

Magnitudes below are observations from specific corpora and model versions. They prove an effect exists and matters; they are not thresholds and do not transfer to a new domain without re-measurement. Nothing here is legal or regulatory advice - these are engineering controls that help evidence an obligation owned by someone else.

## JDG-01 - Judge Failure Modes

**Trigger:** an LLM judge produces a score that gates a release, ranks two systems, or is reported as quality evidence. Measured magnitudes below are `CURRENT_PRIMARY`; inline labels mark the exceptions.

| Failure mode | Measured magnitude | Mitigation |
|---|---|---|
| Position bias | Order-swap consistency on near-identical pairs: GPT-4 65.0%, GPT-3.5 46.2%, Claude-v1 23.8%, first position favoured throughout. Elsewhere reordering alone let a 13B model "win" 66 of 80 queries. | Score both orders; a win needs preference in both, else tie. Track order-disagreement rate as judge health. |
| Verbosity bias | Doubling list length adding no information flipped the verdict in 8.7% / 91.3% / 91.3% of cases (GPT-4 / GPT-3.5 / Claude-v1). Regressing length out raised Spearman correlation with human rankings 0.94 to 0.98. | Cap or normalise length before judging; report a length-controlled score. A gain arriving with a length increase is unproven. |
| Self-enhancement | Win-rate uplift on own output ~10% (GPT-4), ~25% (Claude-v1), none (GPT-3.5); the source states its data cannot establish that the bias exists, so treat these as effect ceilings, not measurements. Self-recognition 73.5% out of the box for the strongest judge tested, >90% for two weaker models after fine-tuning on 500 examples, self-preference rising linearly with it. | Never make one model both generator and sole judge on a gating decision. Use another family, a deterministic check, or human adjudication. Strip identifiers and style tells from judge input. |
| Cannot grade what it cannot solve | Math-grading failures 14/20 default, 6/20 chain-of-thought, 3/20 reference-guided. On hard pairs with objective ground truth, strong judges score barely above random. | Supply the reference answer where one exists; it beats telling the judge to think. Where truth is computable, compute it. A model-generated reference is not one: scoring against it measures agreement with the generator, and where generator and system under test share a family the self-enhancement row above applies to the reference itself. Approving or deleting a generated *case* does not verify its *label*. |
| Non-determinism | Krippendorff α across repeated GPT-4 judge samples on the same items 0.587, below human inter-annotator 0.659 on the same task. | Repeat material scores K times; report mean and standard error. Lowering temperature is not the fix - it cuts sampling variance, not bias, and changes the configuration under measurement (JDG-04). |
| Anchoring across attributes | Scoring a second attribute in the same context as the first: the two human scores correlate at r = 0.315, the judge's at r = 0.979 - the first score all but fixes the second. Same study found a 1-10 scale beating 1-5 variants on Kendall τ. | One attribute per call - the source study's own mitigation. Never present attributes scored in one call as independent multi-dimensional evidence. Choose scale granularity by re-measurement: the coarse-scale convention is `ENGINEERING_SYNTHESIS` and the measured result above runs the other way. |
| Prompt sensitivity | Scoring one attribute first versus fourth in the same rubric moved agreement with human labels from τ 0.400 to 0.368. Separately, judges show leniency bias and can differ from human scores by up to 5 points while percent agreement stays high. | Freeze and version the judge prompt as an artifact. Report a chance-corrected agreement statistic, not percent agreement. Re-validate after any edit (JDG-03). |

**Required output:** a judge card recording model and version, prompt hash, scale, per-call attribute, order-swap policy, repeat count K, order-disagreement rate, chance-corrected agreement against human labels, and known unmitigated biases.

## JDG-02 - Rubric Construction

**Trigger:** authoring or editing the criteria text a judge scores against. Criteria text is code; write it defensively.

1. **State the desired behaviour affirmatively, as an observable predicate.** A criterion that describes the *required* behaviour in negatively-valenced words invites the judge to penalise it. Rewrite "output contains no unsupported dosage claim" as "every dosage statement is followed by a citation to a retrieved source". `ENGINEERING_SYNTHESIS` - no study isolating rubric polarity was located; adjacent work shows sensitivity to negation and unfamiliar phrasing but supplies no judge-side magnitude. Cite no paper for this; validate per rubric under JDG-03.
2. **Forbid deduction for the required property explicitly.** If the system must emit a disclaimer, abstention, hedge, or refusal, the rubric must state that its presence may not reduce the score. Otherwise the judge's preference for fluent, confident, complete-sounding text penalises compliance.
3. **Replace judgement with arithmetic wherever the property is countable.** Put the formula in the rubric: "score = supported_claims / total_claims; a claim is supported when a retrieved passage entails it". Counting reproduces, rating drifts, and intermediate counts are auditable.
4. **Order the rubric: evidence, then enumerated evaluation steps, then score.** Enumerated reasoning steps are measured to help grading of verifiable reasoning, and a supplied reference helps more (JDG-01) `CURRENT_PRIMARY`. For subjective attributes with no verifiable answer no comparable gain was located, so decide per criterion and record the decision `ENGINEERING_SYNTHESIS`.
5. **Bounded scale, one attribute per call, source retained in context, constrained output** ("output only the number", or one fixed JSON field). Anchor each scale with a worked excellent, acceptable, and poor response; prefer a binary predicate where the criterion admits one.
6. **Version the rubric with prompt, retrieval config, model version, and eval-set hash.** A rubric edit is a behavioural change to the gate.

**Required output:** a versioned rubric with one affirmative predicate per criterion, count formulae where applicable, explicit no-deduction clauses, scale anchors, and the per-criterion reasoning-step decision.

## JDG-03 - Validate the Judge Before the System

**Trigger:** before any judge output is used to claim anything about a system, and again after every rubric or judge-prompt edit.

The ordering rule: **the judge is under test first.** A judge that cannot separate a known-good output from a known-bad one tells you nothing about the system, and its system score is not evidence.

1. Per criterion build a minimal pair - known-good and known-bad differing only in that property. Include the absence case (correct answer is "not supported by the corpus") and the compliance case from JDG-02 step 2.
2. Run the judge on the pairs. Failure to separate them, or penalising the compliant member, is a rubric defect. Fix the rubric; do not proceed to the system.
3. **Diagnostic:** an unexpectedly low score on a system you have independent reason to believe correct implicates the metric first. Read the judge rationale on the case you are most confident about, checking for length, position, format, and polarity artefacts, before touching a prompt or retriever.
   Read the profile across strata, not only single scores. `JDG-04` step 1 requires strata designed to differ; when an adversarial or fatal-class stratum scores level with the normal stratum, the first two suspects are that the stratum does not contain the property it is named for and that the metric is insensitive to that property — not that the system is uniformly strong. A flat profile across strata built to differ is a finding about the eval set, and it is cheaper to find here than after the gate quotes the number.
4. Calibrate against human labels on a stratified subset and report a chance-corrected agreement statistic (Cohen's κ for two raters, Krippendorff's α for more or for ordinal scales); percent agreement can be high while absolute scores diverge by several points. Published agreement figures do not transfer - judges near random on hard objective pairs still track human preference well on open chat, so re-measure on this domain's cases.
5. **Human labels come from the exploratory set, never the frozen regression set.** Calibrating on the gate set fits the judge to the gate.
6. On weak separation apply measured mitigations in cost order `CURRENT_PRIMARY`: reference-guided grading (math-grading failures 14/20 to 3/20); few-shot judge examples (order-consistency 65.0% to 77.5%, ~4x call cost from the longer prompt); a fine-tuned lightweight judge (order-consistency 16.2% to 65.0%, trained on 20K human preference votes). Budget human labels accordingly - a fine-tuned judge is the expensive option, and its reported gain came from a five-figure label set, not a handful `ENGINEERING_SYNTHESIS`.
7. Re-run steps 1-4 after any rubric edit and record deltas. Multi-judge ensembles are widely recommended but no clean measured gain was located `UNVERIFIED`; treat ensembling as unproven cost, not a fix.

**Required output:** a judge validation record with minimal-pair results per criterion, the agreement statistic with n, mitigations applied, and residual blind spots.

## JDG-04 - Evaluation Sets and Gates

**Trigger:** creating an eval set, or stating a numeric release threshold on top of one.

1. **Stratify, do not collect by convenience:** normal cases per major input class; near-misses differing from correct by one material detail; adversarial and injection cases; absence/empty cases where the correct output is abstention; each rare-but-fatal category as its own stratum.
2. **Separate regression from exploratory.** The regression set is frozen, hash-identified, versioned with prompts, rubric, model version, index, and code, and never used to develop prompts or judges. The exploratory set is mutable and carries iteration. Production failures enter regression only by reviewed post-mortem addition.
3. **Assume contamination.** Paraphrase and translation of test items bypass n-gram decontamination, a 13B model overfitting rephrased test data reached frontier-comparable scores, and 8-18% of one widely used coding benchmark was found overlapping public pretraining sets. `CURRENT_PRIMARY` Cases drawn from public documentation or benchmarks are suspect; generated cases inherit the generator's distribution. Record per-case provenance.
4. **Report a standard error with every mean.** Binary: `SE = sqrt(s̄(1-s̄)/n)`, CI95 = s̄ ± 1.96·SE. Cluster the SE when cases share a source document, passage, or language - naive SEs were understated by up to 3x in the source analysis. Compare two systems **paired** on identical items so shared difficulty cancels - a free variance reduction. Repeat sampling K per item until within-item variance is small against between-item variance; do not lower temperature to buy the same reduction, since that changes which system is under measurement rather than measuring it better. `CURRENT_PRIMARY`
5. **Size the set to the difference you must detect.** In the source's worked example, detecting a 3 percentage-point absolute difference at 80% power and 5% significance takes n ≈ 969 independent items, which is where its recommendation of at least 1,000 items per new eval comes from; the inputs are illustrative, so recompute for the effect size and variance actually at stake. `CURRENT_PRIMARY` A 50-case set at s̄ = 0.9 has SE ≈ 4.2pp and CI95 ≈ ±8pp, so it cannot support a gate of "quality ≥ 92%" `ENGINEERING_SYNTHESIS`; small sets support only absolute gates on fatal classes and paired-difference comparisons.
6. **Weight thresholds by mistake cost, not case count.** One fatal-class failure outranks any aggregate gain. Give each failure class its own threshold and blocking status; never let a high average mask a fatal stratum.
7. **Compose the gate** from deterministic hard gates a judge cannot override; zero violations per fatal class; a paired-difference improvement whose CI excludes zero; bounded latency and cost; and for agents pass^k over k independent trials, since single-run rates overstate reliability - one function-calling benchmark reported pass^8 below 25% in a retail domain. `CURRENT_PRIMARY`

8. **Constrain uncertainty directionally.** Low confidence in an assessment may hold a gate where it is or escalate it; it may never relax it. A confident assessment can move work into a lighter lane; a low-confidence one stays at its current minimum however benign the other signals look. `ENGINEERING_SYNTHESIS` Treating uncertainty as a neutral input is what lets a case nobody could evaluate pass as a case nothing was wrong with.

**Required output:** a gate specification giving, per failure class, the metric, threshold, n, SE or CI, blocking status, and named owner, plus the frozen set hash and the version bundle it pins to.

Before editing an evaluator that is accepting or rejecting the wrong cases, write down what it must accept, must reject, and cannot evaluate: the Gate Contract in [engineering-artifacts.md](engineering-artifacts.md), and the drift rule that goes with it.

## What a Judge Structurally Cannot Catch

A judge scores whether a claim *looks* supported by the context it is shown. It has no channel to the world outside that context.

The load-bearing case: a citation carrying a real, resolvable, correctly formatted identifier - DOI, trial registration number, PMID, invoice number, SKU, diagnosis code, statute section - attached to a claim that source does not support. The identifier is syntactically valid, the prose coherent, and the identifier's true content usually absent from the judge's context, so every internal-consistency check passes. Not hypothetical: in one measurement of generative search systems only 51.5% of generated sentences were fully supported by their citations, and only 74.5% of citations supported the sentence they were attached to. `CURRENT_PRIMARY`

The control is deterministic, not evaluative: resolve every emitted identifier against the source registry, confirm the resolved record is the one actually retrieved for that span, and fail the case on mismatch. Run it as a separate hard gate no judge score can override. `ENGINEERING_SYNTHESIS`

Generalise: **verify metadata by code, verify meaning by judge.** Anything with a canonical form - identifiers, dates, quantities, units, currency, schema fields, permissions, links, ranges - is checkable by a deterministic function and must be. Reserve the judge for entailment, relevance, tone, completeness, and other properties with no closed form. For the meaning half, entailment-based faithfulness checking is credible: extract atomic claims and verify each against retrieved context, treating NLI and question-generation approaches as complementary rather than substitutable. `CURRENT_PRIMARY`

Every judge dimension duplicating a deterministic check is wasted cost and an invitation to override. Use [completeness-provenance.md](completeness-provenance.md) when a judge output carries a guarantee or provenance claim.
