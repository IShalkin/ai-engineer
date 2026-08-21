# Foundation Models and Algorithm Selection

## ALG-01 — Formalize Before Selecting AI

**Trigger:** a problem is described as “use AI” or “build an agent.”

Describe:

- state/observations and whether they are fully observable;
- actions/outputs and constraints;
- objective, utility, or loss;
- uncertainty and data-generating process;
- horizon: one-shot, sequential, adversarial, or multi-agent;
- ground-truth/evaluation availability;
- computational and operational limits.

Create a deterministic, rules, search, statistical, or manual baseline. Use an LLM only for parts whose semantic/generalization benefit exceeds its uncertainty and control cost.

## ALG-02 — Method Router

| Problem structure | First methods to consider | Key evaluation |
|---|---|---|
| Known state and goal, enumerable actions | graph/state-space search, heuristic search | completeness, optimality, nodes/time/memory |
| Optimization with local structure | local search, evolutionary methods | solution quality, robustness, compute |
| Variables with hard constraints | CSP, propagation, backtracking | validity, solve time, scalability |
| Adversarial sequential choice | minimax/alpha-beta, game-theoretic methods | exploitability, win/utility, compute |
| Logical facts and rules | knowledge representation and inference | soundness, completeness, maintainability |
| Ordered actions with preconditions/effects | planning, scheduling | plan validity, cost, robustness |
| Uncertain variables | probabilistic models/Bayesian inference | calibration, likelihood, decision utility |
| Temporal hidden state | HMM/state-space/sequential inference | predictive accuracy, filtering latency |
| Predict from examples | supervised/unsupervised/deep learning | generalization, calibration, robustness |
| Learn actions from reward | reinforcement learning | return, sample efficiency, safety |
| Open-ended language/vision generation | foundation model with constraints/tools | task success, grounding, safety, cost |

Hybrid systems are normal: deterministic orchestration and policy around learned perception or judgment. Select the simplest method whose assumptions match the problem, then test those assumptions.

## Failure Signals

Using an agent for a fixed algorithm, optimizing an undefined objective, no baseline, treating fluent output as calibrated probability, ignoring partial observability, applying RL without a safe environment/reward, and selecting a model before defining evaluation.
