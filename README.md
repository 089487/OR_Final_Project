# Fantasy Baseball Draft Optimization

This project implements an integer-programming approach to fantasy baseball
snake-draft optimization, based on the proposal in
`reference/OR_final_project.pdf`.

The main experiment compares:

- `ADP-aware ILP`
- `Static IP`
- `Direct Greedy`
- `Opportunity Cost Greedy`

across draft positions and ADP uncertainty values.

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
data/raw/2026/             raw FantasyPros projection CSVs
data/adp/                  ADP CSVs
data/processed/            model-ready player data
src/                       shared model, IP, and heuristic code
scripts/                   executable experiment/data scripts
experiments/benchmark/     unified benchmark outputs
experiments/shadow_prices/ shadow-price and scoring-system outputs
experiments/mock_draft/    supplemental mock-draft experiments
reports/                   report figures/tables/materials
logs/                      long-run logs
```

## Data Processing

Build the processed 2026 Yahoo and FanGraphs data:

```bash
python scripts/process_data.py
```

This writes:

```text
data/processed/2026_yahoo_data.csv
data/processed/2026_fangraph_data.csv
```

The processed data must contain:

```text
season
player
projected_points
adp
eligible_positions
```

## Main Benchmark

Run the unified Yahoo 2026 benchmark:

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

This produces:

```text
experiments/benchmark/yahoo_2026/static_IP/
experiments/benchmark/yahoo_2026/adp_aware_ILP/
experiments/benchmark/yahoo_2026/heuristic_greedy/
experiments/benchmark/yahoo_2026/heuristic_opportunity_cost/
experiments/benchmark/yahoo_2026/summary/
```

Expected benchmark size:

```text
12 draft positions * 21 delta values * 4 methods = 1008 rows
```

Heuristic optimality gap is reported against the ADP-aware ILP:

```text
optimal_gap_pct = (ADP-aware ILP objective - heuristic objective) / ADP-aware ILP objective
```

`Static IP` is not evaluated by this optimality gap because it ignores ADP
availability. It is used to estimate the no-ADP upper baseline and ADP
availability cost.

Each method folder contains:

```text
results.csv
summary.csv
draft_result_position6_delta0.csv
```

The representative draft result fixes `draft_position=6` and `delta=0`.
The `summary/` folder also contains:

```text
draft_result_position6_delta0_all_methods.csv
position6_delta0_roster_comparison.md
```

## Shadow Price

Run the LP-relaxation shadow price analysis at the representative setting:

```bash
python scripts/run_shadow_price.py \
  --players data/processed/2026_yahoo_data.csv \
  --outdir experiments/shadow_prices/yahoo_2026 \
  --draft-position 6 \
  --delta 0
```

This writes:

```text
experiments/shadow_prices/yahoo_2026/shadow_prices.csv
experiments/shadow_prices/yahoo_2026/position_shadow_prices.png
experiments/shadow_prices/yahoo_2026/shadow_price_summary.md
```

## Legacy/Supporting Experiments

The older scripts are retained for focused checks:

```bash
python scripts/run_experiments.py --players data/processed/2026_yahoo_data.csv
python scripts/evaluate_heuristics.py --players data/processed/2026_yahoo_data.csv
```

The main report should prefer `scripts/run_benchmark.py`, because it compares
IP and heuristics on the same draft-position by delta grid.

## Mock Draft

Mock draft is a supplemental dynamic simulation, not the main validation.

Example same-strategy run:

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
project_plan.md       project direction and experiment priorities
modeling.md           primal/dual model and shadow-price explanation
expr.md               experiment inventory
repo_cleanup_plan.md  cleanup and restructuring record
data_source.md        data-source notes
```
