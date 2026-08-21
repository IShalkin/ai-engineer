# Financial Crime, Credit Decisioning, and Model Risk Management

This module owns the BSA/AML, sanctions, and credit-decisioning specifics - the model-classification determination, threshold governance under the FFIEC manual, regulator-set fraud-rate metrics, CDD/KYC evidence and staleness, and SAR clocks and retention - while [fraud-model-risk-guardrails.md](fraud-model-risk-guardrails.md) is canonical for the shared model-risk framework, detection-system design, adverse-action explainability, and agent authority controls, and its citation wins wherever both state the same control.

Engineering controls for AI in fraud prevention, AML/sanctions screening, and credit-adjacent decisioning about people. These are controls that help an accountable owner satisfy an obligation; none of this is legal advice and the obligation is never transferred to engineering.

Instruments cited are US federal banking and consumer-credit sources unless marked otherwise; one EU payments instrument appears as an example of a regulator-set numeric metric. Regulation is jurisdiction- and version-specific: confirm the instrument and amendment in force before designing to a number in it.

## FIN-01 - Classify, Then Inventory

The 2011 interagency `Supervisory Guidance on Model Risk Management` (Federal Reserve SR 11-7; OCC Bulletin 2011-12; FDIC FIL 22-2017; April 4, 2011) defines a model as "a quantitative method, system, or approach that applies statistical, economic, financial, or mathematical theories, techniques, and assumptions to process input data into quantitative estimates", with three components - information input, processing, reporting - and covers approaches whose inputs are qualitative or judgmental provided the output is quantitative. `CURRENT_PRIMARY`

1. Decide per system whether it meets that definition and record the reasoning. The `Interagency Statement on Model Risk Management for Bank Systems Supporting Bank Secrecy Act/Anti-Money Laundering Compliance` (Federal Reserve, FDIC, OCC; April 9, 2021) states the determination is bank-specific and that single-factor threshold reports and CTR aggregation likely are not models. `CURRENT_PRIMARY`
2. Do not use classification as an escape hatch: the same statement says risk management "should be consistent with safety and soundness principles" whether the system is called a model, a tool, or an application. `CURRENT_PRIMARY`
3. Treat an LLM that scores or ranks as inside the model boundary. An LLM that only drafts narrative may fall outside the quantitative-output definition yet still needs the same change control and audit trail. `ENGINEERING_SYNTHESIS`
4. Keep a firm-wide inventory of models in use, in development, and recently retired: purpose and products, permitted and restricted uses, input type/source, component models, outputs and intended use, functioning status, last update, policy exceptions, named development and validation owners, completed and planned validation dates, expected validity window. Any variation warranting separate validation is a separate cross-referenced entry. `CURRENT_PRIMARY` Version prompts, indexes, tool definitions, features, and thresholds as inventory attributes, not untracked config. `ENGINEERING_SYNTHESIS`

Model risk is "the potential for adverse consequences from decisions based on incorrect or misused model outputs and reports", from two causes: fundamental error, and correct output used incorrectly or outside its designed environment. The second dominates in agent systems that reuse a score for a purpose never validated. `CURRENT_PRIMARY`

## FIN-02 - Three Elements and Effective Challenge

Three elements: development/implementation/use; validation; governance, policies, controls. The guiding principle is "effective challenge" - "critical analysis by objective, informed parties who can identify model limitations and assumptions and produce appropriate changes" - depending on incentives, competence, and influence. `CURRENT_PRIMARY`

| Validation element | Content | Artifact |
|---|---|---|
| Conceptual soundness | design/construction quality, developmental evidence, assumptions, variable choice, data relevance, comparison to alternatives, sensitivity analysis | design record, baseline ladder, sensitivity report |
| Ongoing monitoring | process verification (input accuracy, auditable code change control), benchmarking to alternative internal/external models or data, override analysis | monitoring plan, benchmark comparison, override ledger |
| Outcomes analysis | outputs versus actual outcomes, back-testing on a period not used in development at the forecast/performance frequency, parallel outcomes analysis on adjustment | back-test record, champion-challenger result |

