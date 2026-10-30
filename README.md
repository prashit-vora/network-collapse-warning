# Network Collapse Warning

**Deterministic and probabilistic time-to-collapse in load-redistribution networks.**

A mathematical course project: define network dynamics, solve deterministic failure events, and calculate distributions of remaining collapse time under uncertain demand. All data are synthetic. This is an abstract persistent-workload model, not a physical power-grid or Internet traffic simulator.

## Model

Start with 100 nodes, mean degree approximately six, capacities totaling 1,000 workload units, and initial loads between four and seven. External demand is shared equally among active nodes. A node fails when its load strictly exceeds capacity after a complete demand step. Its entire load is distributed equally among neighbors surviving that synchronous failure round. Further overloads trigger new rounds before additional external demand arrives. Nodes do not recover; the graph does not grow or rewire. Load with no surviving recipient is recorded as unserved demand.

**Collapse means at least 30 of the original 100 nodes have failed**, not necessarily that every node has failed. Workload conservation is checked throughout.

Between failure events, the continuous counterpart has dL_i/dt = D/n_active and an affine solution. The next crossing occurs after n_active × minimum spare capacity / D. Cascades require a separate jump rule. The continuous model fails at upward capacity crossing; it is distinct from the discrete strict-overload model. The original discrete model can skip quiet steps using a floor-plus-one event formula. Summing event intervals gives node failure and threshold-collapse times for a fully known deterministic model.

For random demand, independent increments are uniform on [1−a, 1+a], with mean one. A first-passage recurrence defines the remaining-time distribution; independent Monte Carlo continuations approximate it without seeing the actual future. There is no trained machine-learning model and no demonstrated critical slowing down.

## Colab notebooks

Open a notebook and select **Runtime → Run all**. CPU is sufficient. Dependencies are normally included in Colab; no local installation is required. Close unused runtimes to avoid session limits. Save or download temporary CSVs before terminating a runtime.

| Notebook | Purpose |
|---|---|
| [01: baseline](https://colab.research.google.com/github/prashit-vora/network-collapse-warning/blob/main/notebooks/01_baseline_simulation.ipynb) | Rules, hand-checked examples, plots and optional animation |
| [02: repeated runs](https://colab.research.google.com/github/prashit-vora/network-collapse-warning/blob/main/notebooks/02_repeated_baseline_experiment.ipynb) | 50 random-network seeds |
| [03: capacity variation](https://colab.research.google.com/github/prashit-vora/network-collapse-warning/blob/main/notebooks/03_capacity_variation_experiment.ipynb) | 150 paired capacity experiments |
| [04: solved equations](https://colab.research.google.com/github/prashit-vora/network-collapse-warning/blob/main/notebooks/04_solved_deterministic_model.ipynb) | Derived continuous and discrete event equations; 150 discrete collapse-time checks |
| [05: random demand](https://colab.research.google.com/github/prashit-vora/network-collapse-warning/blob/main/notebooks/05_random_demand_equations.ipynb) | First-passage distribution and conditional forecast example |
| [06: final validation](https://colab.research.google.com/github/prashit-vora/network-collapse-warning/blob/main/notebooks/06_final_validation.ipynb) | 450 topology/capacity runs, 180 independent-future forecast checks, figures and CSVs |

Animation output can exceed the Colab MCP message-size limit. Run that optional cell in Colab itself; notebook 06 has no animation.

## Verified findings

- Across all three graph families and 50 paired seeds, equal capacities produced threshold collapse in the first-failure step in every tested run. This does not imply every node failed.
- Capacity variation generally brought collapse earlier and often created a period of damage before collapse. In the larger-variation setting, median first-failure-to-collapse gaps were 46 steps (random), 26 (small-world), and 38.5 (BA). These are finite-sample, model-specific results.
- At step 20, full-state random-demand forecasts had mean absolute errors of 0.57–2.80 steps across six topology/noise groups, compared with 20.63–23.87 steps for an independent-training median-lifetime baseline. The full-state method has substantially more information than this simple baseline.
- Nominal 80% integer prediction intervals covered 80–100% of independent actual futures across groups of 30 cases. Some intervals are conservative; finite sample confidence intervals are provided. This is simulation-internal assessment under the correct demand law, not real-world calibration or proof of exact 80% coverage.
- The cumulative-demand event optimization matched the whole-step reference in 30 independently seeded random-demand cases across all three topologies. Workload accounting is checked in all experiment paths.

See the [full results and limitations audit](results/validation/VALIDATION_AUDIT.md) before using these numbers. Earlier notebooks use different seed schemes from the final validation; their medians must not be mixed as if they were one dataset.

## Results and reproduction

Committed results include raw CSVs, numerical summaries, execution metadata, and PNG/PDF figures under [`results/validation/`](results/validation/). No external dataset is required.

To reproduce locally in an existing environment with the required libraries:

```bash
python src/final_validation.py
python src/plot_validation.py
```

Or run self-contained notebook 06 in Colab. It embeds the same analysis and plotting source and takes several minutes, depending on runtime speed. The script hash and local package versions are recorded in `environment.json`.

## Parameters, numerical settings and limits

Model parameters: node count; graph generator/connectivity; capacities and spread; initial loads; demand mean and amplitude; collapse fraction. Numerical settings: independent seeds, maximum horizon, number of forecast paths, continuous crossing tolerance, observation time. Actual collapse time is an outcome, not a hyperparameter.

NetworkX generators: connected G(n,p), p=6/99; connected Watts–Strogatz, k=6 and rewiring probability 0.1; Barabási–Albert, m=3. BA grows during initial generation only. Actual mean degree is approximately matched (6.0208, 6, 5.82), so topology effects are not perfectly isolated. Finite BA graphs are not empirical evidence of a power-law degree distribution.

Forecast validation currently uses only observation step 20, capacity spread 0.3, uniform independent demand, correct model parameters and full state. It does not establish performance at every time, with partial observations, under correlated demand or under model error. The persistent-load assumption omits service, repair and protective controls. No universal topology ranking or novel general collapse theorem is claimed.

## Sources and final report

[References and software attribution](REFERENCES.md) distinguish published background from our specific modeling choices. Development used OpenAI Codex/ChatGPT assistance; the group must review and understand the analysis and follow its course's requirements.

The course requires an IEEE two-column LaTeX report, at most six pages including references, submitted as PDF by October 30, 2026. The exact supplied checklist is saved in [REPORT_REQUIREMENTS.md](REPORT_REQUIREMENTS.md). The final report PDF has not been authored or submitted as part of the validation task.

## Additional failure-progression figure

[Open notebook 07 in Colab](https://colab.research.google.com/github/prashit-vora/network-collapse-warning/blob/main/notebooks/07_random_failure_progression.ipynb). It shows 50 random-demand trajectories continued beyond the 30-node threshold until complete failure. The ensemble mean and an explicit early-damage zoom clarify small failures before major cascades. Individual paths remain stepped; no smoothing or favorable-seed selection is used. Data and figures are in results/validation/random_demand_failure_*; reproduce with `python src/plot_failure_progression.py`.
