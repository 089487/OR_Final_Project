# Fantasy Baseball Draft Optimization Model

This file documents the mathematical model implemented in `src/draft_model.py`.

## Sets

- \(I\): set of available players.
- \(P\): set of roster positions.
  \[
  P=\{C,1B,2B,3B,SS,OF,Util,SP,RP\}.
  \]
- \(K\): set of draft picks owned by one team.

For a snake draft with \(M\) teams and draft position \(j\), the overall pick in round
\(r\) is

\[
S_r =
\begin{cases}
(r-1)M+j, & r \text{ odd},\\
rM-j+1, & r \text{ even}.
\end{cases}
\]

In the code, `snake_picks()` returns the list \(\{S_k:k\in K\}\).

## Parameters

- \(V_i\): projected fantasy points for player \(i\).
- \(E_{ip}\in\{0,1\}\): 1 if player \(i\) is eligible for roster position \(p\).
- \(R_p\): required number of roster slots at position \(p\).
- \(A_i\): average draft position for player \(i\).
- \(S_k\): overall pick number corresponding to our \(k\)-th pick.
- \(\delta\): ADP availability buffer.

The default roster requirements are:

| Position | Requirement |
|---|---:|
| C | 1 |
| 1B | 1 |
| 2B | 1 |
| 3B | 1 |
| SS | 1 |
| OF | 3 |
| Util | 1 |
| SP | 5 |
| RP | 2 |

Eligibility note: `Util` is available to all hitters. A player whose only eligible
position is `Util` can only be assigned to `Util`. Pitchers cannot be assigned to `Util`.

## Decision Variables

The integer model uses three groups of binary variables:

\[
y_i =
\begin{cases}
1, & \text{if player }i\text{ is drafted},\\
0, & \text{otherwise},
\end{cases}
\]

\[
x_{ip} =
\begin{cases}
1, & \text{if player }i\text{ is assigned to roster position }p,\\
0, & \text{otherwise},
\end{cases}
\]

\[
z_{ik} =
\begin{cases}
1, & \text{if player }i\text{ is selected using pick }k,\\
0, & \text{otherwise}.
\end{cases}
\]

## Primal ILP

The objective is to maximize total projected roster points:

\[
\max \sum_{i\in I} V_i y_i.
\]

Each draft pick selects exactly one player:

\[
\sum_{i\in I} z_{ik}=1
\qquad \forall k\in K.
\]

The pick variables and drafted-player variable are linked:

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
\qquad \forall i\in I,\;p\in P\text{ with }E_{ip}=0.
\]

Every roster position must be filled exactly:

\[
\sum_{i\in I} x_{ip}=R_p
\qquad \forall p\in P.
\]

ADP availability is enforced by fixing impossible pick assignments to zero:

\[
z_{ik}=0
\qquad \forall i\in I,\;k\in K\text{ with }A_i+\delta<S_k.
\]

Binary restrictions:

\[
x_{ip},y_i,z_{ik}\in\{0,1\}.
\]

## LP Relaxation

Shadow prices are computed from the LP relaxation of the ILP. In the LP relaxation,
the binary restrictions are replaced by bounds:

\[
0\le x_{ip}\le 1,\qquad
0\le y_i\le 1,\qquad
0\le z_{ik}\le 1.
\]

All structural constraints remain the same. Gurobi only provides meaningful dual values
for the LP relaxation, not for the integer model.

## Compact LP Form For The Dual

For the dual derivation, it is convenient to write the LP relaxation in compact form.
Let

\[
\mathcal{F}=\{(i,p):E_{ip}=1\},
\]

and

\[
\mathcal{A}=\{(i,k):A_i+\delta\ge S_k\}
\]

be the eligible assignment pairs and available pick pairs. Variables outside these sets
are fixed to zero and omitted.

The relaxed primal becomes:

\[
\max \sum_i V_i y_i
\]

subject to

\[
\sum_{i:(i,k)\in\mathcal{A}} z_{ik}=1
\qquad \forall k,
\]

\[
\sum_{k:(i,k)\in\mathcal{A}} z_{ik}-y_i=0
\qquad \forall i,
\]

\[
\sum_{p:(i,p)\in\mathcal{F}} x_{ip}-y_i=0
\qquad \forall i,
\]

\[
\sum_{i:(i,p)\in\mathcal{F}} x_{ip}=R_p
\qquad \forall p,
\]

\[
0\le x_{ip}\le 1,\quad 0\le y_i\le 1,\quad 0\le z_{ik}\le 1.
\]

The upper bounds matter in the exact dual. In many OR explanations, the roster
shadow prices are discussed without writing every bound multiplier. The next section
includes them explicitly.

## Dual Variables

Because the primal is a maximization problem with equality constraints and upper
bounds, the equality-constraint dual variables are unrestricted in sign:

- \(\alpha_k\): dual variable for the pick-fill constraint.
- \(\beta_i\): dual variable for \(\sum_k z_{ik}-y_i=0\).
- \(\gamma_i\): dual variable for \(\sum_p x_{ip}-y_i=0\).
- \(\pi_p\): dual variable for the roster-position constraint.

For the upper bounds, use nonnegative dual variables:

- \(\mu^z_{ik}\ge 0\): upper-bound multiplier for \(z_{ik}\le 1\).
- \(\mu^x_{ip}\ge 0\): upper-bound multiplier for \(x_{ip}\le 1\).
- \(\mu^y_i\ge 0\): upper-bound multiplier for \(y_i\le 1\).

## Dual Objective

The LP dual is:

\[
\min
\sum_{k\in K}\alpha_k
+\sum_{p\in P}R_p\pi_p
+\sum_{(i,k)\in\mathcal{A}}\mu^z_{ik}
+\sum_{(i,p)\in\mathcal{F}}\mu^x_{ip}
+\sum_{i\in I}\mu^y_i.
\]

The right-hand side of the two linking constraints is zero, so \(\beta_i\) and
\(\gamma_i\) do not appear in the dual objective.

## Dual Constraints

Each primal variable produces one dual constraint.

For every available pick variable \(z_{ik}\):

\[
\alpha_k+\beta_i+\mu^z_{ik}\ge 0
\qquad \forall (i,k)\in\mathcal{A}.
\]

For every eligible assignment variable \(x_{ip}\):

\[
\gamma_i+\pi_p+\mu^x_{ip}\ge 0
\qquad \forall (i,p)\in\mathcal{F}.
\]

For every drafted-player variable \(y_i\):

\[
-\beta_i-\gamma_i+\mu^y_i\ge V_i
\qquad \forall i\in I.
\]

Sign restrictions:

\[
\alpha_k,\beta_i,\gamma_i,\pi_p\text{ are unrestricted},
\]

\[
\mu^z_{ik},\mu^x_{ip},\mu^y_i\ge 0.
\]

## Shadow Price Interpretation

In the implementation, the reported shadow price for a position \(p\) is Gurobi's dual
value for:

\[
\sum_{i\in I}x_{ip}=R_p.
\]

That value is \(\pi_p\), read in code as:

```python
model.getConstrByName(f"roster_{pos}").Pi
```

Interpretation:

\[
\pi_p \approx
\frac{\partial \text{optimal LP objective}}{\partial R_p}.
\]

So \(\pi_p\) is the marginal change in the relaxed optimal objective when the roster
requirement for position \(p\) is increased by one unit, locally around the current
solution.

Important caveats:

- The value is from the LP relaxation, not the integer model.
- Because the roster constraints are equalities, \(\pi_p\) can be positive or negative.
- It should be treated as an approximate positional-scarcity signal, not as an exact
integer marginal value.