1. Validation is performed by people not responsible for development or use and with no stake in the outcome; where developers do part of it, an independent party critically reviews and adds work. Independence "should be judged by actions and outcomes", evidenced by models actually changed as a result of validation. `CURRENT_PRIMARY`
2. Track override rate and override performance. High overrides, or overrides that consistently improve performance, are evidence the model needs redevelopment - not that human review is working. `CURRENT_PRIMARY`
3. Champion-challenger is parallel outcomes analysis: if the adjusted model does not outperform the original against realised outcomes, more change or redesign is needed before replacement. `CURRENT_PRIMARY`
4. Review each model at least annually; validate material changes before implementation. Policy may permit immaterial changes without revalidation, or component revalidation, if written and approved in advance. `CURRENT_PRIMARY`
5. Deficiencies unfixable within the model's framework mean rejection, not shipping behind a disclaimer. Where validation cannot precede use (data paucity), document it, tell users and management, and mitigate with compensating controls. `CURRENT_PRIMARY`
6. Vendor models: validate your own use. Demand developmental evidence, test results, stated limitations, vendor monitoring; lean on sensitivity analysis and benchmarking where code is closed; document customisation; monitor outcomes on your own data; hold a contingency plan for vendor loss. The 2021 statement adds that validation independence matters especially "when banks outsource multiple functions to the same third party" - a constraint on buying model, monitoring, and validation from one vendor. `CURRENT_PRIMARY`
7. Documentation must let a reader unfamiliar with the model understand how it operates, its limitations, and key assumptions. That is the model-card acceptance criterion. `CURRENT_PRIMARY`

## FIN-03 - Threshold Governance

A threshold is a governed artifact, not a tunable constant.

1. The FFIEC BSA/AML Examination Manual states the authority to establish or change expected-activity profiles should be clearly defined in policy, monitoring-system access limited, and changes should generally require approval of the BSA compliance officer or senior management. `CURRENT_PRIMARY`
2. Management must document and explain filtering criteria and thresholds and why both suit the institution's risk; review and test them periodically; and independently validate the monitoring system's programming methodology and effectiveness to confirm it detects potentially suspicious activity. `CURRENT_PRIMARY`
3. Test both sides: sample alerts at or above the threshold and activity suppressed below it, showing the suppressed population is genuinely low-risk. Retain both samples as the change record's evidence. `ENGINEERING_SYNTHESIS`
4. Record per change: prior value, new value, alert-volume and detection impact, sampled evidence, approver, effective date, rollback value. `ENGINEERING_SYNTHESIS`
5. Detection may be deliberately inefficient. The 2021 statement recognises BSA/AML models "place greater emphasis on coverage over efficiency" and that a bank "may choose to accept a reduction in efficiency (such as by producing more alerts) in exchange for greater coverage". `CURRENT_PRIMARY` Never let an alert-volume SLO silently retune coverage down.
6. A regulator may set the metric. Under Commission Delegated Regulation (EU) 2018/389 (RTS on strong customer authentication) the transaction-risk-analysis exemption holds only while the monitored fraud rate for that transaction type is at or below an Annex reference rate tied to an exemption threshold value - remote card-based payments 0.13% at EUR 100, 0.06% at EUR 250, 0.01% at EUR 500; remote credit transfers 0.015%, 0.01%, 0.005% at the same values - calculated on a rolling 90-day basis, subject to audit review, and ceasing when the rate exceeds the reference rate for two consecutive quarters. `CURRENT_PRIMARY` (EU; verify the amendment in force) Such a metric is a hard release gate and a monitored SLO, not an internal target.

## FIN-04 - Metrics, Labels, Feedback

1. Accuracy is meaningless at these base rates: predicting "not suspicious" everywhere scores near-perfect and detects nothing. Report precision, recall, PR-AUC, alerts per investigator-hour, and detection at fixed review capacity. `ENGINEERING_SYNTHESIS`
2. Weight errors by cost - fraud loss, investigation cost, customer harm from a wrongful freeze, regulatory consequence differ by orders of magnitude. Pick the operating point on the cost-weighted curve and name who owns that cost function. `ENGINEERING_SYNTHESIS`
3. Labels arrive late, partial, and biased by your own past decisions: blocked transactions never reveal ground truth, unalerted activity is unlabelled by construction. Feed dispositions and confirmed outcomes back as versioned labels carrying decision timestamp and producing model version, and hold a randomised or below-threshold sample outside the policy to estimate the missed population. `ENGINEERING_SYNTHESIS`
4. Expect no clean outcome label. The 2021 statement notes testing for some BSA/AML models "may not include the same techniques as other models" because of "the lack of information about realized outcomes (e.g., Suspicious Activity Reports)". `CURRENT_PRIMARY` Substitute benchmarking, coverage testing, and typology scenario sets, and say so in the validation report rather than passing a proxy off as an outcome.
5. Split by time and by entity so an entity in training cannot appear in test and the model is never scored on information unavailable at decision time.
6. Credit scoring carries an explicit duty: a creditor "is responsible for ensuring its system is validated and revalidated based on the creditor's own data when it becomes available" (12 CFR part 1002, Supp. I, comment 2(p)-3). `CURRENT_PRIMARY`

