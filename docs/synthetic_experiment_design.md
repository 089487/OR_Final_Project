# New Synthetic Factor Experiment Plan

This document defines the revised synthetic benchmark design.

Main change:

```text
points and positions are generated independently by default.
```

The synthetic data should not assume that certain positions naturally have
higher or lower points.  Position effects are introduced only through specific
position-distribution scenarios, such as rewarding multi-position eligibility.

## 1. Fixed Roster Ratio

The base roster requirement is:

```python
ROSTER_REQUIREMENTS = {
    "C": 1,
    "1B": 1,
    "2B": 1,
    "3B": 1,
    "SS": 1,
    "OF": 3,
    "Util": 1,
    "SP": 5,
    "RP": 2,
}
```

Base roster size:

```text
r = 16
```

Base roster ratios:

```text
C:    1/16
1B:   1/16
2B:   1/16
3B:   1/16
SS:   1/16
OF:   3/16
Util: 1/16
SP:   5/16
RP:   2/16
```

When scaling roster size, scale these requirements proportionally.

Example with scale factor `s`:

```text
C    = 1s
1B   = 1s
2B   = 1s
3B   = 1s
SS   = 1s
OF   = 3s
Util = 1s
SP   = 5s
RP   = 2s
r    = 16s
```

Recommended roster scale levels:

```text
s = 1, 2, 3
r = 16, 32, 48
```

## 2. Player-To-Draft-Demand Ratio

Let:

```text
n = number of players
r = roster size per team
t = number of teams
D = r * t = total drafted players in the league
```

The experiment controls player pool size by the player-to-demand ratio:

```text
player-demand-ratio = n / D = 1, 3, 10
```

Equivalently:

```text
n = D
n = 3D
n = 10D
```

Interpretation:

```text
1:1   almost every player must be drafted; feasibility pressure is high.
3:1   moderate replacement pool.
10:1  large player pool; IP model is much larger and heuristics have many choices.
```

Example when `r = 16`, `t = 12`:

```text
D = 192
n / D = 1   => n = 192
n / D = 3   => n = 576
n / D = 10  => n = 1920
```

## 3. Points Generation

Points are generated independently from positions unless a scenario explicitly
links them.

Fixed point range:

```text
min_points = 10
max_points = 800
```

### Scenario P1: Normal Distribution

Generate:

```text
points_i ~ Normal(mu, sigma)
points_i = clip(points_i, 10, 800)
```

Recommended parameters:

```text
mu = 400
sigma = 120
```

Purpose:

```text
Most players are around the middle, with fewer very high or very low values.
```

### Scenario P2: Uniform Distribution

Generate:

```text
points_i ~ Uniform(10, 800)
```

Purpose:

```text
All point levels are equally likely. This removes natural clustering and creates
a broad value spread.
```

### Scenario P3: High-Low Distribution

Mixture ratio:

```text
high : low = 1 : 9
```

Definition:

```text
high players have points > 500
low players have points <= 500
```

Generate:

```text
with probability 0.1:
    points_i ~ Uniform(500, 800)
with probability 0.9:
    points_i ~ Uniform(10, 500)
```

Purpose:

```text
Only a small fraction of players are high-value. Missing elite players should
hurt more, and ADP availability may become more important.
```

## 4. Position Generation

Position generation controls roster feasibility and flexibility.  It is
separate from points generation by default.

The final CSV should store eligible positions as semicolon-separated values:

```text
C
2B;SS
OF;1B
SP
RP
SP;RP
```

### Scenario E1: Uniform By Player Type

First decide whether the player is a hitter or pitcher.  Use the roster ratio to
keep the hitter/pitcher supply roughly realistic:

```text
hitter roster slots = C + 1B + 2B + 3B + SS + OF + Util = 9
pitcher roster slots = SP + RP = 7

P(hitter) = 9/16
P(pitcher) = 7/16
```

For hitters, sample eligible-position pattern uniformly from a predefined list:

```text
C
1B
2B
3B
SS
OF
1B;3B
2B;SS
2B;3B
3B;SS
1B;OF
OF;Util
```

For pitchers, sample uniformly from:

```text
SP
RP
SP;RP
```

Purpose:

```text
General random eligibility while keeping hitters and pitchers separate.
```

### Scenario E2: Higher Points Encourage More Positions

This is the only position scenario that intentionally links points and
eligibility.

Sort players by points percentile:

```text
top 20%      high-value players
middle 50%   medium-value players
bottom 30%   low-value players
```

Assign number of eligible positions:

```text
top 20%:
    hitters get 2 or 3 eligible positions with high probability
    pitchers may get SP;RP with moderate probability

middle 50%:
    mostly 1 or 2 eligible positions

bottom 30%:
    mostly single-position players
```

