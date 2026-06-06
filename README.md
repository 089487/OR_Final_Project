# Fantasy Baseball Draft Optimization

This repository is the final deliverable for an operations research project on
fantasy baseball snake-draft roster construction under market scarcity.

The project combines:

- `ADP-aware ILP`: exact benchmark with roster, eligibility, snake-pick, and ADP
  availability constraints.
- `Direct Greedy` (DG): fast heuristic that drafts by immediate positional
  scarcity.
- `Opportunity Cost Greedy` (OCG): fast heuristic that compares current value
  against expected future replacement value.
- `Competitive draft simulation`: full draft-room simulations where OCG and DG
  agents compete for the same 2026 player pool.

Synthetic factor experiments are the main empirical evidence. The 2026 Yahoo
and FanGraphs datasets are used as realistic validation cases and for the
competitive simulation appendix.

## Final Artifacts

The main submitted artifacts are:

```text
reports/final_report.pdf                 final written report
reports/final_report.tex                 report source
slides/final_slide.pptx                  final presentation deck
slides/final_slide.pdf                   rendered slide deck
slides/final_slide.html                  HTML slide export
factor_explorer.html                     interactive factor/scenario explorer
```

The compact result summaries used by the report are:

```text
reports/synthetic_results.md
reports/real_data_results.md
reports/tables/real_data_summary_by_method.csv
reports/tables/synthetic_scenario_objective_summary.csv
reports/tables/synthetic_scenario_objectives_by_seed.csv
experiments/synthetic/scaling_summary/runtime_scaling_table.md
experiments/competitive_draft/ocg_vs_dg_2026/combined_summary.md
experiments/competitive_draft/dg_vs_ocg_2026/combined_summary.md
experiments/competitive_draft/all_ocg_all_dg_2026/combined_summary.md
```

## Environment

```bash
source ~/myenv/bin/activate
pip install -r requirements.txt
```

Gurobi must be licensed and importable through `gurobipy` for ILP runs. The
greedy heuristics and competitive draft simulations can run without solving the
ILP.

## Repository Layout

```text
src/                         model, draft logic, ILP, heuristics, simulation
scripts/                     data processing and experiment entry points
scoring/                     Yahoo and FanGraphs scoring tables
data/adp/                    historical and 2026 ADP inputs
data/raw/                    local raw 2026 FantasyPros projection inputs
data/processed/              committed 2026 Yahoo/FanGraphs validation pools
docs/                        modeling and experiment-design notes
reports/                     final report, figures, and compact result tables
slides/                      final deck and rendered exports
experiments/synthetic/       committed synthetic summaries and scaling figures
experiments/competitive_draft/ committed 2026 draft-room simulation outputs
reference/                   original project references and instructions
```

Raw synthetic instances, generated `data/synthetic/` metadata, full benchmark
directories, LaTeX auxiliary files, caches, and calibrated 2026 processed pools
are intentionally ignored by git.

## Code Map

The core Python modules are:

```text
src/draft_core.py          snake-pick order, roster rules, player loading
src/ip_model.py            static and ADP-aware integer programming models
src/heuristics.py          Direct Greedy and Opportunity Cost Greedy
src/synthetic_data.py      synthetic player-pool generation
src/competitive_draft.py   multi-team draft-room simulation
```

The main runnable entry points are:

```text
scripts/process_data.py                rebuild 2026 processed player pools
scripts/run_benchmark.py               real-data ILP/DG/OCG benchmark grid
scripts/run_synthetic_benchmark.py     configurable synthetic benchmark runner
scripts/run_synthetic_scenario.py      predefined N1-N6 synthetic scenarios
scripts/run_competitive_draft.py       competitive OCG/DG draft simulations
scripts/summarize_synthetic_scaling.py scaling summary aggregation
scripts/write_runtime_scaling_table.py Markdown runtime table writer
```

## Data Pipeline

Committed validation inputs:

```text
data/adp/2026_adp.csv
data/raw/2026/FantasyPros_2026_Projections_H.csv
data/raw/2026/FantasyPros_2026_Projections_P.csv
data/processed/2026_yahoo_data.csv
data/processed/2026_fangraph_data.csv
```

