# Fantasy Baseball Draft Optimization Report Guide

This document is the single reference you can use to write the final report for the project.

## 1. Project Overview

This project studies fantasy baseball snake-draft roster construction as an operations research problem. The central question is whether a fast heuristic can stay close to the exact optimization benchmark while scaling much better on large draft instances.

The project compares:
- an ADP-aware integer linear program, which acts as the exact benchmark
- Direct Greedy, a simple baseline heuristic
- Opportunity Cost Greedy, a more strategic heuristic

The main evidence comes from synthetic experiments, because they let us control:
- player value distribution
- position flexibility
- roster size
- player-pool size
- ADP noise
- ADP tolerance

Real-data validation with 2026 Yahoo and FanGraphs inputs is included as a sanity check, but the synthetic experiments are the main story.

## 2. Core Project Structure

### `src/`
The core modeling code lives here.

- `src/draft_core.py`
  - shared roster rules
  - snake-draft pick generation
  - player loading and normalization
  - `DraftSolution` data structure

- `src/ip_model.py`
  - exact Gurobi ILP
  - objective and constraints
  - ADP availability enforcement

- `src/heuristics.py`
  - Direct Greedy
  - Opportunity Cost Greedy

- `src/synthetic_data.py`
  - synthetic player generation
  - points, positions, and ADP construction

### `scripts/`
These scripts orchestrate experiments and reporting.

- `scripts/process_data.py`
  - builds the 2026 processed Yahoo/FanGraphs datasets

- `scripts/run_benchmark.py`
  - runs real-data validation benchmarks

- `scripts/run_synthetic_benchmark.py`
  - runs controlled synthetic experiments

- `scripts/run_synthetic_scenario.py`
  - runs the N1-N6 scenario suites

- `scripts/summarize_synthetic_scaling.py`
  - aggregates scaling results and generates summary plots

- `scripts/write_runtime_scaling_table.py`
  - creates report-ready tables

### `docs/`
These are useful for explaining the project in the report.

- `docs/modeling.md`
- `docs/heuristics.md`
- `docs/experiment_plan.md`
- `docs/synthetic_experiment_design.md`

### `reports/`
Contains compact summary writeups and result tables.

## 3. Draft Model

The project uses the same fantasy roster structure everywhere:

| Position | Slots |
| --- | ---: |
| C | 1 |
| 1B | 1 |
| 2B | 1 |
| 3B | 1 |
| SS | 1 |
| OF | 3 |
| Util | 1 |
| SP | 5 |
| RP | 2 |

Total roster size:
- `16` before scaling

### Important notes
- `Util` is hitter-only
- pitchers cannot be assigned to `Util`
- the same roster rules are used by the ILP and both heuristics

### Snake draft
Pick ownership is determined by snake-draft position and number of teams. The model uses those pick numbers to decide when a player is available.

## 4. Exact Benchmark: ADP-Aware ILP

The exact benchmark is an integer linear program solved with Gurobi.

### Decision variables
- `y_i`: whether player `i` is drafted
- `x_ip`: whether player `i` is assigned to position `p`
- `z_ik`: whether player `i` is selected with owned pick `k`

### Objective
Maximize total projected points of the drafted roster.

### Constraints
- each owned pick selects exactly one player
- each drafted player is assigned to exactly one roster position
- roster requirements must be met exactly
- a player can only be assigned to eligible positions
- a player becomes unavailable if `adp + delta < current_pick`

### Interpretation of `delta`
`delta` is the ADP buffer.

- smaller `delta` means stricter ADP availability
- larger `delta` means more tolerance
- `delta = 0` means the player must still be draftable at their ADP window

The ILP is the gold standard for objective value, but it becomes expensive as the player pool grows.

## 5. Heuristic Baselines

### Direct Greedy
Direct Greedy:
- looks at open positions
- picks the scarcest one
- drafts the best currently available player for that position

This heuristic is simple and fast, but it can make myopic decisions.

### Opportunity Cost Greedy
Opportunity Cost Greedy:
- compares the best current player at each open position with the best player expected to remain available at the next owned pick
- tries to estimate the cost of waiting
- includes a fallback for tight position supply

