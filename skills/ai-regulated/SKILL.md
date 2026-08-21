---
name: ai-regulated
description: Design or review AI in a regulated setting — MLR and promotional-content review, audit trails, traceability, validation evidence, official records, provenance of a generated claim, human-in-the-loop approval and its accountability, kill switches, and the non-AI alternative. Use whenever an output could become a regulated record or a decision affects a person. Runs in its own context.
context: fork
agent: ai-engineer
background: false
effort: max
---

Load these two:

- [regulated-domain-controls.md](../ai-engineer/references/regulated-domain-controls.md) —
  REG-01…05: the regime, audit trail, validation, official records
- [completeness-provenance.md](../ai-engineer/references/completeness-provenance.md) — REV-01,
  SRC-01, ASM-01: evidence matrix, claim ledger, guarantee-assumption audit

Add [fraud-model-risk-guardrails.md](../ai-engineer/references/fraud-model-risk-guardrails.md)
(FRD-03/04) **only** if the system could produce an adverse action about a person. Promotional content
review is not that; a decision denying someone something is.

Add [security-governance.md](../ai-engineer/references/security-governance.md) when the question is a
trust boundary or an authority to act, not a record-keeping one.

## Two rules that outrank a clean design

**Regulated text is retrieved, never written.** Approved claims and safety information exist as
records with identities. A generator that composes them is unshippable regardless of output quality,
because there is nothing to audit the string against. The authoritative identity is the store's own
id, not our text and not a hash of our text.

**A gate that runs before the last author certifies nothing.** If any step downstream of the check
still composes, reorders or substitutes content, the check certified an artefact that is not the
delivered one. Establish who the last author is before deciding where the gate sits.

## What an audit trail has to survive

Not "we logged it". A traceability obligation is met when someone can take a delivered artefact and
recover, per element: which approved record it came from, which version of the rule set judged it,
who or what approved it, and when. Version code, prompts, models, data, indexes, policies and eval
sets **together** — a trace that records the output but not the rule-set version cannot answer
whether the decision was correct at the time.

## Where these designs usually fail

- **A control the checked artefact declares for itself.** A payload asserting its own exemption, a
  flag the generator sets, a scope derived from data the same actor supplied. If the thing under
  inspection can widen its own permission, the control is decoration. Derive scope from outside.
- **An accountable human named as a role rather than a person**, with no defined moment of decision
  and no appeal path. A model may propose; it may never grant itself authority.
- **A deterministic check assumed where none exists.** Before designing against a rule, verify the
  rule is written down and machine-readable. A large fraction of real standards delegate the
  judgement to a named human committee — that is an input under change control, not something to
  compute, and inventing a formula from approved examples is how a plausible-but-wrong rule ships.
- **The non-AI alternative never stated.** Regulated assessments ask for it. So does a reviewer who
  wants to know what happens when the system is switched off.

## What to return

The obligation, what evidence discharges it, who owns each piece, the kill switch, the non-AI
fallback, and — stated explicitly — what the design **cannot** catch and therefore stays a human
responsibility. Assert the blind spot as a blind spot so that closing it silently is impossible.

Never decide a regulatory tolerance. Name the function that owns it and leave it unset.
