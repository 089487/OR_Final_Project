# Synthetic Factor Tables for N1-N6

Below are the factor tables for the synthetic experiments. The metric reported is `optimal_gap_ratio` relative to the ADP-aware ILP benchmark, shown as `avg ± std` across random seeds.

## N1 Baseline

Fixed setting:
- `points_scenario = normal`
- `position_scenario = roster_ratio`
- `roster_scale = 1`
- `num_teams = 12`
- `player_demand_ratio = 3`
- `sigma_adp = 30`
- `delta = 0`
- seeds = `0:10`

| Method | optimal_gap_ratio (`avg ± std`) |
|---|---:|
| Direct Greedy (baseline) | `4.79% ± 1.18%` |
| Opportunity Cost Greedy (our approach) | `1.92% ± 0.57%` |

## N2 Points Distribution

Fixed setting:
- `position_scenario = roster_ratio`
- `roster_scale = 1`
- `num_teams = 12`
- `player_demand_ratio = 3`
- `sigma_adp = 30`
- `delta = 0`
- seeds = `0:10`

Varied factor:
- `points_scenario = normal / uniform / high_low`

| points_scenario | Direct Greedy (baseline) | Opportunity Cost Greedy (our approach) |
|---|---:|---:|
| normal | `4.79% ± 1.18%` | `1.92% ± 0.57%` |
| uniform | `3.24% ± 0.77%` | `1.44% ± 0.59%` |
| high_low | `8.39% ± 2.40%` | `2.87% ± 1.32%` |

## N3 Position Distribution

Fixed setting:
- `points_scenario = normal`
- `roster_scale = 1`
- `num_teams = 12`
- `player_demand_ratio = 3`
- `sigma_adp = 30`
- `delta = 0`
- seeds = `0:10`

Varied factor:
- `position_scenario = uniform_by_type / point_flexible / single_position / roster_ratio`

| position_scenario | Direct Greedy (baseline) | Opportunity Cost Greedy (our approach) |
|---|---:|---:|
| uniform_by_type | `4.89% ± 0.62%` | `1.07% ± 0.43%` |
| point_flexible | `5.36% ± 1.66%` | `1.34% ± 0.68%` |
| single_position | `5.11% ± 1.48%` | `0.94% ± 0.65%` |
| roster_ratio | `4.79% ± 1.18%` | `1.92% ± 0.57%` |

## N4 Scaling

Fixed setting:
- `points_scenario = normal`
- `position_scenario = roster_ratio`
- `sigma_adp = 30`
- `delta = 0`
- `num_teams = 12`

Varied factors:
- `roster_scale = 1 / 2 / 3`
- `player_demand_ratio = 1 / 3 / 10`

| roster_scale | player_demand_ratio | Direct Greedy (baseline) | Opportunity Cost Greedy (our approach) |
|---|---:|---:|---:|
| 1 | 1 | `8.13% ± 1.64%` | `3.02% ± 0.95%` |
| 1 | 3 | `5.54% ± 1.07%` | `1.97% ± 0.73%` |
| 1 | 10 | `3.39% ± 0.96%` | `1.23% ± 0.38%` |
| 2 | 1 | `6.65% ± 0.40%` | `2.46% ± 0.63%` |
| 2 | 3 | `2.55% ± 0.69%` | `1.07% ± 0.44%` |
| 2 | 10 | `2.34% ± 0.53%` | `0.81% ± 0.40%` |
| 3 | 1 | `4.82% ± 0.40%` | `2.69% ± 0.55%` |
| 3 | 3 | `2.30% ± 0.52%` | `0.89% ± 0.29%` |
| 3 | 10 | `1.88% ± 0.22%` | `0.48% ± 0.17%` |

## N5 ADP Uncertainty

Fixed setting:
- `points_scenario = normal`
- `position_scenario = roster_ratio`
- `roster_scale = 1`
- `num_teams = 12`
- `player_demand_ratio = 3`
- seeds = `0:10`

Varied factors:
- `sigma_adp = 0 / 10 / 30 / 60 / 100`
- `delta = -10..10`

For the table below, the reported value is averaged over all `delta` values.

| sigma_adp | Direct Greedy (baseline) | Opportunity Cost Greedy (our approach) |
|---|---:|---:|
| 0 | `1.72% ± 0.70%` | `0.42% ± 0.17%` |
| 10 | `3.34% ± 0.91%` | `0.99% ± 0.45%` |
| 30 | `5.03% ± 1.28%` | `1.80% ± 0.75%` |
| 60 | `5.73% ± 1.35%` | `2.43% ± 1.38%` |
| 100 | `4.50% ± 1.48%` | `2.15% ± 1.16%` |

