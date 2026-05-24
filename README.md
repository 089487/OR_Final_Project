# Fantasy Baseball Draft Optimization

This project models fantasy baseball snake draft decisions as an operations
research problem. The main comparison is between an ADP-aware integer program,
a no-ADP static IP baseline, and two fast deterministic heuristics.

The current project focus is:

- build clean player pools from projection and ADP data,
- solve the optimal ADP-aware roster selection problem with Gurobi,
- compare two heuristics against the ADP-aware optimum,
- use shadow prices to explain roster-slot scarcity.

Mock draft simulation is kept as a supporting experiment, not the main empirical
result.

## Environment

```bash
source ~/myenv/bin/activate
pip install -r requirements.txt
```

Gurobi must be licensed and importable through `gurobipy`.

## Repository Layout

```text
reference/                 original project PDF
scoring/                   Yahoo and FanGraphs scoring tables
data/raw/                  raw projection CSVs
data/adp/                  raw ADP CSVs
data/processed/            model-ready player pools
src/                       shared model, IP, and heuristic code
scripts/                   data and experiment scripts
experiments/benchmark/     main method-comparison outputs
experiments/shadow_prices/ LP-relaxation shadow-price outputs
experiments/mock_draft/    supplemental mock-draft outputs
reports/                   report figures/tables/materials
logs/                      long-run logs
```

## Data Processing

Current processed files:

```text
data/processed/2026_yahoo_data.csv
data/processed/2026_fangraph_data.csv
data/processed/2026_yahoo_data_calibrated.csv
data/processed/2026_fangraph_data_calibrated.csv
```

`calibrated` files use adjusted points to better align with the selected scoring
table. Non-calibrated files keep the direct scoring output.

To rebuild the current 2026 processed files:

```bash
source ~/myenv/bin/activate
python scripts/process_data.py
```

The processed data must contain player name, projected points, ADP, and eligible
positions. The current processing script is written around the 2026
FantasyPros-style input format; for 2021-2024 historical data, either match that
schema or generalize the script output names.

## Main Benchmark

The main benchmark compares four methods:

- `Static IP`: no ADP constraint; a no-ADP upper baseline.
- `ADP-aware ILP`: the primary optimal benchmark under draft availability.
- `Direct Greedy`: each pick takes the highest-points feasible player.
- `Opportunity Cost Greedy`: each pick compares current value against future
  replacement value from ADP windows.

The benchmark grid is:

```text
draft positions = 1..12
ADP delta       = -10..10, stride 1
methods         = 4
```

Yahoo:

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

FanGraphs:

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

Use `tmux` for full benchmark runs:

```bash
tmux new -s yahoo_benchmark
source ~/myenv/bin/activate
python scripts/run_benchmark.py --players data/processed/2026_yahoo_data.csv --outdir experiments/benchmark/yahoo_2026 --scoring yahoo --delta-min -10 --delta-max 10 --delta-step 1 --time-limit 60
```

## Benchmark Output

Each benchmark directory should use this structure:

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

Expected size for one scoring table:

```text
12 draft positions * 21 delta values * 4 methods = 1008 rows
```

`draft_result_position6_delta0.csv` stores the representative roster at
`draft_position=6`, `delta=0`, including selected players, assigned positions,
ADP, and projected points.

Heuristic optimality gap is computed against the ADP-aware ILP:

```text
optimal_gap = (objective_ADP_aware_ILP - objective_heuristic) / objective_ADP_aware_ILP
```

`Static IP` does not use this gap because it solves a different no-ADP problem.
Instead, use:

```text
adp_cost = objective_Static_IP - objective_ADP_aware_ILP
```

## Benchmarking New Data

To benchmark a new season or data source:

1. Put raw projection and ADP files under `data/raw/` and `data/adp/`.
2. Convert them into a processed CSV under `data/processed/`.
3. Name the processed file `data/processed/<year>_<scoring>_data.csv`.
4. Run `scripts/run_benchmark.py` with:

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

5. Check `summary/benchmark_results.csv` and the four method folders.

If the output directory already exists from an older run, remove or archive it
before rerunning so flat-layout files do not mix with the current structured
layout.

## Shadow Price

Shadow price analysis is separate from the integer benchmark. It solves the
ADP-aware LP relaxation at fixed `draft_position=6`, `delta=0`.

Yahoo:

```bash
source ~/myenv/bin/activate
python scripts/run_shadow_price.py \
  --players data/processed/2026_yahoo_data.csv \
  --outdir experiments/shadow_prices/yahoo_2026 \
  --scoring yahoo \
  --draft-position 6 \
  --delta 0
```

FanGraphs:

```bash
source ~/myenv/bin/activate
python scripts/run_shadow_price.py \
  --players data/processed/2026_fangraph_data.csv \
  --outdir experiments/shadow_prices/fangraph_2026 \
  --scoring fangraph \
  --draft-position 6 \
  --delta 0
```

Expected outputs:

```text
experiments/shadow_prices/<scoring>_<year>/shadow_prices.csv
experiments/shadow_prices/<scoring>_<year>/position_shadow_prices.png
experiments/shadow_prices/<scoring>_<year>/shadow_price_summary.md
```

These values are LP relaxation dual values, so they should be used for
interpretation rather than as literal integer marginal values.

## Mock Draft

Mock draft is a supplemental dynamic simulation. It is useful for demonstrating
online draft behavior, but the report should use the benchmark grid above as the
main quantitative comparison.

Example:

```bash
python scripts/mock_draft.py \
  --players data/processed/2026_yahoo_data.csv \
  --outdir experiments/mock_draft/experiment_1_same_strategy/all_opportunity_cost_greedy \
  --simulations 1 \
  --draft-position 1 \
  --our-method opportunity_cost_greedy \
  --opponent-method opportunity_cost_greedy
```

Supported methods:

```text
ip
direct_greedy
opportunity_cost_greedy
noisy_adp
```

## Key Documentation

```text
project_plan.md  project direction and experiment priorities
modeling.md      primal/dual model and shadow-price explanation
expr.md          experiment inventory and output conventions
data_source.md   data-source notes
```
