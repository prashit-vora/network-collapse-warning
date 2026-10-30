# Network Collapse Warning

**Early warning signals of cascading failures in networks under increasing load.**

## Research question

Can measurements at each settled simulation step estimate **how many steps remain until network collapse**, with calibrated uncertainty? Do those estimates generalize across random, small-world, and scale-free networks?

The primary prediction target is a distribution over remaining collapse time, summarized by an estimated remaining time and probabilities for time ranges or cumulative probabilities such as collapse within 5 or 10 steps. A fixed-horizon binary alarm is only an optional summary, not the main task. Predictions are conditional on the specified future demand process. For completed collapse trajectories, the observed remaining time at step t is `collapse_step - t`; this outcome must never be supplied as an input feature. Collapse time is an outcome, not a hyperparameter.

This is a simulation research project. No prediction performance has been demonstrated yet.

## What the project does

We model an abstract network of connected units handling transferable workload. Each node has a load and a fixed capacity. Demand increases over time. When a node becomes overloaded, it fails and passes its workload to surviving neighbors. This can overload those neighbors and trigger a chain reaction: a **cascading failure**.

We measure stress before collapse, evaluate early warning rules on independent simulations, and compare network structures. This is an abstract workload model, not a detailed physical power-grid or Internet routing model.

## What makes it dynamic?

The initial node set and connections are fixed: no new nodes join, no new edges are added, and nodes do not recover in the baseline model. Loads change over time, nodes fail, and the active network shrinks. These evolving states and failure cascades are the dynamic process. Animation will make that process visible; it is not the process itself.

## Proposed baseline assumptions

These are explicit starting choices, subject to refinement after pilot experiments.

- Use a simple, undirected, initially connected graph.
- Node capacity is fixed throughout a run. Start with equal capacities and heterogeneous initial loads so nodes do not all reach capacity together.
- Load represents persistent demand: it accumulates rather than being processed and cleared at every step.
- At each external time step, add a fixed total increment of demand, split equally among currently active nodes.
- A node fails only when its load is strictly greater than capacity.
- Resolve overloads in synchronous rounds: identify all overloaded nodes, remove them together, and divide each one's full load equally among neighbors that survive that round.
- Newly overloaded recipients fail in the next cascade round. No additional external demand arrives until the cascade settles.
- If a failed node has no surviving neighbors, record its workload as unserved demand. Never silently discard it.
- Failed nodes and their incident edges remain inactive for the rest of the run.
- Track workload accounting: active load plus cumulative unserved demand equals initial load plus all injected demand, within numerical tolerance.
- There is no intervention, recovery, rerouting beyond direct neighbors, or incoming-node growth in the baseline.

## Simulation procedure

1. Generate a graph and assign a random seed. If disconnected, regenerate the entire graph and record this conditioning; do not take its largest component and change the node count.
2. Set capacities and sample initial node loads below capacity.
3. Record the initial state.
4. Add the external demand increment to surviving nodes.
5. Resolve synchronous failure and redistribution rounds until all remaining nodes are within capacity, or none survive.
6. Record loads, failed-node fraction, unserved demand, cascade size, and warning indicators.
7. Record the first settled external step at which the collapse threshold is crossed. Keep within-step rounds for visualizing the cascade.
8. Repeat until collapse or the maximum number of steps. A run reaching the limit without collapse remains a non-collapse/censored run; do not force a collapse label.
9. Repeat over independent seeds, then compare network types and parameter settings.

Warnings made from a settled state at time t must concern a future step. An alarm first generated after the collapse threshold is crossed is not an early warning.

## Starting simulation parameters

Values below are pilot settings, not established findings or optimal choices. One time step is a simulation unit, not a real-world second.

| Parameter | Meaning | Pilot value |
| --- | --- | --- |
| N | Original node count | 100 |
| Mean degree | Target average number of neighbors | Approximately 6 |
| C | Capacity of each node | 10 workload units |
| Initial utilization | Initial load divided by capacity, sampled per node | Uniform between 0.4 and 0.7 |
| Delta D | Total new workload added per external step | 1 workload unit |
| q | Collapse threshold: cumulative failed nodes / original N | 0.30 |
| T_max | Maximum external steps per run | 1,000 |
| Seed | Reproducible random generation | Recorded per run |
| Replicates | Independent runs per experimental setting | 20 for pilot debugging; choose final count using uncertainty estimates |

