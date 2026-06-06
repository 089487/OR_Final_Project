# English Presentation Transcript for `english_slide2.md`

Target length: about 15 to 20 minutes
Suggested pace: transition slides 5 to 10 seconds; content slides about 30 to 45 seconds

---

## Slide 1: Algorithmic Roster Construction

Hi everyone. Today, we will present our project, **Algorithmic Roster Construction**.

Specifically, we study a sequential decision-making problem where a manager must acquire talent under strict constraints and intense market competition.

We use Fantasy Baseball not as the final application itself, but as a data-rich competitive testbed for studying sequential talent acquisition under scarcity. It gives us real market expectations, projected player utility, and a timed draft environment where opportunity cost matters.

---

## Slide 2: 1. Introduction: The General Manager's Dilemma

In simple terms, this is a step-by-step talent selection problem in a competitive market.

Technically, we model it as sequential resource allocation under scarcity. Multiple decision makers compete for a limited pool of unique players, and every opponent's pick changes the feasible set for everyone else.

A manager must balance roster requirements with the timing paradox: knowing when to secure a scarce asset before its market availability expires.

So our goal is to build a decision-support framework that provides a deployable balance between theoretical optimality and real-time execution speed.

---

## Slide 3: Problem Settings

Next, we introduce the problem settings of our model.

We first define the information available for each player, then explain the snake draft mechanism, and finally describe the roster requirements that every valid team must satisfy.

---

## Slide 4: 2. Problem Settings I: Player Attributes

To model sequential talent acquisition, each player has three attributes.

First is the Value Proxy, \(v_i\), representing consensus projected utility. Second is ADP, or Average Draft Position. This serves as a market expectation proxy, telling us how long an asset is likely to remain available. Finally, eligibility defines where a player fits into the roster's structural constraints.

So \(v_i\) tells us expected utility, ADP tells us timing risk, and eligibility tells us whether the asset fits the roster structure.

---

## Slide 5: 3. Problem Settings II: Snake Draft Mechanism

Next, we define the draft environment.

We use a snake draft, which reverses the order every round. If round one is 1, 2, 3, then round two is 3, 2, 1. This reduces the absolute advantage of the first pick and makes timing strategy more important.

The equations convert the round number and initial position into the absolute pick number, so we know exactly when our team drafts in each round.

---

## Slide 6: 4. Problem Settings III: Roster Requirements

A valid draft must satisfy roster requirements.

We use a 16-slot starting lineup: infield positions, three outfielders, one hitter-only utility slot, five starting pitchers, and two relief pitchers.

This means the model cannot simply choose the highest-valued players. It must also fill every required position correctly. These roster requirements become hard constraints in the optimization model.

---

## Slide 7: Data Framework

After defining the draft environment, we transform the baseball market into a structured data framework.

For each player, we need a value proxy, a market availability proxy, and position eligibility. Fantasy Baseball is useful here because it provides a high-frequency market with consensus projections and observable draft expectations.

---

## Slide 8: 1. Value Proxy ($v_i$): Consensus Projected Utility

The first data component is the value proxy, \(v_i\).

We use 2026 FantasyPros consensus projections. The raw projections include batting and pitching statistics such as home runs, stolen bases, innings, strikeouts, saves, and wins.

However, these raw statistics cannot be used directly as objective values. We convert them into projected utility using league-specific scoring systems.

To test robustness, we use Yahoo and FanGraphs scoring. Because they assign different weights to the same events, the same player may have different utility under different reward structures.

By testing both systems, we check whether the decision framework performs consistently across different reward structures.

---

## Slide 9: 2. Market Availability Proxy (ADP)

The second data component is Average Draft Position, or ADP.

We collected aggregate ADP from FantasyPros, combining information from platforms such as Yahoo, ESPN, CBS, and NFBC.

ADP is important because it represents the market's expectation of when each player will be drafted. In our model, it defines the availability horizon of each asset.

For example, if a player's ADP is much earlier than our next pick, then we should not assume that player will still be available. This makes the model more realistic than simply ranking players by projected points.

---

## Slide 10: Model Formulation

Now we move from data to mathematical modeling.

Using projected value, ADP, and position eligibility, we formulate the draft problem as an integer programming model. The IP model gives us a benchmark for the best possible roster under our assumptions.

---

## Slide 11: 5. Model Formulation I: Variables and Objective