This heuristic is more strategic than Direct Greedy and is usually the stronger baseline.

### How to evaluate heuristics
The heuristics are evaluated against the ADP-aware ILP benchmark using:
- objective value
- runtime
- optimality gap

Typical gap definition:
- `optimal_gap = objective_ADP_aware_ILP - objective_heuristic`

You can also report:
- `optimal_gap_pct = optimal_gap / objective_ADP_aware_ILP`

For the scaling figures, the main runtime chart uses:
- `runtime_seconds` vs `approx_variable_count`

The heuristic gap chart uses:
- `optimal_gap_pct` vs `approx_variable_count`

The IP status chart uses:
- `mip_gap` and solver status vs `approx_variable_count`

## 6. Synthetic Data Design

Synthetic data is the main experimental engine of the project.

The generator creates fictional player pools with:
- `season`
- `player`
- `projected_points`
- `adp`
- `eligible_positions`

The synthetic data is designed so the optimization models can consume it directly.

## 7. Synthetic Data Logic

Synthetic player generation has three main components:
1. projected points
2. eligible positions
3. ADP

### 7.1 Projected points

There are three point scenarios.

#### `normal`
- values cluster near the middle
- this is the baseline benchmark world
- good for a balanced comparison

Typical behavior:
- many average players
- some high-value players
- some low-value players

#### `uniform`
- values are spread evenly across the range
- there is no natural clustering
- tests a flatter value landscape

#### `high_low`
- about 10% of players are high value
- about 90% are lower value
- elite misses become more costly

This is the most star-sensitive scenario.

### 7.2 Position eligibility

There are four position scenarios.

#### `uniform_by_type`
Players are first split into hitters and pitchers, then position patterns are sampled uniformly within each type.

For hitters, examples include:
- `C`
- `1B`
- `2B`
- `3B`
- `SS`
- `OF`
- `1B;3B`
- `2B;SS`
- `OF;Util`

For pitchers:
- `SP`
- `RP`
- `SP;RP`

Purpose:
- random flexibility
- no intentional link between points and flexibility

#### `point_flexible`
This is the only scenario where points and position flexibility are intentionally linked.

- high-value hitters are more likely to have multiple positions
- high-value pitchers are more likely to be `SP;RP`

Purpose:
- favorable to heuristics
- top players are easier to fit into the roster
- tests a world where flexibility helps draft quality

#### `single_position`
Every player has exactly one position.

Purpose:
- least flexible scenario
- makes greedy mistakes hardest to repair
- strongest test of position scarcity

#### `roster_ratio`
Positions are sampled in proportions similar to roster demand:
- more `OF`
- more `SP`
- more `RP`
- fewer single-slot infielders

Purpose:
- balanced baseline
- supply roughly matches demand
- most realistic default position scenario

### 7.3 ADP generation

ADP is created from the point ranking plus Gaussian noise.

Conceptually:
1. rank players by descending points
2. convert rank into a draft order
3. add noise controlled by `sigma_adp`
4. clip the result into valid bounds

#### Meaning of `sigma_adp`
- `0`: ADP perfectly follows player value
- `10`: mild noise
- `30`: moderate noise
- `60`: strong noise
- `100`: very noisy market

#### Why it matters
- low noise means the market is predictable
- high noise creates bargains and traps
- this is the key factor in the ADP uncertainty experiment

## 8. Roster Scale and Player Pool Size

The base roster has 16 slots.

### Roster scaling
When `roster_scale = s`, every roster slot is multiplied by `s`.

Examples:
- `s = 1` gives roster size `16`
- `s = 2` gives roster size `32`
- `s = 3` gives roster size `48`

### Player demand ratio
Player pool size is controlled by:
- `player_demand_ratio = n / D`
- where `n` is the number of players and `D` is total draft demand

Interpretation:
- `1`: nearly every player is needed
- `3`: moderate supply
- `10`: large supply, larger optimization problem

This is one of the main scaling drivers in the experiments.

## 9. Why the Synthetic Experiments Are the Main Evidence

The synthetic experiments are the main evidence because they are controlled and interpretable.