Recommended probabilities for hitters:

```text
top 20%:
    1 position: 20%
    2 positions: 50%
    3 positions: 30%

middle 50%:
    1 position: 60%
    2 positions: 35%
    3 positions: 5%

bottom 30%:
    1 position: 90%
    2 positions: 10%
    3 positions: 0%
```

Recommended probabilities for pitchers:

```text
top 20%:
    SP/RP flex probability = 20%

middle 50%:
    SP/RP flex probability = 10%

bottom 30%:
    SP/RP flex probability = 3%
```

Purpose:

```text
Tests a favorable world for heuristics: high-value players are also easier to
fit into the roster.
```

### Scenario E3: Single-Position Only

Every player has exactly one eligible position.

For hitters:

```text
C, 1B, 2B, 3B, SS, OF
```

For pitchers:

```text
SP, RP
```

Use hitter/pitcher split:

```text
P(hitter) = 9/16
P(pitcher) = 7/16
```

Purpose:

```text
Lowest flexibility setting.  This should make greedy mistakes harder to repair.
```

### Scenario E4: Roster-Ratio Position Mix

Generate player positions according to roster demand ratios.

Use roster slots as weights:

```text
C: 1
1B: 1
2B: 1
3B: 1
SS: 1
OF: 3
SP: 5
RP: 2
```

Normalize by:

```text
1 + 1 + 1 + 1 + 1 + 3 + 5 + 2 = 15
```

So:

```text
C:  1/15
1B: 1/15
2B: 1/15
3B: 1/15
SS: 1/15
OF: 3/15
SP: 5/15
RP: 2/15
```

Note:

```text
Util is not a primary player position.
```

Purpose:

```text
Player supply roughly matches roster demand. For example, OF has 3 roster slots,
so OF appears about three times as often as C.
```

## 5. ADP Generation

ADP is generated from points rank plus noise.

```text
true_rank_i = rank players by descending points
adp_i = true_rank_i + Normal(0, sigma_adp)
adp_i = clip(adp_i, 1, n)
```

Recommended ADP noise levels:

```text
sigma_adp = 0, 10, 30, 60, 100
```

Interpretation:

```text
sigma_adp = 0    ADP perfectly follows points.
sigma_adp = 100  ADP is noisy and may create bargains or traps.
```

## 6. Core Factors

Recommended core factors for N1-N5:

```text
factor                         levels
points scenario                normal, uniform, high_low
position scenario              uniform_by_type, point_flexible,
                               single_position, roster_ratio
player-to-demand ratio n/D     1, 3, 10
roster scale s                 1, 2, 3
league size t                  12 in the current main grid
ADP noise sigma_adp            0, 10, 30, 60, 100
ADP delta                      -10..10, stride 1
random seed                    5 or 10 seeds per setting
```

N6 is the stress-test extension. It intentionally uses larger roster scales,
larger player-to-demand ratios, league sizes 12/15/20, and 3 seeds per stress
level so that the large instances are still practical to run.

The command-line flag is `--player-demand-ratio`, and it means `n / D`.

## 7. Recommended Experiment Sets

### Experiment N1: Baseline Synthetic Benchmark

Purpose: compare methods on controlled but not extreme synthetic data.

Fixed:

```text
points scenario = normal
position scenario = roster_ratio
roster scale s = 1
league size t = 12
n / D = 3
sigma_adp = 30
delta = 0
seeds = 10
```

Methods:

```text
ADP-aware ILP
Direct Greedy
Opportunity Cost Greedy
```

Metrics:

```text
objective
runtime
optimality gap
selected roster
```

### Experiment N2: Points Distribution

Purpose: test whether heuristic performance changes when value distribution
changes.

Fixed:

```text
position scenario = roster_ratio
roster scale s = 1
league size t = 12
n / D = 3
sigma_adp = 30
delta = 0
seeds = 10
```

Vary:

```text
points scenario = normal, uniform, high_low
```

Expected:

```text
high_low should make missing high-value players more costly.
uniform may create a broader spread and more ADP bargains.
normal should be the most stable middle case.
```

### Experiment N3: Position Distribution

Purpose: test whether roster flexibility and position scarcity change heuristic
quality.

Fixed:

```text
points scenario = normal
roster scale s = 1
league size t = 12
n / D = 3
sigma_adp = 30
delta = 0
seeds = 10
```

Vary:

```text
position scenario = uniform_by_type, point_flexible,
                    single_position, roster_ratio
```

Expected:

```text
single_position should be hardest for greedy methods.
point_flexible should be easiest because high-value players are flexible.
roster_ratio is the cleanest demand-matched baseline.
```

### Experiment N4: Scaling

Purpose: identify when Gurobi becomes slow or cannot prove optimality.

Fixed:

```text
points scenario = normal
position scenario = roster_ratio
league size t = 12
sigma_adp = 30
delta = 0
seeds = 5
```

Vary:

```text
roster scale s = 1, 2, 3
n / D = 1, 3, 10
```

Metrics:

```text
runtime
IP status
MIPGap
objective
heuristic optimality gap when IP is optimal
gap to best bound when IP times out
```

### Experiment N5: ADP Uncertainty

Purpose: test sensitivity to draft-rank noise.

Fixed:

```text
points scenario = normal
position scenario = roster_ratio
roster scale s = 1
league size t = 12
n / D = 3
seeds = 10
```

Vary:

```text
sigma_adp = 0, 10, 30, 60, 100
delta = -10..10, stride 1
```

Metrics:

```text
objective by sigma_adp and delta
heuristic optimality gap
runtime
```

### Experiment N6: Large-Scale Stress Test

Purpose: intentionally create instances where the ADP-aware ILP becomes slow,
hits the time limit, or cannot prove optimality.  This experiment is used to
show why scalable heuristics are necessary.

Use this experiment after the smaller synthetic benchmarks are working.

Fixed:

```text
points scenario = high_low
position scenario = single_position
sigma_adp = 60
delta = 0
seeds = 3
```

Why these fixed settings:

```text
high_low:
  only a small fraction of players are high-value, so missing elite players is
  costly.

single_position:
  roster flexibility is low, so greedy mistakes are harder to repair.

sigma_adp = 60:
  ADP availability is noisy enough to create uncertainty.

large n and large r:
  directly increase the number of z_i,round variables.
```

Stress ladder:

```text
level                  roster scale s   r     t    D = r*t   n/D   n
stress_small           3                48    12   576       10    5,760
stress_medium          4                64    15   960       10    9,600
stress_large           6                96    15   1,440     15    21,600
stress_xlarge          10               160   20   3,200     20    64,000
stress_timeout_target  16               256   24   6,144     30    184,320
```

Approximate single-team IP variable count:

```text
variables ~= n * (1 + p + r)
p = 9
```

```text
level                  n        r     approximate variables
stress_small           5,760    48    334,080
stress_medium          9,600    64    710,400
stress_large           21,600   96    2,289,600
stress_xlarge          64,000   160   10,880,000
stress_timeout_target  184,320  256   49,029,120
```

Recommended method policy:

```text
stress_small:
  run ADP-aware ILP, Direct Greedy, Opportunity Cost Greedy

stress_medium:
  run ADP-aware ILP, Direct Greedy, Opportunity Cost Greedy with a 30-minute
  IP time limit

stress_large:
  heuristic-only by default

stress_xlarge:
  heuristic-only by default, with optional 30-minute ADP-aware ILP probe

stress_timeout_target:
  heuristic-only by default, plus one explicit ADP-aware ILP probe with a
  30-minute time limit when the goal is to demonstrate timeout or memory stress
```

Metrics:

```text
runtime
IP status
MIPGap
best_bound
objective
heuristic runtime
heuristic objective
gap to best bound when IP times out
memory/resource failure indicator
```

Expected:

```text
IP should become slow or fail to prove optimality as stress level increases.
Heuristics should still produce feasible rosters much faster.
```

## 8. Output Metrics

For every method:

```text
objective
runtime_seconds
status
selected roster
```

For IP:

```text
MIPGap
best_bound
solved_to_optimality
```

For heuristics when IP is optimal:

```text
optimal_gap = (objective_ADP_aware_ILP - objective_heuristic) / objective_ADP_aware_ILP
```

For IP timeout cases:

```text
gap_to_best_bound = (best_bound - objective_heuristic) / best_bound
```

## 9. Recommended Plots

Use `scripts/summarize_synthetic_scaling.py` after N4/N6 because those
experiments are intentionally split across multiple output folders.

```text
runtime_by_variable_count.png
heuristic_gap_by_variable_count.png
objective_by_points_scenario.png
gap_by_points_scenario.png
gap_by_position_scenario.png
runtime_by_player_to_demand_ratio.png
runtime_by_roster_scale.png
ip_solved_rate_by_scale.png
mip_gap_by_scale.png
objective_by_adp_noise_delta.png
gap_by_adp_noise.png
```

## 10. Expected Narrative

This revised synthetic design supports the following project story:

```text
1. Points and positions can be controlled independently.
2. IP provides the optimal benchmark on manageable synthetic instances.
3. Gurobi becomes difficult as roster scale and player pool size increase.
4. Direct Greedy is fastest but can suffer in low-flexibility position settings.
5. Opportunity Cost Greedy should be more robust under ADP noise and scarce
   roster feasibility.
6. Synthetic stress tests show why heuristics are useful beyond real 2026 data.
```
