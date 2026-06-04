# 2026 Real-Data Validation

The 2026 Yahoo and FanGraphs player pools are used as realistic sanity checks.
They are not the main experiment suite; the synthetic N1-N6 factor experiments
provide the main scalability evidence.

After updating the scoring weights, the processed Yahoo and FanGraphs player
pools were rebuilt and the real-data benchmark was rerun for the representative
case used in the report: `delta = 0` and `draft_position = 6`.

| dataset | method | optimal_gap_ratio |
| --- | --- | ---: |
| yahoo_2026 | Opportunity Cost Greedy | 0.50% |
| yahoo_2026 | Direct Greedy | 3.24% |
| fangraph_2026 | Opportunity Cost Greedy | 1.24% |
| fangraph_2026 | Direct Greedy | 3.36% |

Opportunity Cost Greedy is closer to the ADP-aware ILP than Direct Greedy on
both validation datasets. In the representative Yahoo case, Opportunity Cost
Greedy reduces the optimal gap ratio from 3.24% to 0.50%. In the representative
FanGraphs case, it reduces the optimal gap ratio from 3.36% to 1.24%.

The no-ADP `Static IP` baseline is excluded from the compact validation table
because it solves a different problem. Its role is to estimate the cost of ADP
availability, not heuristic optimality.