They show:
- whether the heuristics stay close to the exact benchmark
- how runtime changes with problem size
- how ADP uncertainty affects performance
- how position structure changes difficulty

The real-data validation cases are useful, but they are secondary. They mainly confirm that the methods behave reasonably on realistic 2026 player pools.

## 10. Scenario-by-Scenario Experiment Description

## N1 Baseline
Purpose:
- establish the reference case
- compare exact and heuristic methods in a balanced synthetic world

Fixed setup:
- `points_scenario = normal`
- `position_scenario = roster_ratio`
- `roster_scale = 1`
- `num_teams = 12`
- `player_demand_ratio = 3`
- `sigma_adp = 30`
- `delta = 0`
- `seeds = 0:10`

What it tells you:
- the baseline performance gap
- whether Opportunity Cost Greedy is closer to the ILP than Direct Greedy
- the normal-case runtime profile

## N2 Points Distribution
Purpose:
- test how value distribution affects method quality

Fixed setup:
- `position_scenario = roster_ratio`
- `roster_scale = 1`
- `num_teams = 12`
- `player_demand_ratio = 3`
- `sigma_adp = 30`
- `delta = 0`
- `seeds = 0:10`

Varied factor:
- `points_scenario = normal, uniform, high_low`

What it tells you:
- whether elite-heavy worlds are harder
- whether flatter point landscapes change heuristic behavior
- how sensitive the methods are to point distribution shape

Expected interpretation:
- `high_low` should make misses more costly
- `uniform` may broaden the opportunity landscape
- `normal` is the balanced middle case

## N3 Position Distribution
Purpose:
- test how positional flexibility changes performance

Fixed setup:
- `points_scenario = normal`
- `roster_scale = 1`
- `num_teams = 12`
- `player_demand_ratio = 3`
- `sigma_adp = 30`
- `delta = 0`
- `seeds = 0:10`

Varied factor:
- `position_scenario = uniform_by_type`
- `position_scenario = point_flexible`
- `position_scenario = single_position`
- `position_scenario = roster_ratio`

What it tells you:
- how much flexibility helps heuristics
- how much single-position scarcity hurts them
- whether the position structure meaningfully changes optimality gaps

Expected interpretation:
- `point_flexible` should be easiest
- `single_position` should be hardest
- `roster_ratio` should be the balanced baseline

## N4 Scaling
Purpose:
- study how problem size affects runtime and gap behavior

Fixed setup:
- `points_scenario = normal`
- `position_scenario = roster_ratio`
- `sigma_adp = 30`
- `delta = 0`
- `num_teams = 12`

Varied factors:
- `roster_scale = 1, 2, 3`
- `player_demand_ratio = 1, 3, 10`

What it tells you:
- how runtime grows with roster size
- how runtime grows with player-pool size
- where exact optimization starts to become expensive

Why it matters:
- this is the key scalability story
- it supports the practical value of heuristics

## N5 ADP Uncertainty
Purpose:
- test sensitivity to market noise and ADP tolerance

Fixed setup:
- `points_scenario = normal`
- `position_scenario = roster_ratio`
- `roster_scale = 1`
- `num_teams = 12`
- `player_demand_ratio = 3`
- `seeds = 0:10`

Varied factors:
- `sigma_adp = 0, 10, 30, 60, 100`
- `delta = -10 .. 10` with step `1`

What it tells you:
- how robust each method is to noisy ADP
- how strict or permissive availability rules affect performance
- whether better tolerance settings can improve results

Expected interpretation:
- low `sigma_adp` makes ADP highly informative
- high `sigma_adp` makes the market less reliable
- `delta` controls feasibility and draft aggressiveness

## N6 Large-Scale Stress
Purpose:
- push the models into large regimes where exact optimization becomes impractical

What it demonstrates:
- heuristic methods remain usable at much larger scales
- the ILP’s runtime grows too fast in large instances
- there is a practical tradeoff between exactness and speed

Typical settings:
- larger roster scales
- larger player-demand ratios
- larger league sizes
- fewer seeds for each stress level

Key message:
- heuristics are not just approximate; they are the practical option in large instances

