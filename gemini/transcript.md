\# English Presentation Transcript for \`english\_slide2.md\`

Target length: about 15 to 20 minutes    
Suggested pace: transition slides 5 to 10 seconds; content slides about 30 to 45 seconds

\---

\#\# Slide 1: Title

Hi everyone. Today, we will present our project, \*\*Strategic Fantasy Baseball Draft Optimization\*\*.

In this project, we study the fantasy baseball draft as an operations research problem. A draft is not only about choosing famous players or the highest-ranked player available. It is a sequential decision-making problem with limited picks, roster requirements, and competition from other managers.

Our goal is to design a method that helps a manager build a high-value roster under realistic draft constraints, while still being fast enough for real draft-day decisions.

\---

\#\# Slide 2: Introduction

Before the season begins, General Managers, or GMs, take turns selecting players from a pool of available talent. Through this process, each manager builds the roster that will compete throughout the season.

Fantasy Baseball simulates this roster-building process. Managers draft players and then compete based on the statistical performance of those players during the season.

However, drafting is not simply about selecting the strongest available player. Managers must balance projected player value, positional requirements, and player availability,  while competing against other managers for the same pool of players.

Therefore, the main challenge is: \*\*how can we fill roster slots correctly and maximize total team value with limited picks and intense competition?\*\*

\---

\#\# Slide 3: Problem Settings

Next, we introduce the problem settings of our model.

We first define the information available for each player, then explain the snake draft mechanism, and finally describe the roster requirements that every valid team must satisfy.

\---

\#\# Slide 4: Player Attributes

To model the draft process, each player in the draft pool is characterized by three key attributes.

The first attribute is \*\*projected value\*\*, denoted by \\(v\_i\\). It represents the expected fantasy points a player can earn during the season.

As scouting and player evaluation become more data-driven, teams tend to assign similar valuations to the same player. This is the convergence of analytics, and it gives us a standardized measure of player quality.

The second attribute is \*\*Average Draft Position\*\*, or ADP. ADP reflects the market expectation of when a player is likely to be selected. It helps us estimate whether a player may still be available at a later pick.

The third attribute is \*\*eligible positions\*\*, denoted by \\(E\_i\\). This tells us which roster slots a player can legally fill.

In short, projected value tells us how good a player is, ADP tells us whether we can still draft him, and eligible positions tell us where he can fit.

\---

\#\# Slide 5: Snake Draft Mechanism

After defining player attributes, we introduce the draft environment.

In Major League Baseball, draft order is usually fixed based on the previous season's standings. But in this project, we use a \*\*snake draft\*\*, which is widely used in Fantasy Baseball.

The key feature of a snake draft is that the order reverses every round. For example, if the first round follows the order 1, 2, 3, then the second round follows 3, 2, 1\.

This mechanism reduces the absolute advantage of having the first pick and places more emphasis on strategy.

The equations on the slide convert the round number and our initial position into our absolute pick number. This lets us know exactly when our team will draft in every round.

\---

\#\# Slide 6: Roster Requirements

A valid draft strategy must satisfy roster requirements.

In this study, we consider a 16-slot starting lineup. The lineup requires one catcher, one first baseman, one second baseman, one third baseman, one shortstop, three outfielders, one utility hitter, five starting pitchers, and two relief pitchers.

One important detail is that the utility position can only be filled by hitters. Pitchers cannot occupy that slot.

So our objective is not simply to draft the highest-valued players. We must also ensure that every required position is filled correctly.

These roster requirements later become constraints in our optimization model.

\---

\#\# Slide 7: Real Data Collection

After defining the draft environment, we transform the baseball market into data.

For each player, we need projected performance, fantasy scoring rules, draft market expectations, and position eligibility. These data components allow us to build both the optimization model and the heuristic algorithms.

\---

\#\# Slide 8: Player Projected Points

The first dataset is player projected points, which becomes the projected value \\(v\_i\\) in our model.

We scraped 2026 projection data from FantasyPros. The raw projections include baseball statistics such as home runs, stolen bases, runs, RBIs, innings pitched, strikeouts, saves, and wins.

However, these raw statistics cannot be used directly in our optimization model. We first convert them into fantasy points using league-specific scoring systems.

To test robustness, we use two scoring formats: Yahoo Scoring and FanGraphs Scoring. Because the two systems assign different weights to the same baseball events, the same player may have different fantasy values in different league settings.

By testing both systems, we can check whether our algorithm performs consistently across different scoring environments.

\---

\#\# Slide 9: Average Draft Position

The second major dataset is Average Draft Position, or ADP.

We collected aggregate ADP from FantasyPros, combining information from platforms such as Yahoo, ESPN, CBS, and NFBC.

ADP is important because it represents the market's expectation of when each player will be drafted. In our model, it helps define the availability window of a player.

For example, if a player's ADP is much earlier than our next pick, then we should not assume that player will still be available. This makes the model more realistic than simply ranking players by projected points.

\---

\#\# Slide 10: Model Formulation