With A active nodes, each receives Delta D / A new workload units per step. Using a fixed total increment keeps the demand schedule comparable across runs. Once we vary N, scale Delta D with N to keep per-original-node stress increments comparable.

### Network-generation parameters

| Network | Generator and pilot settings |
| --- | --- |
| Random | Erdos-Renyi with p = 6 / (N - 1) |
| Small-world | Watts-Strogatz with k = 6 and rewiring probability beta = 0.1 |
| Scale-free comparison | Barabasi-Albert with m = 3 edges per arriving node during initial graph generation |

Barabasi-Albert grows the graph during setup only; there are no arriving nodes during the failure simulation. These choices give similar, not identical, mean degree. Record actual node count, edge count, and mean degree for every run. The baseline comparison holds N and approximate connectivity constant; any connectivity conditioning must be reported.

## What counts as collapse?

For the pilot, collapse occurs when at least 30% of the original nodes have failed. For N = 100, this means 30 failed nodes. This is an operational definition, not a universal law or a claim that all surviving nodes stop functioning.

Check sensitivity to other thresholds, such as 20%, 40%, and 50%. Also track the largest active connected component and fraction of demand unserved: node failure count alone does not fully describe loss of function.

## Candidate warning indicators

- **Remaining spare capacity:** sum of capacity minus load across active nodes, also normalized by original total capacity for comparisons.
- **Near-capacity fraction:** fraction of active nodes with utilization at or above a provisional threshold of 0.9. Also log active node count so this fraction has context.
- **Load concentration:** a defined concentration statistic, such as the Gini coefficient of active loads. State the exact implementation and edge-case conventions before evaluation.
- **Disturbance response:** failures induced by a standardized small workload shock applied to a copy of the current state. The main simulation must remain unchanged. For a pilot, add 1 workload unit to a randomly chosen active node, repeat over 10 sampled targets, and report mean induced failures / active nodes. This is an active stress test with extra computation, not a purely passive measurement.

Measure settled, pre-collapse states only. Record initial indicators before the first demand increment. Handle an empty active set as a terminal state rather than dividing by zero.

## Warning settings versus simulation parameters

Simulation settings define the system: graph size/connectivity, capacities, initial loads, demand increments, and collapse threshold. Prediction hyperparameters configure the future remaining-time model, such as model complexity or history-window length. Optional alarm summaries additionally use indicator thresholds, a reporting horizon, and alarm persistence. The realized collapse step is an outcome, never a setting.

Start with simple remaining-time baselines before complex models; interpretable threshold alarms can be supplementary comparisons. A pilot forecast horizon could be H = 10 future external steps, and alarm persistence could start at one observation. These are provisional choices. If rolling statistics are later added, window length becomes another hyperparameter.

Fit indicator thresholds using training runs only. Use validation runs for tuning; reserve independent test runs for final evaluation. Split entire simulation runs, not individual time steps, to prevent leakage. Report sensitivity to H and stress rate because warning lead time depends on both.

## Remaining-time prediction and evaluation

At every settled pre-collapse state, use only information available at that time to predict a probability distribution over future collapse steps. Summarize it with a point estimate (for example, a median), uncertainty intervals, and probabilities for chosen time ranges. Evaluate remaining-time errors against simple elapsed-time and demand baselines, assess interval coverage and probability calibration, and split by complete simulation runs. Runs without observed collapse require censoring-aware treatment rather than invented collapse times. Keep the provisional 30% failure definition unless explicitly revised.

The following alarm metrics are supplementary views of the time distribution:


- Warning lead time: collapse step minus first qualifying warning step; also report demand increase between warning and collapse.
- Missed-collapse rate: fraction of collapse runs without an alarm in the defined pre-collapse forecast window.
- False-alarm rate: define an alarm event and its denominator explicitly; an alarm is false when collapse does not occur within H future steps. Do not label alarms near a truncated run's end without enough follow-up.
- Demand at collapse and variation across seeds.
- Compare a shared detector across topologies with topology-specific thresholds, using held-out runs.
- Report uncertainty across independent runs and compare against a simple demand-only warning baseline. Since demand grows monotonically, a useful detector should add information beyond elapsed time or demand alone.

A long lead time is not automatically a correct H-step prediction: distinguish general stress warnings from alarms claiming collapse within H steps.

## Implementation roadmap

1. Document the model and assumptions (this README).
2. Build one random-network simulation in Python using NetworkX and NumPy.
3. Check failure rules, synchronous redistribution, workload accounting, and reproducibility on small hand-calculated examples.
4. Plot demand, failed-node count, spare capacity, and network state using Matplotlib.
5. Add warning indicators and independent evaluation.
6. Add small-world and scale-free comparisons and parameter sensitivity experiments.
7. Add an animated demonstration showing load changes and cascading failures.