In the IP model, we define three binary variables.

\(y_i\) indicates whether player \(i\) is drafted. \(x_{ip}\) assigns player \(i\) to position \(p\). \(z_{ik}\) records whether player \(i\) is selected at our \(k\)-th pick.

The objective is to maximize the total projected utility of the starting roster while satisfying all draft and roster constraints.

---

## Slide 12: 6. Model Formulation II: Constraints

The constraints make the solution realistic.

First, we draft exactly one player at each pick, and each drafted player can only be selected once. Second, every drafted player must be assigned to one roster position. Third, every position must satisfy its required slot count.

Finally, ADP creates the market availability constraint. If our pick is later than a player's ADP plus a buffer, that player is treated as unavailable, because competitors probably selected him already.

---

## Slide 13: The Bottleneck

The IP model is useful because it gives us a mathematical benchmark.

However, the next question is whether it can be used in a real draft room. In practice, a fantasy draft has strict time limits, and managers often need to make decisions in less than one minute.

This creates the main bottleneck of the project.

---

## Slide 14: The Fatal Flaws of IP in Practice

Although Gurobi can provide an optimal solution, IP has two practical problems.

First is scalability. As the player pool grows, the branch-and-bound search space grows quickly.

Second is real-time execution. Drafts often have 60-second timers, so a manager cannot wait several minutes for a solver.

Therefore, we use IP as a benchmark, but we need a faster method for real-time decision making.

---

## Slide 15: 7. Algorithms: Heuristic Design

To bridge optimality and speed, we design heuristic algorithms.

The baseline is Direct Greedy.

At each pick, DG estimates which position is most scarce by comparing remaining roster slots with available players, then selects the best player for that position.

This is fast, but myopic. It may overreact to current scarcity and miss a much more valuable asset at another position.

So DG is useful as a baseline, but it does not capture the timing value of a draft pick.

---

## Slide 16: 8. Opportunity Cost Greedy (OCG)

Our main contribution is Opportunity Cost Greedy, or OCG.

OCG asks a simple question: if we do not select this asset now, what value might we lose by our next turn?

We call this the cost of delay.

For each position, OCG compares \(V_{\text{now}}\), the best asset now, with \(V_{\text{next}}\), the best asset likely available next.

If the gap is large, that position is approaching a Value Cliff, meaning the talent pool is likely to decline sharply before our next decision point.

This gives OCG strategic foresight while remaining computationally efficient enough for real-time decision support.

---

## Slide 17: 9. Algorithms: Complexity Analysis

For implementation, we maintain a max-heap for every position.

This allows the algorithm to quickly find the best available asset for each roster slot.

We also use lazy deletion. When opponents draft players, we do not immediately remove them from every heap. We only check availability when a player is popped.

This avoids many unnecessary updates.

Let \(n\) be the total number of players, \(r\) be the roster size, and \(p\) be the number of positions. The total complexity is \(O(n \log n + r \cdot p)\), which is the same order as Direct Greedy.

So OCG adds look-ahead without sacrificing real-time performance.

---

## Slide 18: Real-Data Validation

We first validate the algorithms using real 2026 projection data.

The table compares OCG and Direct Greedy under Yahoo and FanGraphs scoring. The metric is the optimal gap ratio, which measures how far the heuristic solution is from the IP optimum.

Under Yahoo scoring, OCG has a gap of only 0.50%, while Direct Greedy has a gap of 3.24%.

Under FanGraphs scoring, OCG has a gap of 1.24%, while Direct Greedy has a gap of 3.36%.

This shows that OCG consistently stays within 1.5% of the mathematical optimum and clearly outperforms the standard greedy approach.

---

## Slide 19: Synthetic Data & Evaluation

Real data validation is important, but one season of data may not cover all possible market conditions.

Therefore, we also design synthetic experiments. These experiments allow us to control the environment and test whether our algorithm remains robust under extreme or unusual draft conditions.

---

## Slide 20: Four Dimensions of Synthetic Testing

We test four main dimensions.

First is the distribution of player points: normal, uniform, and star-heavy.

Second is position eligibility, from flexible multi-position players to strict single-position players.

The third is market uncertainty. We test how sensitive the algorithm is to ADP noise and systematic bias.

The fourth is the demand ratio. This controls whether the player pool is tight or abundant relative to roster needs.

