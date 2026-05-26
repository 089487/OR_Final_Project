# Experiment Plan

This project uses the 2026 MLB player pool as a realistic validation case and
synthetic data as the main controlled experiment suite.  The central question is
whether fast greedy heuristics can stay close to the ADP-aware ILP objective
while scaling to instances where the integer program becomes impractical.

## Methods

- `ADP-aware ILP`: exact benchmark with roster, eligibility, snake-draft pick,
  and ADP availability constraints.
- `Direct Greedy`: chooses the open roster position with the largest scarcity
  ratio, then drafts the best currently available player for that position.
- `Opportunity Cost Greedy`: chooses the position/player pair with the largest
  current-vs-future opportunity cost, with a feasibility fallback for tight
  position supply.

See `docs/heuristics.md` for the implementation details of both greedy methods.

Heuristic optimality gap is measured against the ADP-aware ILP:

```text
optimal_gap = (objective_ADP_aware_ILP - objective_heuristic) / objective_ADP_aware_ILP
```

Runtime is reported in seconds.  Scaling experiments also report:

```text
approx_variable_count = n * (1 + p + r)
```

where `n` is the number of players, `p` is the number of roster positions, and
`r` is roster size.

## 2026 Real-Data Validation

The real-data section is a sanity check, not the main experimental grid.  It
uses the processed 2026 Yahoo and FanGraphs player pools and reports aggregated
method performance from the existing benchmark summaries.

Report:

- mean objective by method;
- mean and max heuristic optimality gap;
- mean heuristic optimality gap ratio;
- number of benchmark cases.

Do not restore full `experiments/benchmark/` outputs into the repo.  Keep only
the compact report tables under `reports/`.

## Synthetic Factor Experiments

Synthetic experiments isolate one family of factors at a time.

| Scenario | Purpose | Main factors |
| --- | --- | --- |
| N1 Baseline | Establish a controlled reference case | normal points, roster-ratio positions, 12 teams, delta 0 |
| N2 Points Distribution | Test point-value shape | normal, uniform, high-low |
| N3 Position Distribution | Test eligibility structure | uniform-by-type, point-flexible, single-position, roster-ratio |
| N4 Scaling | Test moderate-size scaling | roster scale 1/2/3 and player-demand ratio 1/3/10 |
| N5 ADP Uncertainty | Test ADP noise and tolerance sensitivity | sigma_adp 0/10/30/60/100 and delta -10..10 |
| N6 Large-Scale Stress | Show IP scalability limits | large player pools and roster scales |

Most synthetic scenarios fix a middle draft position and `delta = 0` so each
factor effect is isolated.  N5 is the dedicated ADP uncertainty experiment.

## Main Figures and Tables

- `reports/synthetic_results.md`: narrative summary of N1-N6.
- `reports/real_data_results.md`: compact 2026 validation table and takeaways.
- `experiments/synthetic/scaling_summary/runtime_by_variable_count.png`: main
  scalability figure.
- `experiments/synthetic/scaling_summary/heuristic_gap_by_variable_count.png`:
  heuristic quality over size where an ILP benchmark exists.
- `experiments/synthetic/scaling_summary/runtime_scaling_table.md`: runtime and
  status table, including the manually interrupted timeout-target IP row.

## Interpretation

The expected final story is:

1. The ADP-aware ILP gives the correct benchmark on small and medium instances.
2. Opportunity Cost Greedy has consistently smaller optimality gaps than Direct
   Greedy.
3. IP runtime grows quickly with approximate variable count.
4. Both heuristics solve the largest synthetic stress instance in seconds, while
   the corresponding IP attempt does not produce a result before interruption.