## FIN-05 - Drift and Adversarial Adaptation

Distributions move because an adversary optimises against the deployed control. Drift is a security property, not only a data-quality one.

1. Monitor input and score distributions, alert mix by typology, precision on newly labelled cases, and cohort performance. Alert on outcome degradation, not just pipeline health.
2. Assume probing: rate-limit and log score-exposing surfaces, avoid returning granular scores to untrusted callers, rotate enumerable elements.
3. Keep a rapid-change path. The 2021 statement recognises BSA/AML models "may require quick adjustments to reflect the changing nature of criminal behavior". `CURRENT_PRIMARY` Pre-approve which change classes take the fast path and what evidence each needs; do not improvise governance mid-incident.
4. Release progressively: shadow the candidate on live traffic with no effect, compare to champion on identical cases, canary a bounded population carrying the offline metrics through, then roll out retaining a rollback version of model, thresholds, and features together.
5. Pilots are protected, not exempt. The `Joint Statement on Innovative Efforts to Combat Money Laundering and Terrorist Financing` (Federal Reserve, FDIC, FinCEN, NCUA, OCC; December 3, 2018) states pilots "should not subject banks to supervisory criticism even if the pilot programs ultimately prove unsuccessful", pilots exposing gaps "will not necessarily result in supervisory action", and where an AI-based monitoring system finds suspicious activity existing processes would have missed, the agencies "will not automatically assume that the banks' existing processes are deficient". `CURRENT_PRIMARY` Finding more is not self-incrimination; run pilots alongside the production control, not instead of it.

## FIN-06 - Reason Codes as Forcing Function

Opacity is not a defence. Under ECOA and Regulation B a creditor taking adverse action must state reasons that are "specific" and indicate the "principal reason(s)", and those reasons must "relate to and accurately describe the factors actually considered or scored by a creditor" (15 U.S.C. 1691(d)(2)-(3); 12 CFR 1002.9(a)(2)(i), 1002.9(b)(2)); notification is generally due within 30 days (12 CFR 1002.9(a)(1)). Citing internal standards or policies, or failure to achieve a qualifying score, is insufficient. `CURRENT_PRIMARY`

Two CFPB circulars once carried the sharpest statement of this - that a creditor cannot justify noncompliance because its own technology is too complex or opaque to understand, and that broad or vague reasons obscuring the real ones are not enough. Both were withdrawn (`Interpretive Rules, Policy Statements, and Advisory Opinions; Withdrawal`, 90 FR 20084, applicable May 12, 2025), so do not cite them as authority. `CURRENT_PRIMARY` The codified disclosure duties above are unaffected, and the engineering consequence is unchanged: opacity is not a defence, because the duty attaches to the disclosure, not to the technique.

1. The reason-code path is a release-gated product requirement. If the architecture cannot emit accurate principal reasons, it is not shippable for that decision - reason generation cannot be bolted on later. `ENGINEERING_SYNTHESIS`
2. Reasons must derive from the factors the deployed model actually used, bound to that applicant's scored feature values at that model version. A narrative from a separate LLM never given the attributions is a fabricated reason. `ENGINEERING_SYNTHESIS`
3. An LLM may render an accurate reason set into readable language; it may not select, rank, or invent reasons. Constrain it to a validated code set and diff its output against the source attributions before disclosure. `ENGINEERING_SYNTHESIS`
4. FCRA and ECOA disclosures are distinct. Regulation B commentary states that disclosing the key factors that adversely affected a credit score does not satisfy the ECOA specific-reasons requirement (12 CFR part 1002, Supp. I, comment 9(b)(2)-9); FCRA separately requires the "key factors that adversely affected the credit score of the consumer", all relevant elements in order of importance, generally capped at four (15 U.S.C. 1681g(f)(1)(C), 1681g(f)(2)(B), 1681m(a)(2)). Emit both from the same evidence; neither satisfies the other. `CURRENT_PRIMARY`

