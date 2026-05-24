# Experiment Inventory

This file lists the experiments used in the cleaned repository.

## 1. Unified Benchmark

Script:

```text
scripts/run_benchmark.py
```

Output:

```text
experiments/benchmark/yahoo_2026/
```

Purpose:

- compare the project methods on one shared grid
- evaluate draft position sensitivity
- evaluate ADP delta sensitivity
- compute heuristic optimal gaps against ADP-aware ILP
- estimate the cost of ADP availability constraints using Static IP

Methods:

```text
ADP-aware ILP
Static IP
Direct Greedy
Opportunity Cost Greedy
```

Grid:

```text
draft_position = 1..12
delta = -10..10, stride 1
```

Command:

```bash
python scripts/run_benchmark.py \
  --players data/processed/2026_yahoo_data.csv \
  --outdir experiments/benchmark/yahoo_2026 \
  --scoring yahoo \
  --delta-min -10 \
  --delta-max 10 \
  --delta-step 1 \
  --time-limit 60
```

Expected output size:

```text
12 draft positions * 21 delta values * 4 methods = 1008 rows
```

Key outputs:

```text
experiments/benchmark/yahoo_2026/static_IP/results.csv
experiments/benchmark/yahoo_2026/adp_aware_ILP/results.csv
experiments/benchmark/yahoo_2026/heuristic_greedy/results.csv
experiments/benchmark/yahoo_2026/heuristic_opportunity_cost/results.csv
experiments/benchmark/yahoo_2026/*/summary.csv
experiments/benchmark/yahoo_2026/*/draft_result_position6_delta0.csv
experiments/benchmark/yahoo_2026/summary/benchmark_results.csv
experiments/benchmark/yahoo_2026/summary/summary_by_method.csv
experiments/benchmark/yahoo_2026/summary/summary_by_position.csv
experiments/benchmark/yahoo_2026/summary/summary_by_delta.csv
experiments/benchmark/yahoo_2026/summary/draft_result_position6_delta0_all_methods.csv
experiments/benchmark/yahoo_2026/summary/position6_delta0_roster_comparison.md
experiments/benchmark/yahoo_2026/summary/*.png
```

Benchmark directory convention:

```text
experiments/benchmark/yahoo_2026/
├── static_IP/
├── adp_aware_ILP/
├── heuristic_greedy/
├── heuristic_opportunity_cost/
└── summary/
```

Gap definition:

```text
optimal_gap = ADP-aware ILP objective - heuristic objective
optimal_gap_pct = optimal_gap / ADP-aware ILP objective
```

Only heuristic methods use `optimal_gap_pct` as the performance metric.
`Static IP` is a no-ADP upper baseline and should not be evaluated by
optimality gap against ADP-aware ILP. For Static IP, use:

```text
adp_cost = Static IP objective - ADP-aware ILP objective
```

## 2. Shadow Price Analysis

Script:

```text
scripts/run_shadow_price.py
```

Planned output:

```text
experiments/shadow_prices/yahoo_2026/
```

Purpose:

- solve the ADP-aware LP relaxation
- report roster-position dual values
- support positional scarcity interpretation

Fixed setting:

```text
draft_position = 6
delta = 0
```

This is model interpretation, not the main method-comparison benchmark.

Expected outputs:

```text
experiments/shadow_prices/yahoo_2026/shadow_prices.csv
experiments/shadow_prices/yahoo_2026/position_shadow_prices.png
experiments/shadow_prices/yahoo_2026/shadow_price_summary.md
```

## 3. Mock Draft Experiment 1: Same Strategy Environment

Script:

```text
scripts/mock_draft.py
```

Folder:

```text
experiments/mock_draft/experiment_1_same_strategy/
```

Purpose:

- supplemental dynamic draft demonstration
- compare what happens when every team uses the same deterministic strategy

Methods:

```text
ip
direct_greedy
opportunity_cost_greedy
```

Because these strategies are deterministic given the same data, each run uses:

```text
--simulations 1
```

## 4. Mock Draft Experiment 2: Our Strategy Against Opponents

Script:

```text
scripts/mock_draft.py
```

Folder:

```text
experiments/mock_draft/experiment_2_our_vs_opponents/
```

Purpose:

- planned supplemental experiment
- compare our strategy against stochastic `noisy_adp` opponents

Because `noisy_adp` is stochastic, repeated simulations are meaningful here.

Status:

- design only for now
- not a main project result unless explicitly run later

## Historical Or Superseded Outputs

These old split outputs are superseded by the unified benchmark:

```text
results_2026_yahoo_delta_m10_10/
heuristic_results_yahoo/
```

Smoke-test and duplicate outputs should not be kept as final results:

```text
heuristic_results/
mock_results/
mock_results_all_ip/
heuristic_quota_smoke/
heuristic_results_yahoo_quota/
heuristic_results_yahoo_smoke/
heuristic_results_yahoo_smoke_fast/
mock_refactor_smoke/
mock_results_all_ip_test/
mock_results_test/
mock_results_yahoo/
results/
results_refactor_smoke/
```