### Updated N6 interpretation for this project
The current N6 rerun uses one representative run per stress instance. The latest local results are:

- `stress_small`
  - ADP-aware ILP: `4.235s`, `OPTIMAL`
  - Opportunity Cost Greedy: `0.852s`
  - Direct Greedy: `0.790s`
- `stress_medium`
  - ADP-aware ILP: `12.230s`, `OPTIMAL`
  - Opportunity Cost Greedy: `1.144s`
  - Direct Greedy: `0.951s`
- `stress_large`
  - ADP-aware ILP: `54.267s`, `OPTIMAL`
  - Opportunity Cost Greedy: `2.344s`
  - Direct Greedy: `1.981s`
- `stress_xlarge`
  - ADP-aware ILP: `276.895s`, `OPTIMAL`
  - Opportunity Cost Greedy: `10.360s`
  - Direct Greedy: `6.172s`
- `stress_timeout_target`
  - ADP-aware ILP: `1869.805s`, `ERROR_TimeoutError`
  - Opportunity Cost Greedy: `23.286s`
  - Direct Greedy: `17.760s`

Interpretation:
- the ILP is still solvable on `stress_xlarge`, but the wall time grows sharply
- `stress_timeout_target` is the first case that exceeds the 1800s target
- both heuristics remain practical across the full N6 range

## 11. How to Write the Experimental Story in the Report

A good report structure is:

1. Introduce the business or research question
2. Explain the exact ILP benchmark
3. Introduce the heuristic alternatives
4. Describe the synthetic data generator
5. Explain the N1-N6 experiment design
6. Present the results
7. Emphasize the scalability tradeoff
8. Conclude with the practical recommendation

### Suggested story flow
- N1 establishes the baseline
- N2 and N3 test whether value and flexibility matter
- N4 shows scaling behavior
- N5 shows ADP uncertainty effects
- N6 shows the limit of exact optimization

## 12. Report-Ready Wording

You can reuse these sentences directly or adapt them.

### Project summary
This project formulates fantasy baseball draft roster construction as an ADP-aware integer optimization problem. The exact ILP provides a benchmark solution, while two greedy heuristics offer scalable alternatives for larger instances.

### Synthetic experiments
Synthetic experiments are used as the main evaluation platform because they allow controlled variation in point distributions, position flexibility, roster scale, player-pool size, and ADP uncertainty.

### Method comparison
Opportunity Cost Greedy is designed to be more strategic than Direct Greedy by accounting for the value of waiting for future availability. The ILP remains the exact benchmark, but the heuristics are much faster on larger instances.

### Scalability conclusion
The largest synthetic stress cases demonstrate that exact optimization becomes computationally expensive as the player pool and roster size grow, while the heuristics remain practical and continue to produce results quickly. In the current N6 rerun, `stress_timeout_target` is the first case where the ILP hits the wall-time limit, but both heuristics still finish in seconds.

## 13. Key Terms

- `ADP`: average draft position
- `delta`: ADP tolerance buffer
- `roster scale`: multiplicative factor applied to base roster requirements
- `player-demand ratio`: player-pool size relative to total draft demand
- `optimal gap`: difference between heuristic objective and ILP objective
- `runtime`: computational time in seconds

## 14. Main Takeaways to Emphasize

- The project is about the tradeoff between exactness and scalability.
- The synthetic experiments are the most important evidence.
- The scaling summary should be presented as a single representative run per stress instance, not a seed average.
- In N6, report runtime and gap against `approx_variable_count` rather than comparing multiple seeds.
- Opportunity Cost Greedy is generally the better heuristic.
- The exact ILP is the gold standard on smaller instances.
- The heuristics become more valuable as the problem size grows.
- ADP noise and position flexibility both have meaningful effects on method performance.

## 15. Suggested Final Report Thesis

If you need a one-sentence thesis for the report, use this:

This project shows that while the ADP-aware ILP provides the exact benchmark for fantasy baseball draft optimization, Opportunity Cost Greedy delivers a strong practical alternative that remains much faster and scales better on large synthetic instances.

If you want, I can next convert this into a formal report outline or a shorter executive-summary version.