## N6 Large-Scale Stress

N6 is a stress-test family. Each instance now runs a single representative run on the baseline configuration; the focus is runtime scaling, not seed-level variability.

### N6 synthetic table result

| Experiment | Direct Greedy runtime | Opportunity Cost Greedy runtime | ADP-aware ILP runtime / status | Status | Source |
|---|---:|---:|---:|---|---|
| stress_small | `0.790 s` | `0.852 s` | `4.235 s / OPTIMAL` | complete | local dump from ws6 |
| stress_medium | `0.951 s` | `1.144 s` | `12.230 s / OPTIMAL` | complete | local dump from ws6 |
| stress_large | `1.981 s` | `2.344 s` | `54.267 s / OPTIMAL` | complete | local dump from ws6 |
| stress_xlarge | `6.172 s` | `10.360 s` | `276.895 s / OPTIMAL` | complete | local dump from ws6 |
| stress_timeout_target | `17.760 s` | `23.286 s` | `1869.805 s / ERROR_TimeoutError` | complete | local dump from ws6 |

### N6 scaling summary

| level | method | approx_variable_count | num_players | roster_size | runtime_display | status | cases | note |
|---|---|---:|---:|---:|---|---|---:|---|
| stress_small | ADP-aware ILP | 334080 | 5760 | 48 | `4.235s` | OPTIMAL | 1 | one run per instance; no seed averaging |
| stress_small | Opportunity Cost Greedy | 334080 | 5760 | 48 | `0.852s` | OPTIMAL | 1 | one run per instance; no seed averaging |
| stress_small | Direct Greedy | 334080 | 5760 | 48 | `0.790s` | OPTIMAL | 1 | one run per instance; no seed averaging |
| stress_medium | ADP-aware ILP | 710400 | 9600 | 64 | `12.230s` | OPTIMAL | 1 | one run per instance; no seed averaging |
| stress_medium | Opportunity Cost Greedy | 710400 | 9600 | 64 | `1.144s` | OPTIMAL | 1 | one run per instance; no seed averaging |
| stress_medium | Direct Greedy | 710400 | 9600 | 64 | `0.951s` | OPTIMAL | 1 | one run per instance; no seed averaging |
| stress_large | ADP-aware ILP | 2289600 | 21600 | 96 | `54.267s` | OPTIMAL | 1 | one run per instance; no seed averaging |
| stress_large | Opportunity Cost Greedy | 2289600 | 21600 | 96 | `2.344s` | OPTIMAL | 1 | one run per instance; no seed averaging |
| stress_large | Direct Greedy | 2289600 | 21600 | 96 | `1.981s` | OPTIMAL | 1 | one run per instance; no seed averaging |
| stress_xlarge | ADP-aware ILP | 10880000 | 64000 | 160 | `276.895s` | OPTIMAL | 1 | one run per instance; no seed averaging |
| stress_xlarge | Opportunity Cost Greedy | 10880000 | 64000 | 160 | `10.360s` | OPTIMAL | 1 | one run per instance; no seed averaging |
| stress_xlarge | Direct Greedy | 10880000 | 64000 | 160 | `6.172s` | OPTIMAL | 1 | one run per instance; no seed averaging |
| timeout_target | ADP-aware ILP | 49029120 | 184320 | 256 | `1869.805s` | ERROR_TimeoutError | 1 | one run per instance; exceeded 1800s wall-time target |
| timeout_target | Opportunity Cost Greedy | 49029120 | 184320 | 256 | `23.286s` | OPTIMAL | 1 | one run per instance; no seed averaging |
| timeout_target | Direct Greedy | 49029120 | 184320 | 256 | `17.760s` | OPTIMAL | 1 | one run per instance; no seed averaging |

## Quick Interpretation

- `high_low` in N2 is the hardest points distribution.
- `single_position` in N3 is the hardest position distribution.
- N4 shows that larger player pools and larger rosters increase difficulty, but Opportunity Cost Greedy stays consistently closer to ILP.
- N5 shows that larger `sigma_adp` generally makes the draft harder.
- N6 shows the clear scalability gap: ILP runtime grows sharply, `stress_large` is still comfortably solvable, `stress_xlarge` remains solvable but slower, and `stress_timeout_target` is the first case that hits the wall-time limit.
- In N6, each instance is a single representative run, so `cases = 1` means one measurement per instance rather than a seed average.
