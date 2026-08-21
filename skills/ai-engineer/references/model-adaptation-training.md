# Model Adaptation and Training

## MOD-01 — Adaptation Ladder

**Trigger:** the current system misses a required capability, behavior, format, domain, or cost target.

Locate the causal gap and try the cheapest responsible layer:

1. prompt/schema for interface and explicit instructions;
2. context/RAG for external, private, or changing knowledge;
3. tools/workflow/harness for action, deterministic rules, state, and verification;
4. supervised fine-tuning/PEFT for stable learned behavior or repeated format/task patterns;
5. preference/RL methods for reliably judgeable trade-offs or verifiable trajectory outcomes;
6. pretraining/model architecture only when the missing capability cannot be supplied above.

**Gate:** frozen evaluation shows the gap remains and the proposed layer can plausibly generalize. Record rejected cheaper layers.

## MOD-02 — Dataset Engineering and Synthetic Evolution

1. Define behavior, population, label/rubric, rights, sensitive-data policy, and held-out tests.
2. Collect representative successes, failures, corrections, refusals, and recoveries with provenance.
3. Deduplicate by semantic/entity leakage; split by user/time/source as deployment requires.
4. For synthetic data or Evol-Instruct, generate candidates by explicit transformations/constraints, but use a separate acceptance pipeline with deterministic checks, calibrated judges, diversity controls, and real anchors.
5. Inspect distribution, contamination, conflict, and subgroup coverage.
6. Version data, generator, filters, annotator/judge, and acceptance decisions.

Teacher output is proposed data, not truth. Keep release tests hidden from data generation.

## MOD-03 — SFT, PEFT, and LoRA

Use SFT for stable demonstrations. Use PEFT/LoRA when memory, storage, multi-tenant adapters, or rapid specialization favor small trainable deltas.

1. establish base-model and prompt/RAG baselines;
2. choose full fine-tuning vs adapter from behavior gap and serving constraints;
3. tune rank/target modules/hyperparameters from experiments, not universal ranges;
4. track base model, tokenizer, dataset, adapter, license, and compatibility;
5. evaluate target behavior, general capability, safety, calibration, and latency/cost;
6. canary with reversible adapter/model selection.

Do not train factual freshness into parameters when governed retrieval is required.

## MOD-04 — Preference Optimization and Reinforcement Learning

Use DPO or related preference optimization when ranked pairs express a stable, reviewable preference. Use RLHF when a learned reward and human preference process is justified. Use RLVR/tool-use RL when an environment supplies difficult-to-game verifiable outcomes.

1. define desired behavior and non-negotiable constraints outside the reward;
2. collect diverse comparisons/trajectories and measure annotator disagreement;
3. prevent reward/evaluator leakage and shortcut signals;
4. test reward hacking, mode collapse, sycophancy, unsafe exploration, and capability regression;
5. compare against SFT and harness changes;
6. evaluate on held-out tasks and deploy progressively.

Never let the trained policy modify or solely judge its own reward, authorization boundary, or release gate.

## Failure Signals

Fine-tuning to fix missing context, LoRA chosen from a remembered rank range, synthetic data accepted by its generator, preference labels without disagreement analysis, RL without a safe/verifiable environment, and offline score gains that fail application outcomes.
