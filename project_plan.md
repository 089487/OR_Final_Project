# Project Direction and Experiment Plan

## Main Thesis

This project should focus on integer programming for fantasy baseball draft
optimization, using historical MLB projection and ADP data to study draft
position, ADP uncertainty, roster constraints, scoring systems, and heuristic
performance.

Mock draft simulation is useful, but it should be a supplementary dynamic
simulation rather than the main empirical result. Its conclusions depend on
assumptions about opponent behavior, such as noisy ADP sampling, so it is less
directly grounded than the IP and historical-data experiments.

## Recommended Priority

1. Build historical datasets for 2021-2024.
2. Run the IP model across seasons, draft positions, scoring systems, and ADP
   delta values.
3. Analyze LP relaxation shadow prices for roster constraints.
4. Compare heuristics against the ADP-aware IP using optimal gap.
5. Keep mock draft as a final optional application demo.

## Data Plan

For each season from 2021 to 2024, collect or construct:

- preseason ADP
- hitter projections
- pitcher projections
- processed Yahoo points data
- processed FanGraphs points data

The processed data format should match the current 2026 files:

```text
season
player
team
eligible_positions
adp
projected_points
```

Recommended output layout:

```text
data/processed/2021_yahoo_data.csv
data/processed/2021_fangraph_data.csv
data/processed/2022_yahoo_data.csv
data/processed/2022_fangraph_data.csv
data/processed/2023_yahoo_data.csv
data/processed/2023_fangraph_data.csv
data/processed/2024_yahoo_data.csv
data/processed/2024_fangraph_data.csv
data/processed/2026_yahoo_data.csv
data/processed/2026_fangraph_data.csv
```

## Core IP Experiments

Use `scripts/run_benchmark.py` as the main benchmark runner to evaluate:

- draft position sensitivity: positions 1 through 12
- ADP delta sensitivity: recommended range `-10` to `10`, stride `1`
- scoring comparison: Yahoo vs FanGraphs
- season comparison: 2021-2024 historical seasons, plus 2026 projection case

Main outputs:

- optimal roster by draft position
- objective value by draft position
- objective value by ADP delta
- summary report
- per-method `results.csv`, `summary.csv`, and `draft_result_position6_delta0.csv`
- combined `summary/` folder with method-comparison plots and optimality-gap summaries

## Shadow Price Analysis

Use LP relaxation dual values to interpret roster constraints:

- high positive shadow price means that adding one slot at that position would
  increase the relaxed objective more
- compare shadow prices across seasons and scoring systems
- identify structurally scarce or valuable roster slots, such as SP, RP, OF, SS,
  or C

The shadow price analysis should be presented as model interpretation, not as a
literal integer marginal value.

Default execution should use `scripts/run_shadow_price.py` at:

```text
draft_position = 6
delta = 0
```

## Heuristic Experiments

Use `scripts/run_benchmark.py` as the preferred comparison source, or
`scripts/evaluate_heuristics.py` for focused heuristic-only checks, to compare:

- ADP-aware IP
- Direct Greedy
- Opportunity Cost Greedy

Main metric:

- optimal gap ratio = `(ADP-aware ILP objective - heuristic objective) / ADP-aware ILP objective`

Static IP is not evaluated by this optimal-gap ratio because it ignores ADP
availability. It is reported separately as a no-ADP upper baseline.

Each method should also report a representative case:

```text
draft_position = 6
delta = 0
```

as `draft_result_position6_delta0.csv`.

Recommended experiment grid:

- seasons: 2021-2024, plus optional 2026
- scoring systems: Yahoo and FanGraphs
- draft positions: 1 through 12
- ADP delta: `-10` to `10`, stride `1`

This is the best place to evaluate the heuristics, because the benchmark is the
same ADP-aware IP model.

## Mock Draft Simulation

Mock draft should be a supplementary experiment.

Purpose:

- show that the model can be used in a dynamic draft environment
- compare online draft policies when the available player pool changes after
  every pick
- demonstrate practical usability of IP and heuristics

Recommended usage:

- run on one representative season, such as 2026
- use `noisy_adp` opponents for stochastic simulation
- compare our methods: IP, Direct Greedy, Opportunity Cost Greedy
- keep this section smaller than the core IP and heuristic experiments

Mock draft should not be treated as the main validation because opponent
behavior is simulated rather than observed.

## Suggested Report Structure

1. Problem Description
2. Data Construction
3. Integer Programming Model
4. LP Relaxation and Shadow Price Interpretation
5. Computational Experiments
   - draft position sensitivity
   - ADP delta sensitivity
   - scoring system comparison
   - season comparison
6. Heuristic Methods and Optimal-Gap Evaluation
7. Optional Dynamic Mock Draft Simulation
8. Conclusion