Together, these factors test the algorithm in a wider range of environments than real data alone.

---

## Slide 21: Synthetic Data: Scenario Matrix

This table summarizes the 12 synthetic scenarios.

S1 is the baseline. Then we change one major factor at a time: points distribution, position flexibility, market accuracy, or demand ratio.

For example, S3 uses a star-heavy point distribution, where a small number of elite players account for a large share of total value.

S6 uses single-position eligibility, which makes roster construction harder because players cannot flex into multiple slots.

S11 represents a high-demand market, where available players are scarce compared with roster needs.

Comparing these scenarios shows where OCG provides the greatest advantage.

---

## Slide 22: All data result

This table shows selected results from the synthetic experiments.

Across the scenarios, OCG consistently has a smaller optimality gap than Direct Greedy.

For example, in the baseline case, Direct Greedy has a gap of 4.79%, while OCG reduces it to 1.92%.

In the star-heavy case, the gap falls from 8.39% to 2.87%. In the high-demand case, it falls from 8.81% to 2.64%.

The main conclusion is that OCG remains close to the IP optimum across all 12 scenarios, usually keeping the gap under 3%.

---

## Slide 23: Strategic Insights: Where OCG Excels

Our results show that OCG is most effective in stress scenarios.

In a star-heavy market, simpler methods often miss the timing and fail to secure elite players. OCG's look-ahead logic prevents this by identifying the value cliff early.

In the single-position scenario, early mistakes are also costly because there is no positional flexibility. OCG helps maintain a strong balance across the entire roster.

---

## Slide 24: Strategic Insights: Where OCG Excels

In chaotic market scenarios, where players are drafted differently from ADP, OCG still remains robust.

Finally, in high-demand markets, the player pool is tight. OCG performs well because it can identify when waiting would cause a large loss in value.

---

## Slide 25: Stress Testing: Runtime Scaling

Next, we evaluate runtime scaling.

As the number of players, positions, and roster slots grows, IP becomes much slower.

In the largest timeout case, IP runs for more than 1,869 seconds and still does not finish.

In contrast, DG and OCG remain fast. OCG completes the largest case in about 23 seconds, which makes it much more practical for large-scale or real-time decision environments.

---

## Slide 26: Scaling Visualization

The visualization shows the same runtime pattern.

As variables increase, the IP curve rises much faster than the heuristic methods.

Direct Greedy is slightly faster than OCG, but the difference is small compared with the improvement in solution quality.

This is the key trade-off: OCG spends a little more computation than simple greedy, but achieves better draft quality while remaining practical.

---

## Slide 27: Draft Simulation: One OCG vs 11 DG Teams (Yahoo)

Next, we simulate a competitive draft where one OCG team drafts against eleven Direct Greedy teams under Yahoo scoring.

The chart compares team outcomes by draft position. This test moves beyond a single-team benchmark and asks whether OCG still creates value when all teams are competing for the same player pool.

The main takeaway is that OCG remains competitive across draft positions because it makes better timing decisions during the draft.

---

## Slide 28: Draft Simulation: One OCG vs 11 DG Teams (FanGraphs)

We repeat the same competitive draft simulation under FanGraphs scoring.

This is important because FanGraphs scoring values batting and pitching events differently from Yahoo scoring. If OCG performs well under both scoring systems, then the method is not only tuned to one particular league format.

The result again supports the robustness of opportunity-cost reasoning in a competitive draft room.

---

## Slide 29: 10. Conclusions & Future Extensions

To conclude, OCG provides a strong balance between execution speed and solution quality.

It functions as a real-time decision-support framework that handles millions of variables in seconds.

While we use baseball as our testbed, this cost-of-delay logic can generalize to other competitive talent acquisition scenarios under scarcity.

Our experiments show that OCG performs especially well under stress scenarios, including star-heavy value curves, low flexibility, chaotic markets, and high demand.

Future work can add predicting opponent moves and risk-aware utility, so the framework can handle uncertain behavior, injuries, and upside-versus-safety preferences.

---

## Slide 30: Thank You for Watching!

Thank you for your attention.

This project shows that Fantasy Baseball can serve as a data-rich testbed for sequential talent acquisition under scarcity. By combining real market data, integer programming, and a fast opportunity-cost heuristic, we can produce recommendations that are both high-quality and practical.

We are happy to answer any questions.
