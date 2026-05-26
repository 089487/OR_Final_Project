# Synthetic Experiment Run Scripts

This file lists the commands for running each synthetic experiment scenario.

Before running any experiment:

```bash
source ~/myenv/bin/activate
```

For long runs, use `tmux`:

```bash
tmux new -s <session_name>
source ~/myenv/bin/activate
```

Synthetic outputs are ignored by git:

```text
data/synthetic/
experiments/synthetic/<scenario-output>/
```

The exception is `experiments/synthetic/scaling_summary/`, which is committed as
the final scaling evidence.

## N1 Baseline

Purpose: controlled baseline with normal points and roster-ratio positions.

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
  --time-limit 0 \
  --methods adp_aware_ilp,direct_greedy,opportunity_cost_greedy
```

Suggested tmux:

```bash
tmux new -s syn_N1
source ~/myenv/bin/activate
python scripts/run_synthetic_benchmark.py --experiment N1_baseline --outdir experiments/synthetic/N1_baseline --points-scenario normal --position-scenario roster_ratio --roster-scale 1 --num-teams 12 --player-demand-ratio 3 --sigma-adp 30 --delta 0 --seeds 0:10 --time-limit 0 --methods adp_aware_ilp,direct_greedy,opportunity_cost_greedy
```

## N2 Points Distribution

Purpose: compare normal, uniform, and high-low point distributions.

Run these three commands.

### N2 Normal

```bash
python scripts/run_synthetic_benchmark.py \
  --experiment N2_points_normal \
  --outdir experiments/synthetic/N2_points_distribution/normal \
  --points-scenario normal \
  --position-scenario roster_ratio \
  --roster-scale 1 \
  --num-teams 12 \
  --player-demand-ratio 3 \
  --sigma-adp 30 \
  --delta 0 \
  --seeds 0:10 \
  --time-limit 0 \
  --methods adp_aware_ilp,direct_greedy,opportunity_cost_greedy
```

### N2 Uniform

```bash
python scripts/run_synthetic_benchmark.py \
  --experiment N2_points_uniform \
  --outdir experiments/synthetic/N2_points_distribution/uniform \
  --points-scenario uniform \
  --position-scenario roster_ratio \
  --roster-scale 1 \
  --num-teams 12 \
  --player-demand-ratio 3 \
  --sigma-adp 30 \
  --delta 0 \
  --seeds 0:10 \
  --time-limit 0 \
  --methods adp_aware_ilp,direct_greedy,opportunity_cost_greedy
```

### N2 High-Low

```bash
python scripts/run_synthetic_benchmark.py \
  --experiment N2_points_high_low \
  --outdir experiments/synthetic/N2_points_distribution/high_low \
  --points-scenario high_low \
  --position-scenario roster_ratio \
  --roster-scale 1 \
  --num-teams 12 \
  --player-demand-ratio 3 \
  --sigma-adp 30 \
  --delta 0 \
  --seeds 0:10 \
  --time-limit 0 \
  --methods adp_aware_ilp,direct_greedy,opportunity_cost_greedy
```

Suggested tmux:

```bash
tmux new -s syn_N2
source ~/myenv/bin/activate
python scripts/run_synthetic_benchmark.py --experiment N2_points_normal --outdir experiments/synthetic/N2_points_distribution/normal --points-scenario normal --position-scenario roster_ratio --roster-scale 1 --num-teams 12 --player-demand-ratio 3 --sigma-adp 30 --delta 0 --seeds 0:10 --time-limit 0 --methods adp_aware_ilp,direct_greedy,opportunity_cost_greedy
python scripts/run_synthetic_benchmark.py --experiment N2_points_uniform --outdir experiments/synthetic/N2_points_distribution/uniform --points-scenario uniform --position-scenario roster_ratio --roster-scale 1 --num-teams 12 --player-demand-ratio 3 --sigma-adp 30 --delta 0 --seeds 0:10 --time-limit 0 --methods adp_aware_ilp,direct_greedy,opportunity_cost_greedy
python scripts/run_synthetic_benchmark.py --experiment N2_points_high_low --outdir experiments/synthetic/N2_points_distribution/high_low --points-scenario high_low --position-scenario roster_ratio --roster-scale 1 --num-teams 12 --player-demand-ratio 3 --sigma-adp 30 --delta 0 --seeds 0:10 --time-limit 0 --methods adp_aware_ilp,direct_greedy,opportunity_cost_greedy
```

## N3 Position Distribution

Purpose: compare roster flexibility and position-generation rules.

Run these four commands.

### N3 Uniform By Type

```bash
python scripts/run_synthetic_benchmark.py \
  --experiment N3_position_uniform_by_type \
  --outdir experiments/synthetic/N3_position_distribution/uniform_by_type \
  --points-scenario normal \
  --position-scenario uniform_by_type \
  --roster-scale 1 \
  --num-teams 12 \
  --player-demand-ratio 3 \
  --sigma-adp 30 \
  --delta 0 \
  --seeds 0:10 \
  --time-limit 0 \
  --methods adp_aware_ilp,direct_greedy,opportunity_cost_greedy
