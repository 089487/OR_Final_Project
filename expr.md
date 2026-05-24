# Experiment Inventory

This file records the experiments that should be reported and the output
structure expected by future reruns.

## 1. Main Benchmark

Purpose: compare optimization and heuristic draft strategies across draft
positions and ADP tolerance values.

Methods:

- `Static IP`: no-ADP integer-program baseline.
- `ADP-aware ILP`: integer program with snake-draft availability.
- `Direct Greedy`: highest-points feasible player at each pick.
- `Opportunity Cost Greedy`: largest current advantage over future replacement
  value.

Grid:

```text
draft_position = 1..12
delta = -10..10, stride 1
scoring = yahoo, fangraph
```

Yahoo command:

```bash
source ~/myenv/bin/activate
python scripts/run_benchmark.py \
  --players data/processed/2026_yahoo_data.csv \
  --outdir experiments/benchmark/yahoo_2026 \
  --scoring yahoo \
  --delta-min -10 \
  --delta-max 10 \
  --delta-step 1 \
  --time-limit 60
```

FanGraphs command:

```bash
source ~/myenv/bin/activate
python scripts/run_benchmark.py \
  --players data/processed/2026_fangraph_data.csv \
  --outdir experiments/benchmark/fangraph_2026 \
  --scoring fangraph \
  --delta-min -10 \
  --delta-max 10 \
  --delta-step 1 \
  --time-limit 60
```

Use `tmux` for full benchmark runs.

Expected output:

```text
experiments/benchmark/<scoring>_<year>/
  static_IP/
    results.csv
    summary.csv
    draft_result_position6_delta0.csv
  adp_aware_ILP/
    results.csv
    summary.csv
    draft_result_position6_delta0.csv
  heuristic_greedy/
    results.csv
    summary.csv
    draft_result_position6_delta0.csv
  heuristic_opportunity_cost/
    results.csv
    summary.csv
    draft_result_position6_delta0.csv
  summary/
    benchmark_results.csv
    summary_by_method.csv
    summary_by_position.csv
    summary_by_delta.csv
    draft_result_position6_delta0_all_methods.csv
    position6_delta0_roster_comparison.md
    method_comparison.png
    objective_by_position_delta.png
    optimal_gap_by_position_delta.png
    adp_cost_by_position_delta.png
```

Expected output size for one scoring table:

```text
12 draft positions * 21 deltas * 4 methods = 1008 rows
```

The representative draft output fixes `draft_position=6`, `delta=0` and records
the selected roster for each algorithm.

## 2. Gap and ADP Cost Definitions

Heuristic optimality gap is measured against the ADP-aware ILP:

```text
optimal_gap = (objective_ADP_aware_ILP - objective_heuristic) / objective_ADP_aware_ILP
```

`Static IP` is a no-ADP upper baseline and should not receive this heuristic
optimality gap. Its diagnostic is:

```text
adp_cost = objective_Static_IP - objective_ADP_aware_ILP
```

This separates two questions:

- how much value is lost because draft availability matters;
- how close each heuristic is to the ADP-aware optimum.

## 3. Shadow Price Analysis

Purpose: explain roster-slot marginal values from the LP relaxation of the
ADP-aware model.

Fixed scenario:

```text
draft_position = 6
delta = 0
```

Yahoo command:

```bash
source ~/myenv/bin/activate
python scripts/run_shadow_price.py \
  --players data/processed/2026_yahoo_data.csv \
  --outdir experiments/shadow_prices/yahoo_2026 \
  --scoring yahoo \
  --draft-position 6 \
  --delta 0
```

FanGraphs command:

```bash
source ~/myenv/bin/activate
python scripts/run_shadow_price.py \
  --players data/processed/2026_fangraph_data.csv \
  --outdir experiments/shadow_prices/fangraph_2026 \
  --scoring fangraph \
  --draft-position 6 \
  --delta 0
```

Expected output:

```text
experiments/shadow_prices/<scoring>_<year>/
  shadow_prices.csv
  position_shadow_prices.png
  shadow_price_summary.md
```

Interpretation note: these are LP relaxation dual values, not integer-program
shadow prices. They should be reported separately from benchmark optimality
gaps.

## 4. Benchmarking New Data

Process for a new season or scoring source:

1. Collect raw projection and ADP files under `data/raw/` and `data/adp/`.
2. Convert them into a processed player pool under `data/processed/`.
3. Confirm the processed file contains player name, projected points, ADP, and
   eligible positions.
4. Run `scripts/run_benchmark.py` with a new output directory:

```bash
python scripts/run_benchmark.py \
  --players data/processed/<year>_<scoring>_data.csv \
  --outdir experiments/benchmark/<scoring>_<year> \
  --scoring <scoring> \
  --delta-min -10 \
  --delta-max 10 \
  --delta-step 1 \
  --time-limit 60
```

5. Run shadow price analysis for the same processed file if the report needs
   marginal roster-slot interpretation.

If a benchmark directory already exists, remove or archive it before rerunning.
This avoids mixing old flat-output files with the current structured layout.

## 5. Supplemental Mock Draft

Mock draft simulation is supplementary. It is useful for discussing how a
strategy behaves when all teams are drafting from the same player pool, but it
is not the central benchmark for the final project.

Existing scripts:

```text
scripts/mock_draft.py
scripts/evaluate_heuristics.py
```

Recommended report usage: mention mock draft as a realism check while keeping
the main quantitative comparison on the benchmark grid above.

## 6. Historical Or Superseded Outputs

Older outputs that used a flat benchmark layout or regression-based ADP
experiments should not be treated as final results. The final benchmark layout
is the structured method-folder layout documented above.