Now we move from data to mathematical modeling.

Using projected value, ADP, and position eligibility, we formulate the draft problem as an integer programming model. The IP model gives us a benchmark for the best possible roster under our assumptions.

\---

\#\# Slide 11: Variables and Objective

In our integer programming model, we define three types of binary decision variables.

First, \\(y\_i\\) equals 1 if player \\(i\\) is drafted, and 0 otherwise.

Second, \\(x\_{ip}\\) equals 1 if player \\(i\\) is assigned to position \\(p\\). This handles position eligibility and roster construction.

Third, \\(z\_{ik}\\) equals 1 if player \\(i\\) is selected at our \\(k\\)-th pick. This connects player selection with the draft timeline.

The objective is to maximize the total projected value of our starting roster. In other words, we want to select the combination of players that gives the highest total fantasy points while satisfying all draft and roster constraints.

\---

\#\# Slide 12: Constraints

The constraints make sure the solution is realistic.

First, we draft exactly one player at each of our picks. This is represented by the constraint that the sum of \\(z\_{ik}\\) over all players equals 1 for every pick.

Second, if a player is drafted, he must be assigned to exactly one roster position. This links the drafting decision \\(y\_i\\) with the assignment variable \\(x\_{ip}\\).

Third, every position must satisfy its required number of roster slots.

Finally, we add a market availability constraint using ADP. If our pick is later than a player's ADP plus a buffer, we treat that player as unavailable.

This prevents the model from choosing players who would probably already be drafted by opponents.

\---

\#\# Slide 13: The Bottleneck

The IP model is useful because it gives us a mathematical benchmark.

However, the next question is whether it can be used in a real draft room. In practice, a fantasy draft has strict time limits, and managers often need to make decisions in less than one minute.

This creates the main bottleneck of the project.

\---

\#\# Slide 14: Fatal Flaws of IP in Practice

Although Gurobi can provide a mathematically optimal solution, traditional IP has two major practical problems.

The first is scalability. As the number of players increases, the branch-and-bound search space grows very quickly. With a large player pool, the solver may need too much time to prove optimality.

The second is real-time execution. Drafts usually have timers, often around 60 seconds per pick. A manager cannot wait several minutes, or even longer, for an optimization solver during a live draft.

Therefore, we use IP as a benchmark, but we need a faster method for real-time decision making.

\---

\#\# Slide 15: Heuristic Design

To bridge the gap between optimality and speed, we designed two heuristic algorithms.

The first one is the baseline method: \*\*Direct Greedy\*\*.

The idea is simple. At each pick, the algorithm estimates which position is most scarce by comparing remaining roster slots with available players in the market. Then it selects the best player for the most scarce position.

This is fast and intuitive, but it is also myopic. For example, it may draft a mediocre catcher just because catcher looks scarce, while missing a much more valuable superstar at another position.

So Direct Greedy gives us a useful baseline, but it does not fully capture the timing value of a draft pick.

\---

\#\# Slide 16: Opportunity Cost Greedy

Our main heuristic is \*\*Opportunity Cost Greedy\*\*, or OCG.

The key idea is to measure the \*\*cost of waiting\*\*.

At each pick, OCG first looks at all remaining roster gaps. For each position, it identifies the best player available now, which we call \\(V\_{\\text{now}}\\).

Then it forecasts the best player who is likely to remain available by our next pick, called \\(V\_{\\text{next}}\\).

The opportunity cost is the difference between these two values. If the difference is large, waiting is expensive, so we should draft that position now. If the difference is small, we can safely delay.

This gives OCG some strategic look-ahead, while still keeping the algorithm fast enough for live decisions.

\---

\#\# Slide 17: Complexity Analysis

For implementation, we maintain a max-heap, or priority queue, for every position.

This allows the algorithm to quickly find the best available player for each roster slot.

We also use lazy deletion. When opponents draft players, we do not immediately remove those players from every heap. Instead, when a player is popped from a heap, we check whether he is still available. If not, we discard him and continue.

This improves efficiency because we avoid many unnecessary updates.

Let \\(n\\) be the total number of players, \\(r\\) be the roster size, and \\(p\\) be the number of positions. The total complexity is \\(O(n \\log n \+ r \\cdot p)\\), which is the same order as Direct Greedy.

So OCG adds strategic look-ahead without sacrificing real-time performance.

\---

\#\# Slide 18: Real-Data Validation

We first validate the algorithms using real 2026 projection data.

The table compares OCG and Direct Greedy under Yahoo and FanGraphs scoring. The metric is the optimal gap ratio, which measures how far the heuristic solution is from the IP optimum.

Under Yahoo scoring, OCG has a gap of only 0.50%, while Direct Greedy has a gap of 3.24%.

Under FanGraphs scoring, OCG has a gap of 1.24%, while Direct Greedy has a gap of 3.36%.

This shows that OCG consistently stays within 1.5% of the mathematical optimum and clearly outperforms the standard greedy approach.

\---

\#\# Slide 19: Synthetic Data and Evaluation