Fair-treatment testing sits alongside, and its legal footing under this specific regulation is in motion - so state the control on engineering grounds, not on the theory. Regulation B once carried official commentary explaining an "effects test" for facially neutral creditor practices; a 2026 CFPB final rule (91 FR 21620, effective July 21, 2026) deleted that commentary and revised 12 CFR 1002.6(a) to state that the Act "does not provide that the 'effects test' applies for determining whether there is discrimination in violation of the Act". `CURRENT_PRIMARY` Cohort testing survives that change: other statutes, other regulators and other jurisdictions are untouched by it, and a model whose error rate differs sharply by cohort is defective on its own terms. The disclosure duties above are also unaffected. Controls: test outcome and error rates by cohort before release and on a schedule after; test features and candidate proxies, not only the final decision; record the stated justification and the alternatives actually evaluated for each retained feature, and keep that search reviewable. Which legal theory the testing serves is the accountable owner's call, not engineering's. See `FRD-03` for the same control stated in full.

## FIN-07 - Autonomy Limit on Adverse Action

An autonomous agent may not take an adverse action against a person unless the action is evidenced, reviewable, explainable, and appealable. Absent all four, the agent proposes and a human decides. Adverse action here includes declining or repricing credit, freezing or closing an account, blocking a payment, and exiting a customer.

1. **Evidenced** - the record binds authenticated actor, subject, model and prompt versions, thresholds in force, input feature values, retrieved evidence IDs, policy decision, timestamp. Retention follows the applicable rule; for SARs and supporting documentation, five years from filing (31 CFR 1020.320(d)). `CURRENT_PRIMARY`
2. **Reviewable** - a named human can reconstruct the decision from the record without rerunning the model. The FFIEC manual expects documented conclusions and documented SAR decisions including the specific reason for filing or not filing, with examiners focused on the effectiveness of the decision-making process rather than individual decisions. `CURRENT_PRIMARY`
3. **Explainable** - accurate principal reasons exist per FIN-06 before the action is communicated, not after an appeal.
4. **Appealable** - a route to human reconsideration exists, is disclosed where required, and its outcomes feed FIN-04 labels.

Hard boundaries:

- Statutory clocks are deadlines, not agent discretion: a SAR is filed no later than 30 calendar days from initial detection, extended to 60 if no suspect is identified (31 CFR 1020.320(b)(3)); continuing activity is reviewed at 90 days with filing by 120 days after the prior related SAR (FFIEC manual); currency transactions over $10,000 are reported (31 CFR 1010.311). Instrument the clock with escalation before breach. `CURRENT_PRIMARY`
- SAR existence is confidential (31 CFR 1020.320(e)). An agent must not surface, hint at, or explain a SAR to the subject; keep SAR-derived context in a segregated store excluded from customer-facing retrieval. `CURRENT_PRIMARY`
- CDD/KYC duties - understanding the nature and purpose of the relationship, ongoing monitoring, identifying beneficial owners (31 CFR 1020.210(b)(5); 25% equity prong and control prong at 31 CFR 1010.230) - define what identity evidence an agent must hold before acting on an entity, and the staleness at which it must refuse. `CURRENT_PRIMARY`
- Where a decision is later contested through dispute or representment, the evidence package assembled at decision time is what gets produced. Design the record to be sufficient then, because it cannot be reconstructed afterwards. `ENGINEERING_SYNTHESIS`

## Cross-Module Links

Use [ml-system-design-lifecycle.md](ml-system-design-lifecycle.md) for the design sequence and stage-aware review, [evaluation-testing.md](evaluation-testing.md) for datasets, metrics, and release gates, [production-operations.md](production-operations.md) for progressive release and monitoring layers, [security-governance.md](security-governance.md) for the external-effect gate and audit record, and [completeness-provenance.md](completeness-provenance.md) when a guarantee or independence claim is asserted.