To rebuild the processed 2026 Yahoo and FanGraphs pools from the local raw
projection files:

```bash
python scripts/process_data.py
```

The calibrated processed files are present locally only when generated and are
excluded from the final tracked branch.

## Synthetic Experiments

Run a small smoke benchmark:

```bash
python scripts/run_synthetic_benchmark.py \
  --experiment smoke \
  --outdir /tmp/or_smoke \
  --seeds 0:1 \
  --methods adp_aware_ilp,direct_greedy,opportunity_cost_greedy
```

Run one predefined scenario suite:

```bash
python scripts/run_synthetic_scenario.py --scenario N1
python scripts/run_synthetic_scenario.py --scenario N2
python scripts/run_synthetic_scenario.py --scenario N3
python scripts/run_synthetic_scenario.py --scenario N4
python scripts/run_synthetic_scenario.py --scenario N5
python scripts/run_synthetic_scenario.py --scenario N6
```

`N6` can optionally attempt the larger ILP runs:

```bash
python scripts/run_synthetic_scenario.py --scenario N6 --include-n6-ip
```

After N4/N6 scaling runs, regenerate the committed scaling summary:

```bash
python scripts/summarize_synthetic_scaling.py \
  --roots experiments/synthetic/N4_scaling experiments/synthetic/N6_large_scale_stress \
  --outdir experiments/synthetic/scaling_summary

python scripts/write_runtime_scaling_table.py \
  --input experiments/synthetic/scaling_summary/runtime_scaling_table.csv \
  --output experiments/synthetic/scaling_summary/runtime_scaling_table.md
```

Detailed synthetic commands are documented in `docs/run_scripts.md`.

## Real-Data Validation

The real-data benchmark uses the 2026 processed Yahoo/FanGraphs pools. The full
grid has 12 draft positions times 21 delta values per scoring system when using
the default `-10..10` delta sweep.

Example local Yahoo run:

```bash
python scripts/run_benchmark.py \
  --players data/processed/2026_yahoo_data.csv \
  --outdir /tmp/yahoo_2026_benchmark \
  --scoring yahoo \
  --delta-min -10 \
  --delta-max 10 \
  --delta-step 1
```

The final report uses compact summaries rather than committing the full
benchmark output directories.

## Competitive Draft Simulation

Run OCG against DG opponents for every draft slot on both 2026 datasets:

```bash
python scripts/run_competitive_draft.py \
  --datasets 2026_yahoo,2026_fangraph \
  --mode single_ocg \
  --ocg-team all \
  --outdir experiments/competitive_draft/ocg_vs_dg_2026
```

Run the reverse diagnostic, one DG team against OCG opponents:

```bash
python scripts/run_competitive_draft.py \
  --datasets 2026_yahoo,2026_fangraph \
  --mode single_dg \
  --dg-team all \
  --outdir experiments/competitive_draft/dg_vs_ocg_2026
```

Run all-OCG and all-DG draft rooms:

```bash
python scripts/run_competitive_draft.py \
  --datasets 2026_yahoo,2026_fangraph \
  --mode all_ocg,all_dg \
  --outdir experiments/competitive_draft/all_ocg_all_dg_2026
```

## Documentation

Useful supporting notes:

```text
docs/modeling.md
docs/heuristics.md
docs/experiment_plan.md
docs/synthetic_experiment_design.md
docs/run_scripts.md
data_source.md
reports/project_summary.md
reports/project_summary_en.md
reports/project_summary_zh.md
```

## Checks

Recommended sanity checks before handoff:

```bash
python -m compileall src scripts
python scripts/run_synthetic_benchmark.py --experiment smoke --outdir /tmp/or_smoke --seeds 0:1 --methods adp_aware_ilp,direct_greedy,opportunity_cost_greedy
python scripts/run_competitive_draft.py --datasets 2026_yahoo --mode single_ocg --ocg-team 1 --outdir /tmp/or_competitive_smoke
git status --short --ignored
```

To rebuild the final report PDF from the repository root:

```bash
latexmk -cd -xelatex -interaction=nonstopmode -halt-on-error reports/final_report.tex
```