```

### N3 Point Flexible

```bash
python scripts/run_synthetic_benchmark.py \
  --experiment N3_position_point_flexible \
  --outdir experiments/synthetic/N3_position_distribution/point_flexible \
  --points-scenario normal \
  --position-scenario point_flexible \
  --roster-scale 1 \
  --num-teams 12 \
  --player-demand-ratio 3 \
  --sigma-adp 30 \
  --delta 0 \
  --seeds 0:10 \
  --time-limit 0 \
  --methods adp_aware_ilp,direct_greedy,opportunity_cost_greedy
```

### N3 Single Position

```bash
python scripts/run_synthetic_benchmark.py \
  --experiment N3_position_single_position \
  --outdir experiments/synthetic/N3_position_distribution/single_position \
  --points-scenario normal \
  --position-scenario single_position \
  --roster-scale 1 \
  --num-teams 12 \
  --player-demand-ratio 3 \
  --sigma-adp 30 \
  --delta 0 \
  --seeds 0:10 \
  --time-limit 0 \
  --methods adp_aware_ilp,direct_greedy,opportunity_cost_greedy
```

### N3 Roster Ratio

```bash
python scripts/run_synthetic_benchmark.py \
  --experiment N3_position_roster_ratio \
  --outdir experiments/synthetic/N3_position_distribution/roster_ratio \
  --points-scenario normal \
  --position-scenario roster_ratio \
  --roster-scale 1 \
  --num-teams 12 \
  --player-demand-ratio 3 \
  --sigma-adp 30 \
  --delta 0 \
  --seeds 0:10 \
  --time-limit 0 \
  --methods adp_aware_ilp,direct_greedy,opportunity_cost_greedy
