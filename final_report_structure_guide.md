# Final Report Structure Guide

This guide translates the seven report-writing requirements from `reference/final_project_instructions.pdf` into concrete writing instructions for `final_report.tex`.

## 1. Introduction

Purpose:
Introduce the business background, motivation, and high-level decision problem before any formulas or implementation details.

What to include:
- Start from the real decision setting: a fantasy baseball manager preparing for a snake draft.
- Explain why the draft matters: roster quality is largely determined before the season starts.
- Describe the problem at a high level: choose a sequence of players under roster, position, and ADP availability constraints.
- Emphasize why the problem is interesting: local best-player choices may create future roster imbalance.
- Identify the decision maker: the fantasy manager.
- Highlight the complicated environment: opponents draft players, ADP creates market timing, players have multi-position eligibility, and roster rules must be satisfied.
- State the key trade-offs: projected points vs positional scarcity, current value vs future availability, exact solution quality vs runtime.

Writing style:
- Business-facing, concise, and motivating.
- Avoid detailed mathematical notation.
- Avoid implementation details unless they clarify the high-level contribution.

Current report role:
The Introduction should position Opportunity Cost Greedy as the proposed decision-support heuristic, Direct Greedy as a simple baseline, and the ADP-aware ILP as the benchmark.

## 2. Problem Description

Purpose:
Describe the operational problem and conceptual model in words before writing the mathematical formulation.

What to include:
- The manager owns a fixed sequence of draft picks determined by snake-draft order.
- Each player has projected points, eligible positions, and ADP.
- The manager must draft one player per owned pick.
- The final roster must satisfy fixed position requirements.
- A drafted player must be assigned to exactly one eligible roster slot.
- A player should be considered unavailable if ADP suggests he would already have been drafted by opponents.
- The objective is to maximize total projected roster points.

Writing style:
- Use business language first.
- Define decision variables, parameters, objective, and constraints conceptually.
- Keep this section complete but not formula-heavy.

Suggested narrative:
This is a sequential-looking decision, but the model treats the draft plan as an integrated roster-construction problem because every pick changes the value of future picks.

## 3. Model Formulation

Purpose:
Give a compact mathematical model that precisely represents the problem.

What to include:
- Sets:
  - players
  - roster positions
  - owned draft picks
- Parameters:
  - projected points
  - eligibility matrix
  - roster requirements
  - pick numbers
  - ADP
  - ADP tolerance or buffer
- Decision variables:
  - whether a player is drafted
  - whether a player is assigned to a position
  - whether a player is selected with a specific pick
- Objective:
  - maximize total projected points.
- Constraints:
  - one player per owned pick
  - link pick decisions to drafted-player decisions
  - assign each drafted player to exactly one position
  - respect player-position eligibility
  - satisfy roster requirements
  - enforce ADP-based availability
  - binary variable restrictions

Writing style:
- Compact and precise.
- Use notation consistently.
- Follow the formulation style of the proposal, but update terminology to match the current project focus.

Important positioning:
The ILP is the exact benchmark, not the final scalable algorithm.

## 4. Algorithms

Purpose:
Describe the self-designed heuristic algorithm and the comparison algorithms.

What to include:
- ADP-aware ILP:
  - exact benchmark
  - solved with Gurobi
  - useful for measuring optimality gaps
- Direct Greedy:
  - simple baseline
  - chooses strong currently available players while filling roster needs
  - expected to be fast but myopic
- Opportunity Cost Greedy:
  - proposed heuristic
  - estimates the cost of waiting at each position
  - compares current available value with expected future value at the next owned pick
  - chooses the position/player pair with the highest opportunity-cost urgency
  - includes feasibility fallback logic for tight position supply

What to emphasize:
- A self-proposed algorithm is required.
- The proposed algorithm should be clearly different from simply calling a solver.
- The reason for the heuristic is scalability.

