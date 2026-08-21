# Layer 3 Judge Protocol — Artifact Scoring

Layer 3 scores the artifact a skill run produced. Layers 1 and 2 (routing facts, deterministic
checks) are not in scope here and must not be re-decided by a model.

Authority: `skills/ai-engineer/references/judge-bias-and-calibration.md` (JDG-01..JDG-04) and the
`EVA-03` / `Release Gate` / `Completeness, Grounding, and Anti-Sycophancy Gates` sections of
`skills/ai-engineer/references/evaluation-testing.md`. Every rule below carries the ID it comes
from. **If anything here contradicts those modules, the module wins and this file is the defect.**
One contradiction is called out explicitly in section 4.

This document sets no passing score, no tolerance, no numeric bar, and no set size. Every threshold,
and the decision to run this layer at all, is owned by **the maintainer**.

**Enforcement status: none of it.** No code in this repository implements any rule below. Nothing
strips identifiers, scores both orders, computes κ/α, caps length, repeats a score K times, freezes
or hashes the judge prompt, or parses a `REFUSE-TO-SCORE` reply. There is no runnable Layer 3. Every
rule here is a requirement on whoever builds one — a rule in this file may not be cited as a control
that is in place.

---

## 1. Scoring boundary

**The judge may score, one attribute per call (JDG-01, anchoring row):**

- **Required-output completeness** — presence and substance of each element named in the
  `Required output:` cell of the procedure under review, item by item.
- **Named assumptions** — assumptions stated as assumptions, not smuggled in as fact.
- **Rejected alternatives** — alternatives named *and* the reason for rejection given.
- **Mode match** — whether the artifact is the requested mode (Explain / Design / Review /
  Implement) rather than a different, adjacent artifact.

**The judge may NOT score:**

- **Trajectory — which modules were actually read.** That is a fact recoverable from the transcript
  by string matching. Handing a checkable fact to a model converts evidence into opinion, and the
  opinion is then weaker than the grep it replaced. JDG-01 "cannot grade what it cannot solve" and
  the closing rule *verify metadata by code, verify meaning by judge* both forbid it; a judge
  dimension duplicating a deterministic check is wasted cost and an invitation to override.
- **Whether a planted defect was found.** The planted string is known in advance; detection is a
  grep against the artifact. Same rule.
- **Anything with a canonical form** — IDs, hashes, counts, file paths, presence of a literal
  section heading. Deterministic function, always (JDG-01, closing section).
- **Verdicts, readiness, or release fitness.** See section 3.

Boundary in one line: **the judge is for entailment, relevance, coverage and completeness of
meaning; code owns every fact.**

The judge's own output follows the mandatory record order from `evaluation-testing.md` EVA-03:
findings with evidence first, then required-factor coverage and explicit gaps, then per-dimension
scores. A correct score emitted before the findings fails this protocol even if the number is right.

## 2. Cross-family judge, and the dependency the maintainer accepts

The judge must come from a different model family than the model that produced the artifact.
Reason: **self-preference** (JDG-01, self-enhancement row) — measured win-rate uplift on own output
up to ~25% in the source, with self-recognition tracking self-preference linearly. No calibration
performed *inside* one family removes it, because the bias is in the grader that the calibration is
being fit to. JDG-01's mitigation is explicit: never make one model both generator and sole judge on
a decision that carries weight.

**Corollary the maintainer must accept:** the judge becomes a versioned dependency of every number
this layer emits, and its supplier can change it without telling us.

- Record beside the skill content hashes, in the same run record: judge family and version string,
  judge prompt hash, rubric version, scale, per-call attribute, order-swap policy, repeat count K,
  order-disagreement rate, agreement statistic with n (JDG-01 judge card; JDG-02 step 6).
- **A judge change — model version, prompt, or rubric — invalidates comparison with earlier runs.**
  Re-run calibration (section 4) and re-run minimal pairs (JDG-03 step 7) before any new number is
  compared to an old one. Scores across a judge boundary are two readings from two instruments.
- No model name is named here. Family selection is a maintainer decision with cost attached.

## 3. The judge is not a gate

The judge holds **one vote, for reporting and prioritisation.** It does not pass, fail, block, or
release anything.

