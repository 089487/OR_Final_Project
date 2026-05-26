# Synthetic Experiment Notes

These notes correspond to the rerun after updating Opportunity Cost Greedy with
a feasibility fallback. Older notes from the pre-fallback heuristic were removed
to avoid mixing stale infeasibility results with the final experiment results.

## N1 Baseline

- Completed 10 seeds with all methods feasible/OPTIMAL.
- ADP-aware ILP mean objective: 9228.582, mean runtime: 0.071s, MIPGap: 0.
- Opportunity Cost Greedy mean objective: 9051.306, mean gap: 1.919%, mean runtime: 0.029s.
- Direct Greedy mean objective: 8786.931, mean gap: 4.785%, mean runtime: 0.027s.
- No NaN objectives/runtimes or infeasible cases. Baseline behavior remains reasonable after the feasibility fallback.

## N2 Points Distribution

- Completed normal, uniform, and high_low scenarios with 10 seeds each. All 90 method runs are feasible/OPTIMAL.
- No NaN objectives or runtimes. ADP-aware ILP MIPGap is 0 for all IP runs.
- Normal: ADP-aware ILP mean objective 9228.582; Opportunity Cost Greedy gap 1.919%; Direct Greedy gap 4.785%.
- Uniform: ADP-aware ILP mean objective 11440.292; Opportunity Cost Greedy gap 1.439%; Direct Greedy gap 3.243%.
- High-low: ADP-aware ILP mean objective 9137.382; Opportunity Cost Greedy gap 2.867%; Direct Greedy gap 8.390%.
- Main observation: high-low remains the hardest points scenario for greedy methods, especially Direct Greedy. Opportunity Cost Greedy is still consistently closer to IP.

## N3 Position Distribution

- Completed uniform_by_type, point_flexible, single_position, and roster_ratio scenarios with 10 seeds each. All 120 method runs are feasible/OPTIMAL.
- No NaN objectives or runtimes. ADP-aware ILP MIPGap is 0 for all IP runs.
- Opportunity Cost Greedy gaps: uniform_by_type 1.074%, point_flexible 1.344%, single_position 0.939%, roster_ratio 1.919%.
- Direct Greedy gaps: uniform_by_type 4.890%, point_flexible 5.364%, single_position 5.107%, roster_ratio 4.785%.
- Main observation: position distribution does not create feasibility issues after the fallback. Opportunity Cost Greedy remains consistently closer to IP than Direct Greedy.

## N4 Scaling

- Completed 9 scale/ratio settings with 5 seeds each. All 135 method runs are feasible/OPTIMAL.
- The previous Opportunity Cost Greedy infeasibility in tight supply cases is resolved: Opportunity Cost Greedy is now OPTIMAL in 45/45 runs.
- No NaN objectives or runtimes. ADP-aware ILP MIPGap is 0 for all IP runs.
- Across all N4 settings, ADP-aware ILP mean runtime is 0.644s with max runtime 4.915s.
- Opportunity Cost Greedy mean gap is 1.623% and mean runtime is 0.093s; max gap is 3.714%.
- Direct Greedy mean gap is 4.177% and mean runtime is 0.088s; max gap is 10.349%.
- As instance size grows within N4, IP runtime increases more sharply than both heuristics, while Opportunity Cost Greedy stays closer to the ADP-aware ILP objective than Direct Greedy.

## N5 ADP Uncertainty

- Completed sigma_adp settings 0, 10, 30, 60, and 100 with 10 seeds and delta -10..10. All 3150 method runs are feasible/OPTIMAL.
- No NaN objectives or runtimes. ADP-aware ILP MIPGap is 0 for all IP runs.
- Opportunity Cost Greedy mean gap is 1.557% and mean runtime is 0.029s; max gap is 5.792%.
- Direct Greedy mean gap is 4.063% and mean runtime is 0.027s; max gap is 9.460%.
- Gap by ADP noise for Opportunity Cost Greedy: sigma 0 = 0.416%, 10 = 0.992%, 30 = 1.800%, 60 = 2.429%, 100 = 2.146%.
- Gap by ADP noise for Direct Greedy: sigma 0 = 1.721%, 10 = 3.342%, 30 = 5.029%, 60 = 5.728%, 100 = 4.496%.
- Main observation: larger ADP uncertainty generally makes the greedy methods farther from the ADP-aware ILP, but Opportunity Cost Greedy remains substantially closer than Direct Greedy.

## N6 Large Scale Stress

- Completed the default N6 rerun after the Opportunity Cost Greedy feasibility fallback. The preserved IP-only large/xlarge/timeout-target outputs were not rerun.
- stress_small: all methods OPTIMAL for 3 seeds. ADP-aware ILP mean runtime 4.346s; Opportunity Cost Greedy gap 1.328% and runtime 0.286s; Direct Greedy gap 2.551% and runtime 0.330s.
- stress_medium: all methods OPTIMAL for 3 seeds. ADP-aware ILP mean runtime 6.498s; Opportunity Cost Greedy gap 0.759% and runtime 0.449s; Direct Greedy gap 1.603% and runtime 0.418s.
- stress_large_heuristic: heuristics only, 2,289,600 approximate variables. Opportunity Cost Greedy runtime 1.008s; Direct Greedy runtime 0.926s.
- stress_xlarge_heuristic: heuristics only, 10,880,000 approximate variables. Opportunity Cost Greedy runtime 2.965s; Direct Greedy runtime 2.705s.
- stress_timeout_target_heuristic: heuristics only, 49,029,120 approximate variables. Opportunity Cost Greedy runtime 9.381s; Direct Greedy runtime 8.744s.
- Preserved IP stress results: stress_large_ip solved OPTIMAL in 41.131s at 2,289,600 approximate variables; stress_xlarge_ip_tl1800 solved OPTIMAL in 299.430s at 10,880,000 approximate variables; timeout_target IP was manually interrupted before producing benchmark_results.csv.
- Main observation: the final stress results show the intended scale separation. IP remains exact on large/xlarge but runtime grows sharply, while both heuristics finish in seconds even at the timeout-target scale.

## Scaling Summary

- Regenerated experiments/synthetic/scaling_summary after N6 completed.
- Updated outputs include scaling_benchmark_results.csv, scaling_summary_by_method_size.csv, ip_status_by_variable_count.csv, runtime_scaling_table.csv, runtime_scaling_table.md, runtime_by_variable_count.png, heuristic_gap_by_variable_count.png, and ip_status_mip_gap_by_variable_count.png.
- runtime_scaling_table.md explicitly marks the timeout_target ADP-aware ILP row as MANUAL_INTERRUPT_NO_OUTPUT with no benchmark_results.csv, while the matching heuristic rows are OPTIMAL and complete in under 10 seconds.