```

Suggested tmux:

```bash
tmux new -s syn_N3
source ~/myenv/bin/activate
python scripts/run_synthetic_benchmark.py --experiment N3_position_uniform_by_type --outdir experiments/synthetic/N3_position_distribution/uniform_by_type --points-scenario normal --position-scenario uniform_by_type --roster-scale 1 --num-teams 12 --player-demand-ratio 3 --sigma-adp 30 --delta 0 --seeds 0:10 --time-limit 0 --methods adp_aware_ilp,direct_greedy,opportunity_cost_greedy
python scripts/run_synthetic_benchmark.py --experiment N3_position_point_flexible --outdir experiments/synthetic/N3_position_distribution/point_flexible --points-scenario normal --position-scenario point_flexible --roster-scale 1 --num-teams 12 --player-demand-ratio 3 --sigma-adp 30 --delta 0 --seeds 0:10 --time-limit 0 --methods adp_aware_ilp,direct_greedy,opportunity_cost_greedy
python scripts/run_synthetic_benchmark.py --experiment N3_position_single_position --outdir experiments/synthetic/N3_position_distribution/single_position --points-scenario normal --position-scenario single_position --roster-scale 1 --num-teams 12 --player-demand-ratio 3 --sigma-adp 30 --delta 0 --seeds 0:10 --time-limit 0 --methods adp_aware_ilp,direct_greedy,opportunity_cost_greedy
python scripts/run_synthetic_benchmark.py --experiment N3_position_roster_ratio --outdir experiments/synthetic/N3_position_distribution/roster_ratio --points-scenario normal --position-scenario roster_ratio --roster-scale 1 --num-teams 12 --player-demand-ratio 3 --sigma-adp 30 --delta 0 --seeds 0:10 --time-limit 0 --methods adp_aware_ilp,direct_greedy,opportunity_cost_greedy
```

## N4 Scaling

Purpose: test roster scale and player-pool size.

Run these combinations:

```text
roster-scale = 1, 2, 3
player-demand-ratio = 1, 3, 10
```

Suggested tmux:

```bash
tmux new -s syn_N4
source ~/myenv/bin/activate
```

Then run:

```bash
python scripts/run_synthetic_benchmark.py --experiment N4_scale_s1_ratio1 --outdir experiments/synthetic/N4_scaling/s1_ratio1 --points-scenario normal --position-scenario roster_ratio --roster-scale 1 --num-teams 12 --player-demand-ratio 1 --sigma-adp 30 --delta 0 --seeds 0:5 --time-limit 0 --methods adp_aware_ilp,direct_greedy,opportunity_cost_greedy
python scripts/run_synthetic_benchmark.py --experiment N4_scale_s1_ratio3 --outdir experiments/synthetic/N4_scaling/s1_ratio3 --points-scenario normal --position-scenario roster_ratio --roster-scale 1 --num-teams 12 --player-demand-ratio 3 --sigma-adp 30 --delta 0 --seeds 0:5 --time-limit 0 --methods adp_aware_ilp,direct_greedy,opportunity_cost_greedy
python scripts/run_synthetic_benchmark.py --experiment N4_scale_s1_ratio10 --outdir experiments/synthetic/N4_scaling/s1_ratio10 --points-scenario normal --position-scenario roster_ratio --roster-scale 1 --num-teams 12 --player-demand-ratio 10 --sigma-adp 30 --delta 0 --seeds 0:5 --time-limit 0 --methods adp_aware_ilp,direct_greedy,opportunity_cost_greedy
python scripts/run_synthetic_benchmark.py --experiment N4_scale_s2_ratio1 --outdir experiments/synthetic/N4_scaling/s2_ratio1 --points-scenario normal --position-scenario roster_ratio --roster-scale 2 --num-teams 12 --player-demand-ratio 1 --sigma-adp 30 --delta 0 --seeds 0:5 --time-limit 0 --methods adp_aware_ilp,direct_greedy,opportunity_cost_greedy
python scripts/run_synthetic_benchmark.py --experiment N4_scale_s2_ratio3 --outdir experiments/synthetic/N4_scaling/s2_ratio3 --points-scenario normal --position-scenario roster_ratio --roster-scale 2 --num-teams 12 --player-demand-ratio 3 --sigma-adp 30 --delta 0 --seeds 0:5 --time-limit 0 --methods adp_aware_ilp,direct_greedy,opportunity_cost_greedy
python scripts/run_synthetic_benchmark.py --experiment N4_scale_s2_ratio10 --outdir experiments/synthetic/N4_scaling/s2_ratio10 --points-scenario normal --position-scenario roster_ratio --roster-scale 2 --num-teams 12 --player-demand-ratio 10 --sigma-adp 30 --delta 0 --seeds 0:5 --time-limit 0 --methods adp_aware_ilp,direct_greedy,opportunity_cost_greedy
python scripts/run_synthetic_benchmark.py --experiment N4_scale_s3_ratio1 --outdir experiments/synthetic/N4_scaling/s3_ratio1 --points-scenario normal --position-scenario roster_ratio --roster-scale 3 --num-teams 12 --player-demand-ratio 1 --sigma-adp 30 --delta 0 --seeds 0:5 --time-limit 0 --methods adp_aware_ilp,direct_greedy,opportunity_cost_greedy
python scripts/run_synthetic_benchmark.py --experiment N4_scale_s3_ratio3 --outdir experiments/synthetic/N4_scaling/s3_ratio3 --points-scenario normal --position-scenario roster_ratio --roster-scale 3 --num-teams 12 --player-demand-ratio 3 --sigma-adp 30 --delta 0 --seeds 0:5 --time-limit 0 --methods adp_aware_ilp,direct_greedy,opportunity_cost_greedy
python scripts/run_synthetic_benchmark.py --experiment N4_scale_s3_ratio10 --outdir experiments/synthetic/N4_scaling/s3_ratio10 --points-scenario normal --position-scenario roster_ratio --roster-scale 3 --num-teams 12 --player-demand-ratio 10 --sigma-adp 30 --delta 0 --seeds 0:5 --time-limit 0 --methods adp_aware_ilp,direct_greedy,opportunity_cost_greedy
```

## N5 ADP Uncertainty

Purpose: test ADP noise and delta sensitivity.

Run one command per `sigma_adp`.

```bash
python scripts/run_synthetic_benchmark.py \
  --experiment N5_adp_sigma0 \
  --outdir experiments/synthetic/N5_adp_uncertainty/sigma0 \
  --points-scenario normal \
  --position-scenario roster_ratio \
  --roster-scale 1 \
  --num-teams 12 \
  --player-demand-ratio 3 \
  --sigma-adp 0 \
  --delta-min -10 \
  --delta-max 10 \
  --delta-step 1 \
  --seeds 0:10 \
  --time-limit 0 \
  --methods adp_aware_ilp,direct_greedy,opportunity_cost_greedy