Suggested content:
- A short algorithm description in words.
- Pseudocode or a step-by-step bullet list.
- Complexity discussion if space allows.

## 5. Data Collection and Generation

Purpose:
Show that the project includes both random synthetic instances and at least one real-world instance.

Synthetic data:
- Explain the synthetic generator.
- Describe factors, levels, and scenarios:
  - projected point distribution
  - position eligibility distribution
  - roster scale
  - player-demand ratio
  - ADP noise
  - ADP tolerance
  - large-scale stress size
- Explain how generated parameters become player points, ADP, and eligibility.
- Explain why synthetic instances are useful: they isolate factors and stress-test scalability.

Real-world data:
- State that real fantasy baseball inputs are derived from Yahoo and FanGraphs sources.
- Explain which fields are needed:
  - projected fantasy value or points
  - ADP
  - player position eligibility
- Explain that real data is used as a practicality check, while synthetic data is the main controlled evaluation.

Important requirement:
The final report must include both generated instances and real-world instances.

## 6. Performance Evaluation

Purpose:
Present results showing whether the proposed algorithm performs well.

Required benchmarks:
- ADP-aware ILP as the exact or upper-bound benchmark where solvable.
- Direct Greedy as a simple heuristic baseline.
- Opportunity Cost Greedy as the proposed method.

Metrics:
- objective value
- runtime
- optimal gap
- optimal gap percentage
- solver status and MIP gap for ILP

Synthetic experiments:
- N1: baseline comparison.
- N2: points distribution sensitivity.
- N3: position distribution sensitivity.
- N4: scaling over roster size and player-pool size.
- N5: ADP uncertainty and tolerance.
- N6: large-scale stress test.

Scaling figures to include:
- runtime vs approximate IP variable count.
- heuristic optimal-gap percentage vs approximate IP variable count.
- ILP status or MIP gap vs approximate IP variable count.

Key expected message:
Opportunity Cost Greedy should be close to the ILP benchmark and better than Direct Greedy, while running much faster than ILP on large instances.

N6 current interpretation:
- `stress_xlarge` remains solvable by ILP but takes substantially longer than the heuristics.
- `stress_timeout_target` is the first case where the ILP exceeds the wall-time target.
- Both heuristics remain practical across all N6 sizes.

## 7. Conclusions

Purpose:
Summarize the study and state possible improvements.

What to include:
- Restate the decision problem and why it matters.
- Summarize the model: ADP-aware ILP benchmark.
- Summarize the algorithmic contribution: Opportunity Cost Greedy.
- Summarize empirical findings:
  - Opportunity Cost Greedy improves over Direct Greedy.
  - ILP gives strong benchmark quality but scales poorly.
  - The proposed heuristic is more practical for large draft settings.
- Discuss limitations:
  - ADP is only an approximation of opponent behavior.
  - projected points are uncertain.
  - real drafts involve strategic interaction and changing preferences.
- Suggest improvements:
  - dynamic opponent modeling
  - richer uncertainty modeling
  - bench and category-specific scoring
  - hybrid ILP-heuristic repair methods

Writing style:
- Short and decisive.
- Emphasize the practical recommendation.

## Overall Report Order

Use this order in `final_report.tex`:

1. Introduction
2. Problem Description
3. Model Formulation
4. Algorithms
5. Data Collection and Generation
6. Performance Evaluation
7. Conclusions

## Final Writing Checklist

- The report starts from a real decision maker and business motivation.
- The problem is described in words before formulas.
- The ILP is presented as an exact benchmark.
- Opportunity Cost Greedy is clearly presented as the self-designed algorithm.
- Direct Greedy is clearly presented as the simple baseline.
- Both synthetic and real-world data are included.
- Performance evaluation includes objective quality and runtime.
- Optimal gaps are computed relative to the ADP-aware ILP when available.
- Scaling plots are used to support the scalability claim.
- The conclusion states both practical value and limitations.
