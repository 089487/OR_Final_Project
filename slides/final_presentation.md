---
marp: true
theme: default
paginate: true
size: 16:9
math: mathjax
---

# Scalable Fantasy Baseball Draft Optimization

## Exact ADP-Aware ILP and Opportunity-Cost Greedy Heuristics

#### Group 4

B13705051 周孟承  
B13902103 鄭宇宏  
B13303153 詹舒宇  
B11705039 李盈盈

---

## Motivation

- Fantasy baseball drafts are sequential decisions under uncertainty.
- A manager must fill roster positions while accounting for player value, eligibility, and draft availability.
- ADP changes the problem: a high-value player may not be available later.
- We compare exact optimization with scalable greedy heuristics.

---

## Methods

| Method | Role | Main Idea |
| --- | --- | --- |
| ADP-aware ILP | Exact benchmark | Optimize roster, pick, eligibility, and ADP constraints |
| Direct Greedy | Simple benchmark heuristic | Fill the scarcest open position first |
| Opportunity Cost Greedy | Proposed scalable heuristic | Draft where waiting causes the largest value loss |

---

## ADP-Aware ILP

Decision variables:

- $y_i$: whether player $i$ is drafted.
- $x_{ip}$: whether player $i$ is assigned to position $p$.
- $z_{ik}$: whether player $i$ is selected with owned pick $k$.

Objective:

$$
\max \sum_i V_i y_i
$$

Key availability rule:

$$
z_{ik}=0 \quad \text{if } A_i+\delta<S_k
$$

---

## Direct Greedy

Direct Greedy is the simple benchmark heuristic.

For every open position:

$$
\text{scarcity ratio}
=
\frac{\text{remaining slots}}{\text{available eligible players}}
$$

Then it drafts:

- the position with largest scarcity ratio;
- the highest-point currently available player for that position.

---

## Opportunity Cost Greedy

Opportunity Cost Greedy is our proposed scalable heuristic.

For each open position:

$$
\text{opportunity cost}
=
\text{best current points}
-
\text{best next-pick points}
$$

It also uses a feasibility fallback when:

$$
\text{current count} \le \text{remaining slots}
\quad \text{or} \quad
\text{future count} < \text{remaining slots}
$$

---

## Implementation

Both heuristics use:

- one max-heap per roster position;
- lazy deletion for selected or expired players;
- ADP expiration sorted by `ADP + delta`;
- active player counts by position.

Approximate heuristic complexity:

$$
O(ne \log n + rp \log n)
$$

---

## Experiment Design

Real-data validation:

- 2026 Yahoo player pool.
- 2026 FanGraphs player pool.

Synthetic experiments:

- N1 baseline.
- N2 points distribution.
- N3 position distribution.
- N4 scaling.
- N5 ADP uncertainty.
- N6 large-scale stress test.

---

## Heuristic Quality

Opportunity Cost Greedy stays closer to the exact benchmark.

| Experiment | Opportunity Cost Greedy gap | Direct Greedy gap |
| --- | ---: | ---: |
| N1 baseline | 1.919% | 4.785% |
| N2 high-low points | 2.867% | 8.390% |
| N4 scaling | 1.623% | 4.177% |
| N5 ADP uncertainty | 1.557% | 4.063% |

---

## Scaling Results

| Instance | Approx. variables | ADP-aware ILP | Opportunity Cost Greedy | Direct Greedy |
| --- | ---: | ---: | ---: | ---: |
| stress_large | 2,289,600 | 41.131s | 1.008s | 0.926s |
| stress_xlarge | 10,880,000 | 299.430s | 2.965s | 2.705s |
| timeout_target | 49,029,120 | interrupted | 9.381s | 8.744s |

Exact optimization provides a benchmark, but heuristic scalability is much stronger.

---

## Real-Data Validation

| Dataset | Method | Mean objective | Mean gap |
| --- | --- | ---: | ---: |
| Yahoo 2026 | ADP-aware ILP | 7917.209 | 0.000 |
| Yahoo 2026 | Opportunity Cost Greedy | 7767.732 | 149.477 |
| Yahoo 2026 | Direct Greedy | 7662.866 | 254.343 |
| FanGraphs 2026 | ADP-aware ILP | 14642.927 | 0.000 |
| FanGraphs 2026 | Opportunity Cost Greedy | 14320.135 | 322.792 |
| FanGraphs 2026 | Direct Greedy | 14097.337 | 545.590 |

---

## Conclusion

- ADP-aware ILP is the exact benchmark for manageable instances.
- Direct Greedy is a simple benchmark heuristic.
- Opportunity Cost Greedy is the proposed scalable heuristic.
- Opportunity Cost Greedy consistently reduces optimality gaps.
- Large synthetic experiments show why scalable heuristics are necessary.

