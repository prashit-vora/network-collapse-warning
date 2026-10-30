# Validation and results audit

Completed October 30, 2026. All results below are synthetic, model-conditional experiments; no empirical network dataset was used.

## 1. Network comparison

450 deterministic runs: three graph generators × three capacity settings × 50 paired seeds. Initial loads and capacities are identical across topologies for each seed. Capacities are not aligned with graph centrality. Connected random/small-world graphs are obtained by rejection sampling; results apply to that conditioned ensemble.

| Network | Capacity spread | Median collapse step | Median gap after first failure | Collapse in first-failure step |
|---|---:|---:|---:|---:|
| random | 0 | 302.5 | 0 | 50/50 |
| random | 0.2 | 151 | 2 | 24/50 |
| random | 0.3 | 93.5 | 46 | 2/50 |
| small_world | 0 | 302.5 | 0 | 50/50 |
| small_world | 0.2 | 151.5 | 1 | 25/50 |
| small_world | 0.3 | 84.5 | 26 | 11/50 |
| scale_free | 0 | 302.5 | 0 | 50/50 |
| scale_free | 0.2 | 153.5 | 3 | 24/50 |
| scale_free | 0.3 | 94 | 38.5 | 3/50 |

Actual mean degrees are 6.0208 (random, ensemble average), 6 (small-world), and 5.82 (BA). Thus connectivity is approximately matched, not exactly controlled. Do not attribute every difference solely to topology or claim a universally most robust graph family. Capacity heterogeneity brings collapse earlier in these experiments, while often allowing a longer period of damage before collapse. More gradual failure does not mean greater resilience.

## 2. Uncertainty validation

Forecasts use full observed node loads, capacities, graph, and the correct future demand distribution. Observation time is fixed at step 20. Capacity spread is 0.3. Each of 180 test cases has 300 independent forecast continuations and one separate actual future. Model information does not include the actual future demand sequence. Each topology/amplitude group uses 30 independent seeds; the same seeds across groups are paired, so groups are not mutually independent. No run was excluded for early collapse, and none of the evaluated paths was censored at 1,000 steps.

The simple elapsed-time baseline is a topology/amplitude-specific median lifetime estimated using 30 separate training seeds, minus the observation time. It is intentionally information-poor relative to the full-state model. It is a reference, not proof of superiority to other forecasting methods.

| Network | Demand amplitude | Test cases | MAE (steps) | Baseline MAE | 80% interval coverage | 95% Wilson interval for coverage | Mean interval width |
|---|---:|---:|---:|---:|---:|---|---:|
| random | 0.2 | 30 | 0.57 | 23.70 | 100.0% | 88.6–100.0% | 2.53 |
| random | 0.5 | 30 | 2.80 | 23.87 | 90.0% | 74.4–96.5% | 7.13 |
| small_world | 0.2 | 30 | 0.70 | 20.63 | 96.7% | 83.3–99.4% | 2.17 |
| small_world | 0.5 | 30 | 1.77 | 21.23 | 83.3% | 66.4–92.7% | 5.20 |
| scale_free | 0.2 | 30 | 0.80 | 22.53 | 86.7% | 70.3–94.7% | 2.47 |
| scale_free | 0.5 | 30 | 2.33 | 22.57 | 80.0% | 62.7–90.5% | 6.23 |

The intervals are empirical 10th–90th percentile ranges of integer collapse times, using inverted empirical CDF quantiles. Because of discreteness, their probability content can exceed 80%; observed coverage of 100% is not evidence of perfect calibration. Coverage estimates have only 30 cases per group. For example, the low-noise random-network group has 100% observed coverage and a 95% Wilson lower bound above 80%, showing conservative behavior relative to exact nominal coverage. Brier scores at horizons 25 and 50 are saved in summary.json; many probabilities at horizon 25 are near zero, so small Brier scores there alone are weak evidence of forecasting skill.

## 3. Equation and implementation audit

- The load ODE has an exact affine solution between failure events, but does not itself encode redistribution. The jump map is essential.
- The next-event formula determines the next crossing only. Individual node times and network collapse require the full recursive event sequence.
- Continuous crossing-at-capacity and discrete strict overload after full demand steps are different models. Do not conflate their results.
- The new random-demand cumulative-sum event optimization matched the whole-step reference on 30 independently seeded cases across three topologies, comparing collapse time, first failure, largest cascade and final failure count.
- Workload accounting is asserted throughout: active workload plus unserved demand equals initial workload plus injected demand.
- The collapse threshold is 30 failed nodes out of 100, not total network death. Earlier informal descriptions saying every run lost all nodes were too broad.
- Known-state, known-demand deterministic solving is calculation of the model future. Random-demand continuation yields a conditional probability forecast, not prediction of unknown physical dynamics.
- Our first-passage recurrence follows from conditioning on the next independent demand increment. It is not a novel theorem.
- Positive demand accumulates without service or recovery. No restoring equilibrium, critical slowing down, or saddle-node bifurcation has been demonstrated.
- Experiments 1–5 and the new validation use distinct seed schemes. Use each table with its own experiment metadata; do not combine their medians as if they were the same sample.

## Reproduction

Run `python src/final_validation.py` then `python src/plot_validation.py`, or use notebook 06 in Colab. No GPU is needed. The notebook reruns the full validation and may take several minutes. Results can vary slightly with package versions and floating-point threshold boundaries; local versions are recorded in environment.json.

## Figures

- Figure 1, topology_comparison.pdf/png: collapse-time distributions and median first-failure-to-collapse gaps; each topology/capacity group contains 50 runs.
- Figure 2, uncertainty_validation.pdf/png: interval coverage with Wilson confidence bars and mean absolute error against the independent-training baseline.

## Sources and attribution

The local redistribution model is inspired by overload-cascade research, not a reproduction of Motter–Lai shortest-path load dynamics. Graph generators follow established random, Watts–Strogatz and Barabási–Albert constructions implemented in NetworkX. Mathematical first-passage reasoning is standard. References and software acknowledgements are in REFERENCES.md. No claim of a new general theory or validation on real infrastructure is supported.