```

Repeat with:

```text
sigma_adp = 10, 30, 60, 100
```

Suggested tmux:

```bash
tmux new -s syn_N5
source ~/myenv/bin/activate
python scripts/run_synthetic_benchmark.py --experiment N5_adp_sigma0 --outdir experiments/synthetic/N5_adp_uncertainty/sigma0 --points-scenario normal --position-scenario roster_ratio --roster-scale 1 --num-teams 12 --player-demand-ratio 3 --sigma-adp 0 --delta-min -10 --delta-max 10 --delta-step 1 --seeds 0:10 --time-limit 0 --methods adp_aware_ilp,direct_greedy,opportunity_cost_greedy
python scripts/run_synthetic_benchmark.py --experiment N5_adp_sigma10 --outdir experiments/synthetic/N5_adp_uncertainty/sigma10 --points-scenario normal --position-scenario roster_ratio --roster-scale 1 --num-teams 12 --player-demand-ratio 3 --sigma-adp 10 --delta-min -10 --delta-max 10 --delta-step 1 --seeds 0:10 --time-limit 0 --methods adp_aware_ilp,direct_greedy,opportunity_cost_greedy
python scripts/run_synthetic_benchmark.py --experiment N5_adp_sigma30 --outdir experiments/synthetic/N5_adp_uncertainty/sigma30 --points-scenario normal --position-scenario roster_ratio --roster-scale 1 --num-teams 12 --player-demand-ratio 3 --sigma-adp 30 --delta-min -10 --delta-max 10 --delta-step 1 --seeds 0:10 --time-limit 0 --methods adp_aware_ilp,direct_greedy,opportunity_cost_greedy
python scripts/run_synthetic_benchmark.py --experiment N5_adp_sigma60 --outdir experiments/synthetic/N5_adp_uncertainty/sigma60 --points-scenario normal --position-scenario roster_ratio --roster-scale 1 --num-teams 12 --player-demand-ratio 3 --sigma-adp 60 --delta-min -10 --delta-max 10 --delta-step 1 --seeds 0:10 --time-limit 0 --methods adp_aware_ilp,direct_greedy,opportunity_cost_greedy
python scripts/run_synthetic_benchmark.py --experiment N5_adp_sigma100 --outdir experiments/synthetic/N5_adp_uncertainty/sigma100 --points-scenario normal --position-scenario roster_ratio --roster-scale 1 --num-teams 12 --player-demand-ratio 3 --sigma-adp 100 --delta-min -10 --delta-max 10 --delta-step 1 --seeds 0:10 --time-limit 0 --methods adp_aware_ilp,direct_greedy,opportunity_cost_greedy
```

## N6 Large-Scale Stress Test

Purpose: intentionally create large instances where Gurobi may become slow or
fail to prove optimality.

Use `tmux`.

```bash
tmux new -s syn_N6
source ~/myenv/bin/activate
```

### N6 Stress Small

```bash
python scripts/run_synthetic_benchmark.py \
  --experiment N6_stress_small \
  --outdir experiments/synthetic/N6_large_scale_stress/stress_small \
  --points-scenario high_low \
  --position-scenario single_position \
  --roster-scale 3 \
  --num-teams 12 \
  --player-demand-ratio 10 \
  --sigma-adp 60 \
  --delta 0 \
  --seeds 0:3 \
  --time-limit 300 \
  --methods adp_aware_ilp,direct_greedy,opportunity_cost_greedy
```

### N6 Stress Medium

This is the main stress comparison where IP and heuristics are still run on
the same instances.  The IP has a 30-minute time limit so the result can show
whether Gurobi proves optimality, returns an incumbent with a MIP gap, or fails
to find a solution within the limit.

```bash
python scripts/run_synthetic_benchmark.py \
  --experiment N6_stress_medium \
  --outdir experiments/synthetic/N6_large_scale_stress/stress_medium \
  --points-scenario high_low \
  --position-scenario single_position \
  --roster-scale 4 \
  --num-teams 15 \
  --player-demand-ratio 10 \
  --sigma-adp 60 \
  --delta 0 \
  --seeds 0:3 \
  --time-limit 1800 \
  --methods adp_aware_ilp,direct_greedy,opportunity_cost_greedy