- **Where a deterministic check exists, the deterministic check wins,** and the judge score for that
  property is not collected at all (JDG-01 closing; EVA-03 "use deterministic checks whenever
  possible"). The Release Gate in `evaluation-testing.md` is composed of hard deterministic gates,
  zero critical policy violations, bounded latency/cost, tested rollback, trace completeness, and a
  named operational owner — a judge score is not one of its terms and cannot override one.
- **Where no deterministic check exists,** the judge's finding is a candidate finding. Disagreement
  between judge and reviewer, between orders, or across repeats **escalates to human adjudication**
  (EVA-03, JDG-03).
- **Publish the residual disagreement rate** alongside every reported score: order-disagreement
  rate, judge-vs-human disagreement rate, and how many items went to adjudication. A score reported
  without its disagreement rate is not reportable under this protocol.
- Agreement with the artifact's author, or with another judge, is neither evidence nor correctness
  (`evaluation-testing.md`, anti-sycophancy gates). Ensembling is unproven cost (JDG-03 step 7).

## 4. Calibration is a precondition, not a nicety

**No judge output may be used to claim anything about the skill until calibration has run**
(JDG-03: the judge is under test first).

1. **Seed set: human-labelled first, sized by the maintainer,** against this rubric, before the judge sees
   them. Labels come from the **exploratory** set, never the frozen regression set — calibrating on
   the gate set fits the judge to the gate (JDG-03 step 5).
2. Build the minimal pairs per criterion — known-good vs known-bad differing only in that property,
   including the absence case and the compliant-abstention case (JDG-03 steps 1–2). Failure to
   separate a pair is a **rubric defect**: fix the rubric, do not score the skill.
3. **Report a chance-corrected agreement number** — Cohen's κ for two raters, Krippendorff's α for
   more or for an ordinal scale — with n. Percent agreement is not acceptable: it can stay high
   while absolute scores diverge by several points (JDG-01 prompt-sensitivity row, JDG-03 step 4).
4. Plainly: **an uncalibrated judge score is a reading from an unknown function.** It is not a weak
   number, it is not a number.

**When agreement is poor,** in cost order (JDG-03 step 6), and none of these is a substitute for the
first bullet:

- Read the judge rationale on the case you are most confident about and look for length, position,
  format and polarity artefacts — a low score on an artifact you have independent reason to believe
  correct implicates the metric first (JDG-03 step 3).
- Repair the rubric: affirmative observable predicates, count formulae, explicit no-deduction
  clauses (JDG-02).
- Reference-guided grading — supply the procedure's `Required output:` cell as the reference.
- Few-shot judge examples (~4x call cost from the longer prompt).
- Fine-tuned lightweight judge — expensive, and the reported gain came from a five-figure label set.
- **If agreement stays poor, stop scoring that criterion and report the gap.** Do not restate a
  poor-agreement score with a caveat attached; a number does not fix the function behind it.

**Stated contradiction, module wins:** JDG-04 step 5 shows a set of this size cannot support a
numeric gate — a 50-case set at s̄ = 0.9 already has CI95 ≈ ±8pp. A calibration seed set, at whatever
size the maintainer sets, is therefore **calibration evidence only**. Nobody may read a gate, a trend, or a system comparison off
it. Sizing an eval set that could support a comparison is JDG-04 step 5 arithmetic and a maintainer
decision.

## 5. Bias controls and their mechanisms

| Control | Mechanism | ID |
|---|---|---|
| Position bias | Score **both orders** for any comparison. A win is counted only when preference holds in **both** orders; otherwise it is a tie. Order-disagreement rate is tracked as judge health and published. | JDG-01, EVA-03 |
| Label grading | Strip from the judge's input: the producing model's identity, the procedure name and ID, any project, employer or product identifier, and any file path. The judge grades the artifact, never the label on it. | JDG-01 self-enhancement, EVA-03 |
| Adjective drift | The rubric anchors every level to an **observable criterion** — a present/absent element, a count, a named item — not to an adjective like "clear" or "thorough". Counting reproduces; rating drifts. | JDG-02 steps 1, 3, 5 |
| Verbosity bias | Normalise or cap artifact length before judging and report a length-controlled score. A completeness gain arriving with a length increase is unproven. | JDG-01 verbosity |
| Anchoring | **One attribute per call.** Attributes scored in one context are not independent evidence and may not be presented as multi-dimensional. | JDG-01 anchoring |
| Non-determinism | Repeat any material score K times; report mean and standard error. Lowering temperature is not the fix — it cuts sampling variance, not bias, and changes the configuration under measurement. | JDG-01, JDG-04 step 4 |
| Compliance penalty | The rubric states explicitly that a stated gap, an abstention, or a refusal-to-score may not reduce a score. | JDG-02 step 2 |
| Prompt drift | The judge prompt and rubric are frozen, versioned artifacts. Any edit is a behavioural change and triggers re-validation. | JDG-01 prompt sensitivity, JDG-02 step 6, JDG-03 step 7 |

## 6. Key and data handling

**Key.** The API key lives in an environment variable, read at call time. It is never written into a
config file, a prompt, a fixture, a report, a run record, or a log — **and never appears truncated
or masked**, because a prefix is still key material and a masked key in a log is a key in a log.
Nothing in this eval package prints, echoes, or asserts on the key's value. A missing key is a
configuration error reported by name, not by value.

**TLS-inspecting proxy.** Behind a TLS-inspecting corporate proxy the HTTP client verifies against
its own bundled roots and fails, because the chain terminates at the corporate gateway. The client
must be pointed at the corporate CA bundle through the standard environment variable for its
runtime — `REQUESTS_CA_BUNDLE` / `SSL_CERT_FILE` for Python clients, `NODE_EXTRA_CA_CERTS` for
Node. The exact error string to expect is:

```
self-signed certificate in certificate chain
```

(the Python surface of the same failure is `certificate verify failed: self-signed certificate in
certificate chain`). **This is a local trust-store misconfiguration, not the API being down and not
a bad key.** Misreading it that way sends people to retry logic, backoff, and key rotation for a
one-variable fix. Do not add retries for it; it is deterministic and will fail identically forever.
The bundle path itself is environment configuration and appears in no file in this repository.

**Data.** Sending an artifact to an external judge API is **publication.** It leaves the machine.
Therefore:

- Every fixture in this eval package is **synthetic**, authored for the eval, and contains nothing
  from any employer, customer, or internal system — no real document text, no internal names,
  no identifiers, no paths.
- Synthetic fixtures inherit the generator's distribution and are contaminated evidence by default;
  record per-case provenance (JDG-04 step 3).
- **Whether to send anything at all to an external judge is the maintainer's decision, not this
  document's.** This protocol describes how it would be done safely if the maintainer decides to;
  it does not authorise it, and it does not implement it.

---

**Ownership.** Maintainer owns: judge family and version selection, calibration agreement bar,
repeat count K, eval-set size and freeze, every threshold, blocking status of every check, and the
decision to send data to an external API. This protocol owns none of them and states none of them.
