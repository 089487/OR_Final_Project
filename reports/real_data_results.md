# 2026 Real-Data Validation

The 2026 Yahoo and FanGraphs player pools are used as realistic sanity checks.
They are not the main experiment suite; the synthetic N1-N6 factor experiments
provide the main scalability evidence.

The table below is extracted from the existing benchmark summaries before the
full `experiments/benchmark/` folders were removed from the final repo.

| dataset | method | mean objective | mean optimality gap | max optimality gap | cases |
| --- | --- | ---: | ---: | ---: | ---: |
| yahoo_2026 | ADP-aware ILP | 7917.209 | 0.000 | 0.000 | 252 |
| yahoo_2026 | Opportunity Cost Greedy | 7767.732 | 149.477 | 255.700 | 252 |
| yahoo_2026 | Direct Greedy | 7662.866 | 254.343 | 373.000 | 252 |
| fangraph_2026 | ADP-aware ILP | 14642.927 | 0.000 | 0.000 | 252 |
| fangraph_2026 | Opportunity Cost Greedy | 14320.135 | 322.792 | 508.000 | 252 |
| fangraph_2026 | Direct Greedy | 14097.337 | 545.590 | 644.500 | 252 |

Opportunity Cost Greedy is closer to the ADP-aware ILP than Direct Greedy on
both validation datasets. Yahoo has mean optimality gaps of 149.477 points for
Opportunity Cost Greedy and 254.343 points for Direct Greedy. FanGraphs has mean
optimality gaps of 322.792 points for Opportunity Cost Greedy and 545.590 points
for Direct Greedy.

The no-ADP `Static IP` baseline is excluded from the compact validation table
because it solves a different problem. Its role is to estimate the cost of ADP
availability, not heuristic optimality.
