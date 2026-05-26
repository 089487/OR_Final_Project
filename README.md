# Fantasy Baseball Draft Optimization

This project studies fantasy baseball snake-draft roster construction as an
operations research problem. The final scope is:

- `ADP-aware ILP`: exact benchmark with roster, eligibility, snake-pick, and ADP
  availability constraints.
- `Direct Greedy`: scalable heuristic that drafts by immediate positional
  scarcity.
- `Opportunity Cost Greedy`: scalable heuristic that drafts by current value
  relative to expected future replacement value.

Synthetic factor experiments are the main empirical evidence. The 2026 Yahoo
and FanGraphs data are kept as realistic validation cases, not as the main
experiment grid.

## Environment

```bash
source ~/myenv/bin/activate
pip install -r requirements.txt
```

Gurobi must be licensed and importable through `gurobipy` for ILP runs. The
heuristics run without Gurobi.

## Repository Layout

```text
reference/                 original project PDF
scoring/                   Yahoo and FanGraphs scoring tables
data/adp/                  ADP inputs
data/processed/            committed 2026 validation player pools
src/                       model, IP, heuristic, and synthetic-data code
scripts/                   data processing and experiment runners
docs/                      model and experiment design notes
reports/                   final result summaries and compact tables
experiments/synthetic/     committed synthetic scaling summary only
```

Raw synthetic instances, full benchmark outputs, logs, caches, and calibrated
2026 variants are intentionally ignored.

## Data

Committed validation inputs:

```text
data/adp/2026_adp.csv
data/processed/2026_yahoo_data.csv
data/processed/2026_fangraph_data.csv
```

To rebuild the 2026 processed files from the local raw projection files:

```bash
python scripts/process_data.py
```

The calibrated processed files are currently excluded from the main branch. They
can be used later for a robustness appendix if needed.

## Synthetic Experiments

Run a small smoke benchmark:

```bash
python scripts/run_synthetic_benchmark.py \
  --experiment smoke \
  --outdir /tmp/or_smoke \
  --seeds 0:1 \
  --methods adp_aware_ilp,direct_greedy,opportunity_cost_greedy
```

Run the baseline synthetic experiment:

```bash
python scripts/run_synthetic_benchmark.py \
  --experiment N1_baseline \
  --outdir experiments/synthetic/N1_baseline \
  --points-scenario normal \
  --position-scenario roster_ratio \
  --roster-scale 1 \
  --num-teams 12 \
  --player-demand-ratio 3 \
  --sigma-adp 30 \
  --delta 0 \
  --seeds 0:10 \
  --methods adp_aware_ilp,direct_greedy,opportunity_cost_greedy
```

Run the scenario suite:

```bash
python scripts/run_synthetic_scenario.py
```

After N4/N6 runs, regenerate the committed scaling summary:

```bash
python scripts/summarize_synthetic_scaling.py \
  --roots experiments/synthetic/N4_scaling experiments/synthetic/N6_large_scale_stress \
  --outdir experiments/synthetic/scaling_summary

python scripts/write_runtime_scaling_table.py \
  --input experiments/synthetic/scaling_summary/runtime_scaling_table.csv \
  --output experiments/synthetic/scaling_summary/runtime_scaling_table.md
```

## Real-Data Validation

The 2026 Yahoo and FanGraphs benchmarks are summarized only as compact report
artifacts:

```text
reports/real_data_results.md
reports/tables/real_data_summary_by_method.csv
```

Full `experiments/benchmark/yahoo_2026` and
`experiments/benchmark/fangraph_2026` outputs are not part of the final repo.
To rerun a local validation benchmark:

```bash
python scripts/run_benchmark.py \
  --players data/processed/2026_yahoo_data.csv \
  --outdir /tmp/yahoo_2026_benchmark \
  --scoring yahoo \
  --delta-min -10 \
  --delta-max 10 \
  --delta-step 1
```

## Results

Primary result files:

```text
reports/synthetic_results.md
reports/real_data_results.md
experiments/synthetic/scaling_summary/runtime_scaling_table.md
experiments/synthetic/scaling_summary/runtime_by_variable_count.png
experiments/synthetic/scaling_summary/heuristic_gap_by_variable_count.png
```

The central finding is that the ADP-aware ILP gives an exact benchmark on small
and medium instances, while both greedy heuristics scale to much larger
synthetic instances. Opportunity Cost Greedy is consistently closer to the ILP
objective than Direct Greedy in the final experiments.

## Documentation

```text
docs/modeling.md
docs/heuristics.md
docs/experiment_plan.md
docs/synthetic_experiment_design.md
docs/run_scripts.md
data_source.md
```

## Checks

```bash
python -m compileall src scripts
python scripts/run_synthetic_benchmark.py --experiment smoke --outdir /tmp/or_smoke --seeds 0:1 --methods adp_aware_ilp,direct_greedy,opportunity_cost_greedy
git status --short --ignored
```