```

### N6 Stress Large

This may be memory-heavy.  Start with heuristics, then optionally add IP.

```bash
python scripts/run_synthetic_benchmark.py \
  --experiment N6_stress_large_heuristic \
  --outdir experiments/synthetic/N6_large_scale_stress/stress_large_heuristic \
  --points-scenario high_low \
  --position-scenario single_position \
  --roster-scale 6 \
  --num-teams 15 \
  --player-demand-ratio 15 \
  --sigma-adp 60 \
  --delta 0 \
  --seeds 0:3 \
  --time-limit 300 \
  --methods direct_greedy,opportunity_cost_greedy
```

Optional IP attempt:

```bash
python scripts/run_synthetic_benchmark.py \
  --experiment N6_stress_large_ip \
  --outdir experiments/synthetic/N6_large_scale_stress/stress_large_ip \
  --points-scenario high_low \
  --position-scenario single_position \
  --roster-scale 6 \
  --num-teams 15 \
  --player-demand-ratio 15 \
  --sigma-adp 60 \
  --delta 0 \
  --seeds 0:1 \
  --time-limit 1800 \
  --methods adp_aware_ilp
```

### N6 Stress XLarge

Heuristic-only by default.

```bash
python scripts/run_synthetic_benchmark.py \
  --experiment N6_stress_xlarge_heuristic \
  --outdir experiments/synthetic/N6_large_scale_stress/stress_xlarge_heuristic \
  --points-scenario high_low \
  --position-scenario single_position \
  --roster-scale 10 \
  --num-teams 20 \
  --player-demand-ratio 20 \
  --sigma-adp 60 \
  --delta 0 \
  --seeds 0:3 \
  --time-limit 300 \
  --methods direct_greedy,opportunity_cost_greedy
```

Optional IP attempt only if you intentionally want to test memory/time limits:

```bash
python scripts/run_synthetic_benchmark.py \
  --experiment N6_stress_xlarge_ip_tl1800 \
  --outdir experiments/synthetic/N6_large_scale_stress/stress_xlarge_ip_tl1800 \
  --points-scenario high_low \
  --position-scenario single_position \
  --roster-scale 10 \
  --num-teams 20 \
  --player-demand-ratio 20 \
  --sigma-adp 60 \
  --delta 0 \
  --seeds 0:1 \
  --time-limit 1800 \
  --methods adp_aware_ilp
```

### N6 Stress Timeout Target

This is the deliberately oversized instance. The goal is to produce a case
where heuristics finish but the ADP-aware ILP either hits the 30-minute time
limit or fails due to memory/model-size pressure.

Heuristic run:

```bash
python scripts/run_synthetic_benchmark.py \
  --experiment N6_stress_timeout_target_heuristic \
  --outdir experiments/synthetic/N6_large_scale_stress/stress_timeout_target_heuristic \
  --points-scenario high_low \
  --position-scenario single_position \
  --roster-scale 16 \
  --num-teams 24 \
  --player-demand-ratio 30 \
  --sigma-adp 60 \
  --delta 0 \
  --seeds 0:3 \
  --time-limit 300 \
  --methods direct_greedy,opportunity_cost_greedy
```

IP stress probe:

```bash
python scripts/run_synthetic_benchmark.py \
  --experiment N6_stress_timeout_target_ip \
  --outdir experiments/synthetic/N6_large_scale_stress/stress_timeout_target_ip \
  --points-scenario high_low \
  --position-scenario single_position \
  --roster-scale 16 \
  --num-teams 24 \
  --player-demand-ratio 30 \
  --sigma-adp 60 \
  --delta 0 \
  --seeds 0:1 \
  --time-limit 1800 \
  --methods adp_aware_ilp
```

## Synthetic Scaling Summary

After running N4 and N6, combine their separate benchmark folders into one
scaling summary. This does not rerun any optimization; it only reads existing
`summary/benchmark_results.csv` files.

```bash
python scripts/summarize_synthetic_scaling.py \
  --roots experiments/synthetic/N4_scaling experiments/synthetic/N6_large_scale_stress \
  --outdir experiments/synthetic/scaling_summary
```

Expected outputs:

```text
experiments/synthetic/scaling_summary/
  scaling_benchmark_results.csv
  scaling_summary_by_method_size.csv
  ip_status_by_variable_count.csv
  runtime_scaling_table.csv
  runtime_scaling_table.md
  runtime_by_variable_count.png
  heuristic_gap_by_variable_count.png
  ip_status_mip_gap_by_variable_count.png
```