**First milestone:** run one simulation and produce a graph of increasing demand triggering a cascade, with a trace explaining why each node failed.

## Planned structure

```text
network-collapse-warning/
├── README.md
├── requirements.txt
├── .gitignore
├── src/
│   └── simulation.py
├── experiments/
└── results/
```

## Run in Google Colab

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/prashit-vora/network-collapse-warning/blob/main/notebooks/01_baseline_simulation.ipynb)

Open the notebook using the badge and choose **Runtime → Run all**. A CPU runtime is enough. No local installation is needed. Colab normally includes the required libraries; the notebook explains what to do if an import is missing.

The first implementation is in [`notebooks/01_baseline_simulation.ipynb`](notebooks/01_baseline_simulation.ipynb). It contains hand-calculated cascade checks, a reproducible 100-node simulation, workload accounting checks, plots with node counts and percentages, a round-by-round cascade view, and an HTML animation. Core simulation checks passed locally, including 20 seeded runs. The updated charts were also executed through Colab MCP and visually checked. Time-to-collapse prediction and topology comparison remain future work.

The notebook also explains a future continuous-time extension: differential equations evolve loads between discrete failure and redistribution events (a hybrid dynamical system).

## Experiment 2: 50 independent seeded runs

[Open the self-contained experiment in Colab](https://colab.research.google.com/github/prashit-vora/network-collapse-warning/blob/main/notebooks/02_repeated_baseline_experiment.ipynb) and select **Runtime → Run all**. This version skips the animation.

The final section of the notebook repeats the unchanged baseline with seeds 1000–1049. It reports collapse timing, first failure, largest cascade, and stress before collapse. It plots collapse-step distribution, failure trajectories for the first ten seeds, and a retrospective near-overload indicator aligned by steps remaining. CSV summaries and full settled histories are saved under `experiment_results/` in the runtime.

Run the baseline definition cells first, then the last two experiment code cells. The animation is optional and can be skipped. This experiment measures joint variability in random graph structure and initial loads; it does not yet fit a remaining-time predictor. The across-run shaded band is not a calibrated prediction interval.

## Experiment 3: capacity variation

[Open the capacity experiment in Colab](https://colab.research.google.com/github/prashit-vora/network-collapse-warning/blob/main/notebooks/03_capacity_variation_experiment.ipynb) and select **Runtime → Run all**.

Compare equal capacities with mild (8–12) and larger (7–13) variation across 50 paired seeds per setting. Total capacity stays exactly 1,000 units; each paired seed keeps graph structure and initial loads identical. The main outcome is the number of external steps from first failure to collapse. The 7–13 bounds ensure the shared initial loads (4–7) remain below capacity. The notebook checks pairing and workload accounting, creates three comparison plots, and exports a 150-run CSV. It does not assume heterogeneity produces gradual failure.

## Experiment 4: derived deterministic event solution

[Open the solved-model notebook in Colab](https://colab.research.google.com/github/prashit-vora/network-collapse-warning/blob/main/notebooks/04_solved_deterministic_model.ipynb).

Derives and solves the load ODE between failures, specifies synchronous redistribution jumps, and calculates collapse by advancing from one failure event to the next. A separate integer event formula preserves the original strict-overload, whole-step convention. That discrete solver matched original collapse steps on 150 cases (50 seeds across three capacity settings). The continuous capacity-crossing model uses a different boundary convention and is not claimed to be identical. For seed 1000 with capacity spread 0.3, discrete collapse is step 65 and continuous collapse time is approximately 64.836971. This is a deterministic full-state calculation, not a trained or probabilistic predictor. Topology comparison remains outstanding.

## Experiment 5: random demand and a first-passage equation

[Open in Colab](https://colab.research.google.com/github/prashit-vora/network-collapse-warning/blob/main/notebooks/05_random_demand_equations.ipynb). Uses independent uniform demand increments with mean one, the same initial present state for all variability settings, the existing strict-overload redistribution rule, and 300 independent future paths per setting. Derives an exact first-passage distribution recurrence and estimates it with Monte Carlo. Includes horizon probabilities, remaining-time quantiles, censoring handling, and workload checks. Zero variability must match the deterministic simulator. Full calibration and topology generalization remain outstanding; this is not yet the final validated project.
