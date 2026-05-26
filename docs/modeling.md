# ADP-Aware Draft Optimization Model

This document describes the exact benchmark implemented by `src/ip_model.py`
and the shared draft utilities in `src/draft_core.py`.

## Sets

- \(I\): available players.
- \(P\): roster positions.
- \(K\): picks owned by one fantasy team.

For a snake draft with \(M\) teams and draft position \(j\), the overall pick in
round \(r\) is:

\[
S_r =
\begin{cases}
(r-1)M+j, & r \text{ odd},\\
rM-j+1, & r \text{ even}.
\end{cases}
\]

`snake_picks()` returns the sequence of owned picks.

## Parameters

- \(V_i\): projected fantasy points for player \(i\).
- \(E_{ip}\): 1 when player \(i\) is eligible at roster position \(p\).
- \(R_p\): required roster slots at position \(p\).
- \(A_i\): average draft position for player \(i\).
- \(S_k\): overall pick number for owned pick \(k\).
- \(\delta\): ADP availability buffer.

The default roster is:

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

`Util` is available to hitters only. Pitchers cannot be assigned to `Util`.

## Decision Variables

\[
y_i =
\begin{cases}
1, & \text{if player } i \text{ is drafted},\\
0, & \text{otherwise},
\end{cases}
\]

\[
x_{ip} =
\begin{cases}
1, & \text{if player } i \text{ is assigned to position } p,\\
0, & \text{otherwise},
\end{cases}
\]

\[
z_{ik} =
\begin{cases}
1, & \text{if player } i \text{ is selected with owned pick } k,\\
0, & \text{otherwise}.
\end{cases}
\]

## ADP-Aware ILP

Maximize projected roster points:

\[
\max \sum_{i\in I} V_i y_i.
\]

Each owned pick selects exactly one player:

\[
\sum_{i\in I} z_{ik}=1
\qquad \forall k\in K.
\]

Pick assignments define drafted players:

\[
\sum_{k\in K} z_{ik}=y_i
\qquad \forall i\in I.
\]

Each drafted player is assigned to exactly one roster position:

\[
\sum_{p\in P} x_{ip}=y_i
\qquad \forall i\in I.
\]

Players cannot be assigned to ineligible positions:

\[
x_{ip}=0
\qquad \forall i,p \text{ with } E_{ip}=0.
\]

Roster requirements must be filled exactly:

\[
\sum_{i\in I} x_{ip}=R_p
\qquad \forall p\in P.
\]

ADP availability is enforced by disabling pick assignments when a player is
expected to be gone before that pick:

\[
z_{ik}=0
\qquad \forall i,k \text{ with } A_i+\delta<S_k.
\]

All decision variables are binary.

## Heuristic Benchmarks

`Direct Greedy` and `Opportunity Cost Greedy` use the same roster, eligibility,
snake-pick, and ADP availability rules as the ILP, but commit to one player and
one roster slot at a time.

`Direct Greedy` chooses an open position using a scarcity score and takes the
best currently available eligible player.

`Opportunity Cost Greedy` compares the best currently available player for each
open position with the best player expected to remain at the next owned pick,
then drafts the largest opportunity-cost choice. It includes a feasibility
fallback for tight position supply.

Heuristic quality is reported against the ADP-aware ILP:

```text
optimal_gap = objective_ADP_aware_ILP - objective_heuristic
optimal_gap_pct = optimal_gap / objective_ADP_aware_ILP
```

Implementation details for the two heuristics are documented in
`docs/heuristics.md`.