Real data validation is important, but one season of data may not cover all possible market conditions.

Therefore, we also design synthetic experiments. These experiments allow us to control the environment and test whether our algorithm remains robust under extreme or unusual draft conditions.

\---

\#\# Slide 20: Four Dimensions of Synthetic Testing

We test four main dimensions.

The first is the distribution of player points. We consider normal, uniform, and star-heavy distributions.

The second is position eligibility. Some players may be flexible and eligible for multiple positions, while others may be restricted to a single position.

The third is market uncertainty. We test how sensitive the algorithm is to ADP noise and systematic bias.

The fourth is the demand ratio. This controls whether the player pool is tight or abundant relative to roster needs.

Together, these factors let us test the algorithm in a much wider range of environments than real data alone.

\---

\#\# Slide 21: Synthetic Data Scenario Matrix

This table summarizes the 14 synthetic scenarios.

Scenario S1 is the baseline. Then we change one major factor at a time, such as the points distribution, position flexibility, market accuracy, or demand ratio.

For example, S3 uses a star-heavy point distribution, where a small number of elite players account for a large share of total value.

S6 uses single-position eligibility, which makes roster construction harder because players cannot flex into multiple slots.

S13 represents a high-demand market, where available players are scarce compared with roster needs.

By comparing results across these scenarios, we can identify where OCG provides the greatest advantage.

\---

\#\# Slide 22: Strategic Insights

The results show that OCG is especially strong in stress scenarios.

In the star-heavy scenario, Direct Greedy often misses the value cliff. It may focus on positional scarcity and fail to secure elite players before they disappear. OCG reduces the gap from 8.39% to 2.87%.

In the single-position scenario, early mistakes are costly because there is no positional flexibility. OCG's look-ahead helps prevent these traps.

In chaotic market scenarios, where players are drafted differently from ADP, OCG still remains robust.

Finally, in high-demand markets, the player pool is tight. OCG performs well because it can identify when waiting would cause a large loss in value.

\---

\#\# Slide 23: Full Results

This table shows selected results from the synthetic experiments.

Across the scenarios, OCG consistently has a smaller optimality gap than Direct Greedy.

For example, in the baseline case, Direct Greedy has a gap of 4.79%, while OCG reduces it to 1.92%.

In the star-heavy case, the gap falls from 8.39% to 2.87%. In the high-demand case, it falls from 8.81% to 2.64%.

The main conclusion is that OCG remains close to the IP optimum across all 14 scenarios, usually keeping the gap under 3%.

\---

\#\# Slide 24: Runtime Scaling

Next, we evaluate runtime scaling.

The approximate number of variables grows with the number of players, positions, and roster size. As the test size increases, IP becomes much slower.

For small and medium cases, IP can still solve the problem optimally. But as the player pool grows, runtime increases sharply.

In the timeout case, with more than 184,000 players and 24 teams, IP runs for more than 1,869 seconds and times out.

In contrast, both DG and OCG remain fast. OCG completes the largest case in about 23 seconds.

This confirms that OCG is much more practical for large-scale or real-time draft environments.

\---

\#\# Slide 25: Scaling Visualization

The visualization shows the same runtime pattern more clearly.

As the number of variables increases, the IP curve rises much faster than the heuristic methods.

Direct Greedy is slightly faster than OCG, but the difference is small compared with the improvement in solution quality.

This is the key trade-off of our method: OCG spends a little more computation time than a simple greedy algorithm, but it achieves much better draft quality while still remaining fast enough for practical use.

\---

\#\# Slide 26: Conclusions and Business Recommendations

To conclude, we provide three recommendations for fantasy baseball managers.

First, Direct Greedy is risky. Choosing only by positional scarcity or best available player can lead to significant value loss, especially in star-heavy or high-demand markets.

Second, IP is a strong benchmark, but not a practical live-draft tool. It is useful for post-draft analysis or pre-season simulation, but its runtime makes it difficult to use during a timed draft.

Third, OCG is the deployable solution. By quantifying the delay cost, OCG captures much of the strategic logic of IP while remaining fast enough for real-time decision making.

In our largest test, it handled around 50 million decision variables in under 25 seconds.

\---

\#\# Slide 27: Limitations and Future Extensions

There are still several limitations and possible extensions.

First, our current model treats ADP as a deterministic threshold. In future work, we can build probabilistic opponent models that capture different drafting behaviors, such as team preferences, risk tolerance, or favorite players.

Second, player projections are treated as average values. But in reality, players have risk. Injuries, slumps, and breakout seasons can all affect performance.

Therefore, future versions can incorporate Monte Carlo simulation and risk preferences. This would allow the algorithm to balance upside and safety depending on the manager's strategy.

\---

\#\# Slide 28: Thank You

Thank you for your attention.

This project shows that fantasy baseball drafting can be modeled as a strategic optimization problem. By combining real data, integer programming, and a fast opportunity-cost heuristic, we can produce draft recommendations that are both high-quality and practical.

We are happy to answer any questions.

