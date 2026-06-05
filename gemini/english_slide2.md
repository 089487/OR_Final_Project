---
marp: true
theme: default
paginate: true
size: 16:9
math: mathjax
style: |
  /* Import High-Quality Modern Fonts */
  @import url('https://fonts.googleapis.com/css2?family=Montserrat:ital,wght@0,400;0,600;0,800;1,400&family=Noto+Sans+TC:wght@400;500;700;900&display=swap');

  section {
    font-family: 'Montserrat', 'Noto Sans TC', sans-serif;
    background-color: #f8fafc;
    color: #334155;
    font-size: 24px;
    line-height: 1.6;
    background-image: radial-gradient(circle at 100% 0%, rgba(219, 234, 254, 0.6) 0%, transparent 40%);
  }

  /* Title Design */
  h1 {
    color: #0f172a;
    font-weight: 900;
    font-size: 46px;
    letter-spacing: -0.5px;
    border: none;
    margin-bottom: 0.2em;
  }
  
  h2 {
    color: #1e293b;
    font-weight: 700;
    font-size: 34px;
    border-bottom: 4px solid #ea580c;
    padding-bottom: 8px;
    display: inline-block;
    margin-bottom: 1.2em;
  }

  /* Cover & Transition Slides (Dark Mode) */
  section.title-slide, section.impact-slide {
    background: linear-gradient(135deg, #0f172a 0%, #1e3a8a 100%);
    color: #f8fafc;
    text-align: center;
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
  }
  section.title-slide h1, section.impact-slide h1 {
    color: #ffffff;
    font-size: 56px;
    text-shadow: 0 4px 16px rgba(0,0,0,0.4);
    border: none;
    margin-bottom: 20px;
  }
  section.title-slide h2, section.impact-slide h2 {
    color: #fb923c;
    border: none;
    font-weight: 500;
  }
  .author-block {
    margin-top: 40px;
    font-size: 20px;
    color: #cbd5e1;
    border-top: 1px solid rgba(255,255,255,0.2);
    padding-top: 20px;
  }

  /* Text Highlights */
  .highlight { color: #ea580c; font-weight: bold; }
  .blue-text { color: #2563eb; font-weight: bold; }
  .green-text { color: #16a34a; font-weight: bold; }

  /* Professional Blockquotes */
  blockquote {
    background: #eff6ff;
    border-left: 6px solid #3b82f6;
    padding: 16px 24px;
    border-radius: 0 8px 8px 0;
    font-style: normal;
    color: #1e40af;
    font-weight: 500;
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
  }

  /* Tables */
  table {
    width: 100%;
    border-collapse: collapse;
    font-size: 20px;
    background: white;
    margin-top: 10px;
    display: table;
    box-shadow: 0 10px 15px -3px rgba(0,0,0,0.1);
  }
  th { 
    background-color: #0f172a !important;
    color: #ffffff !important;
    font-weight: 600; 
    padding: 14px 16px; 
    text-align: center; 
    border: 1px solid #0f172a !important;
  }
  td { 
    padding: 12px 16px; 
    text-align: center; 
    border-bottom: 1px solid #e2e8f0; 
  }
  tbody tr:nth-child(even) td { background-color: #f8fafc !important; }
  tbody tr:hover td { background-color: #eff6ff !important; }

  /* UI Layouts */
  .grid-2 { display: grid; grid-template-columns: 1fr 1fr; gap: 30px; }
  
  .card {
    background: white;
    padding: 24px;
    border-radius: 12px;
    box-shadow: 0 10px 25px -5px rgba(0,0,0,0.05);
    border-top: 5px solid #3b82f6;
  }
  .card-orange { border-top-color: #ea580c; }
  
  .tag {
    display: inline-block;
    background: #e2e8f0;
    color: #334155;
    padding: 4px 12px;
    border-radius: 99px;
    font-size: 16px;
    font-weight: bold;
    margin-bottom: 10px;
  }
  .img-right {
    display: flex;
    justify-content: flex-end;
    width: 100%;
  }
  .img-right img {
    max-width: none !important; 
  }
---
<!-- _class: title-slide -->

# Strategic Fantasy Baseball Draft Optimization

<div class="author-block">
  <strong>OR114-2 Final Project, Group 4</strong><br>
  B13705051 Chou, Meng-Cheng | B13902103 Cheng, Yu-Hung | B13303153 Chan, Shu-Yu | B11705039 Lee, Ying-Ying<br>
</div>

<!--
Presenter notes:
Hi everyone. Today, we will present our project, **Strategic Fantasy Baseball Draft Optimization**.

In this project, we study the fantasy baseball draft as an operations research problem. A draft is not only about choosing famous players or the highest-ranked player available. It is a sequential decision-making problem with limited picks, roster requirements, and competition from other managers.

Our goal is to design a method that helps a manager build a high-value roster under realistic draft constraints, while still being fast enough for real draft-day decisions.
-->
---
## 1. Introduction: The Cornerstone of Roster Building

- **What is the Draft?**
  Before the season begins, General Managers (GMs) take turns selecting players from a pool of amateur or free-agent talent.
- **The Challenge**:
  How to precisely fill roster slots and maximize total team value given limited picks and intense competition?

<div class="img-right">
  <img src="image-2.jpeg" width="500">
</div>

<!--
Presenter notes:
Before the season begins, General Managers, or GMs, take turns selecting players from a pool of available talent. Through this process, each manager builds the roster that will compete throughout the season.

Fantasy Baseball simulates this roster-building process. Managers draft players and then compete based on the statistical performance of those players during the season.

However, drafting is not simply about selecting the strongest available player. Managers must balance projected player value, positional requirements, and player availability, while competing against other managers for the same pool of players.

Therefore, the main challenge is: **how can we fill roster slots correctly and maximize total team value with limited picks and intense competition?**
-->
---
<!-- _class: impact-slide -->

# Problem Settings

<!--
Presenter notes:
Next, we introduce the problem settings of our model.

We first define the information available for each player, then explain the snake draft mechanism, and finally describe the roster requirements that every valid team must satisfy.
-->
---
## 2. Problem Settings I: Player Attributes

Each player in the draft pool is defined by three key attributes:

<div class="grid-2" style="margin-top: 15px;">
<div>

**1. Projected Value ($v_i$)**: Expected Points earned per player in the season
<div class="card" style="margin-top: 15px;">
  <h3 style="margin-top:0;">Convergence of Analytics</h3>
  Team evaluations of players converges as scouting becomes more data-driven. <br>
<span class="blue-text">⇒ Value standardization</span>.
</div>

</div>
<div>

**2. Average Draft Position (ADP)**: Market Expectation Rank

<div class="card card-orange" style="margin-top: 15px;">
  <h3 style="margin-top:0;">Market Game Theory</h3>
  GMs know that after a certain pick, a player is unlikely to remain available.<br><br>
</div>

</div>
<br>
</div>

**3. Eligible Positions ($E_i$)**: The legal defensive slots a player can occupy.

<!--
Presenter notes:
To model the draft process, each player in the draft pool is characterized by three key attributes.

The first attribute is **projected value**, denoted by \(v_i\). It represents the expected fantasy points a player can earn during the season.

As scouting and player evaluation become more data-driven, teams tend to assign similar valuations to the same player. This is the convergence of analytics, and it gives us a standardized measure of player quality.

The second attribute is **Average Draft Position**, or ADP. ADP reflects the market expectation of when a player is likely to be selected. It helps us estimate whether a player may still be available at a later pick.

The third attribute is **eligible positions**, denoted by \(E_i\). This tells us which roster slots a player can legally fill.

In short, projected value tells us how good a player is, ADP tells us whether we can still draft him, and eligible positions tell us where he can fit.
-->
---
## 3. Problem Settings II: Snake Draft Mechanism

While the MLB uses a fixed-order draft based on the previous year's record, we utilize a **"Snake Draft"** mechanism to focus purely on **strategic optimization**.

- **Why and What is Snake Draft?**
  The order reverses every round (1-2-3, 3-2-1), which eliminates the absolute resource advantage of the first pick. The mechanism is also utilized in the game Fantasy Baseball.
- **Mathematical Slot Mapping**:
  For $M$ managers and our initial pick $j$ ($1 \le j \le M$), our absolute pick $k$ in round $r$ is:
  - **Odd Rounds (Forward)**: $k = (r - 1)M + j$
  - **Even Rounds (Reverse)**: $k = rM - j + 1$

<!--
Presenter notes:
After defining player attributes, we introduce the draft environment.

In Major League Baseball, draft order is usually fixed based on the previous season's standings. But in this project, we use a **snake draft**, which is widely used in Fantasy Baseball.

The key feature of a snake draft is that the order reverses every round. For example, if the first round follows the order 1, 2, 3, then the second round follows 3, 2, 1.

This mechanism reduces the absolute advantage of having the first pick and places more emphasis on strategy.

The equations on the slide convert the round number and our initial position into our absolute pick number. This lets us know exactly when our team will draft in every round.
-->
---
## 4. Problem Settings III: Roster Requirements

A valid team must strictly satisfy specific roster constraints shown below:

**The 16-slot starting lineup**

| Position | C | 1B | 2B | 3B | SS | OF | Util | SP | RP |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Required Slots** | 1 | 1 | 1 | 1 | 1 | 3 | 1 | 5 | 2 |

*Note: The **Util (Utility)** slot is restricted to hitters only. (pitchers cannot fill the spot!)*

<!--
Presenter notes:
A valid draft strategy must satisfy roster requirements.

In this study, we consider a 16-slot starting lineup. The lineup requires one catcher, one first baseman, one second baseman, one third baseman, one shortstop, three outfielders, one utility hitter, five starting pitchers, and two relief pitchers.

One important detail is that the utility position can only be filled by hitters. Pitchers cannot occupy that slot.

So our objective is not simply to draft the highest-valued players. We must also ensure that every required position is filled correctly.

These roster requirements later become constraints in our optimization model.
-->
---
<!-- _class: impact-slide -->

# Real Data Collection
## Transforming the Baseball Market into Data

<!--
Presenter notes:
After defining the draft environment, we transform the baseball market into data.

For each player, we need projected performance, fantasy scoring rules, draft market expectations, and position eligibility. These data components allow us to build both the optimization model and the heuristic algorithms.
-->
---
#### 1. Player Projected Points ($v_i$)
- Scraped 2026 projection data from **FantasyPros**.<img src="image.png" height="180" style="vertical-align: middle; margin-left: 10px;">
- Applied two major scoring systems to evaluate model robustness:

<div class="grid-2">
<div class="card">
  <div class="tag">Yahoo Scoring</div>
  <ul>
    <li><b>Batters</b>: (1B: 2.6, 2B: 5.2, 3B: 7.8, HR: 10.4, BB: 2.6, SB: 4.2, <b>R: 1.9, RBI: 1.9</b>)</li>
    <li><b>Pitchers</b>: (IP: 3, K: 3, SV: 8, H: -1.3, BB: -1.3, HBP: -1.3, <b>W: 8, ER: -3</b>)</li>
  </ul>
</div>

<div class="card card-orange">
  <div class="tag">FanGraphs Scoring</div>
  <ul>
    <li><b>Batters</b>: (H: 5.6, 2B: 2.9, 3B: 5.7, HR: 9.4, BB: 3, SB: 1.9, <b>AB: -1</b>)</li>
    <li><b>Pitchers</b>: (IP: 7.4, K: 2, SV: 5, H: -2.6, BB: -3, HBP: -3, <b>HR: -12.3, HLD: 4</b>)</li>
  </ul>
</div>
</div>

<!--
Presenter notes:
The first dataset is player projected points, which becomes the projected value \(v_i\) in our model.

We scraped 2026 projection data from FantasyPros. The raw projections include baseball statistics such as home runs, stolen bases, runs, RBIs, innings pitched, strikeouts, saves, and wins.

However, these raw statistics cannot be used directly in our optimization model. We first convert them into fantasy points using league-specific scoring systems.

To test robustness, we use two scoring formats: Yahoo Scoring and FanGraphs Scoring. Because the two systems assign different weights to the same baseball events, the same player may have different fantasy values in different league settings.

By testing both systems, we can check whether our algorithm performs consistently across different scoring environments.
-->
---
#### 2. Average Draft Position (ADP)
- Collected aggregate ADP from **FantasyPros**, combining data across Yahoo, ESPN, CBS, and NFBC.
- Used to define the "availability window" for each player in the draft pool.

![alt text](image-1.png)

<!--
Presenter notes:
The second major dataset is Average Draft Position, or ADP.

We collected aggregate ADP from FantasyPros, combining information from platforms such as Yahoo, ESPN, CBS, and NFBC.

ADP is important because it represents the market's expectation of when each player will be drafted. In our model, it helps define the availability window of a player.

For example, if a player's ADP is much earlier than our next pick, then we should not assume that player will still be available. This makes the model more realistic than simply ranking players by projected points.
-->
---
<!-- _class: impact-slide -->

# Model Formulation

<!--
Presenter notes:
Now we move from data to mathematical modeling.

Using projected value, ADP, and position eligibility, we formulate the draft problem as an integer programming model. The IP model gives us a benchmark for the best possible roster under our assumptions.
-->
---
## 5. Model Formulation I: Variables and Objective

Using $v_i$ and $\text{adp}_i$, we construct an **Integer Programming (IP)** model.
Let $I$ be the set of players, $P$ the set of positions, and $K$ the set of our draft picks.

**Decision Variables**:
- $y_i \in \{0,1\}$: if player $i$ is drafted.
- $x_{ip} \in \{0,1\}$: if player $i$ is assigned to position $p$.
- $z_{ik} \in \{0,1\}$: if player $i$ is selected at our $k$-th pick.

**Objective Function**: Maximize the total projected value of the starting roster.
$$ \max \sum_{i \in I} v_i y_i $$

<!--
Presenter notes:
In our integer programming model, we define three types of binary decision variables.

First, \(y_i\) equals 1 if player \(i\) is drafted, and 0 otherwise.

Second, \(x_{ip}\) equals 1 if player \(i\) is assigned to position \(p\). This handles position eligibility and roster construction.

Third, \(z_{ik}\) equals 1 if player \(i\) is selected at our \(k\)-th pick. This connects player selection with the draft timeline.

The objective is to maximize the total projected value of our starting roster. In other words, we want to select the combination of players that gives the highest total fantasy points while satisfying all draft and roster constraints.
-->
---
## 6. Model Formulation II: Constraints

1. **Draft Logic & Roster Integrity**:
   $$
   \begin{alignedat}{3}
   \sum_{i \in I} z_{ik} &= 1 && \quad \forall k \in K && \quad \text{(One player per pick)} ; \\
   \sum_{k \in K} z_{ik} &= y_i && \quad \forall i \in I && \quad \text{(At most one pick per player)}
   \end{alignedat}
   $$
   $$
   \begin{alignedat}{3}
   \sum_{p \in P} x_{ip} &= y_i && \quad \forall i \in I && \quad \text{(Assign position if drafted)} ; \\
   \sum_{i \in I} x_{ip} &= r_p && \quad \forall p \in P && \quad \text{(Satisfy roster requirements)}
   \end{alignedat}
   $$

2. **Market Availability Constraint**:
   $$ z_{ik} = 0 \quad \text{if } S_k > \text{adp}_i + \delta, \quad \forall i \in I, k \in K $$
   > *If our pick $S_k$ is later than the player's $\text{adp}_i + \delta$ , he is considered "unavailable."*

<!--
Presenter notes:
The constraints make sure the solution is realistic.

First, we draft exactly one player at each of our picks. This is represented by the constraint that the sum of \(z_{ik}\) over all players equals 1 for every pick.

Second, if a player is drafted, he must be assigned to exactly one roster position. This links the drafting decision \(y_i\) with the assignment variable \(x_{ip}\).

Third, every position must satisfy its required number of roster slots.

Finally, we add a market availability constraint using ADP. If our pick is later than a player's ADP plus a buffer, we treat that player as unavailable.

This prevents the model from choosing players who would probably already be drafted by opponents.
-->
---
<!-- _class: impact-slide -->

# The Bottleneck
## Why Traditional IP Isn't Enough?

<!--
Presenter notes:
The IP model is useful because it gives us a mathematical benchmark.

However, the next question is whether it can be used in a real draft room. In practice, a fantasy draft has strict time limits, and managers often need to make decisions in less than one minute.

This creates the main bottleneck of the project.
-->
---
## The Fatal Flaws of IP in Practice

While Gurobi provides a mathematically optimal solution, it may fail in real-world draft rooms:

<div class="grid-2">
<div class="card">
  <div class="tag">Scalability Crisis</div>
  <h3 style="margin-top:0;">Exponential Complexity</h3>
  The player pool is massive. As the players increase, the Branch-and-Bound search space explodes <span class="highlight">exponentially</span>.
</div>

<div class="card card-orange">
  <div class="tag">Real-Time Execution</div>
  <h3 style="margin-top:0;">Draft-Day Pressure</h3>
  Drafts usually have <span class="highlight">timers </span>(60 secs). A GM cannot wait for an IP solver to converge in large-scale cases.
</div>
</div>

<!--
Presenter notes:
Although Gurobi can provide a mathematically optimal solution, traditional IP has two major practical problems.

The first is scalability. As the number of players increases, the branch-and-bound search space grows very quickly. With a large player pool, the solver may need too much time to prove optimality.

The second is real-time execution. Drafts usually have timers, often around 60 seconds per pick. A manager cannot wait several minutes, or even longer, for an optimization solver during a live draft.

Therefore, we use IP as a benchmark, but we need a faster method for real-time decision making.
-->
---
## 7. Algorithms: Heuristic Design

To bridge the gap between optimality and speed, we designed two heuristics.

### ❌ Baseline: Direct Greedy (DG)
- **Logic**: When it's our turn, calculate the "Scarcity" of each remaining position and pick the best player for the most scarce slot.
  - **Scarcity Calculation**: $\max_{p} \left( \frac{\text{Slots Remaining}}{\text{Available Players in Market}} \right)$
- **Flaw**: It is purely myopic: One might pick a mediocre Catcher just because the position is "scarce," missing out on a once-in-a-generation superstar at another position.

<!--
Presenter notes:
To bridge the gap between optimality and speed, we designed two heuristic algorithms.

The first one is the baseline method: **Direct Greedy**.

The idea is simple. At each pick, the algorithm estimates which position is most scarce by comparing remaining roster slots with available players in the market. Then it selects the best player for the most scarce position.

This is fast and intuitive, but it is also myopic. For example, it may draft a mediocre catcher just because catcher looks scarce, while missing a much more valuable superstar at another position.

So Direct Greedy gives us a useful baseline, but it does not fully capture the timing value of a draft pick.
-->
---
## 8. Opportunity Cost Greedy (OCG)
<span class="highlight">Expanding the Strategic Horizon</span>

- **Core Concept**: Incorporate economic concepts, "Delay-Cost", into the greedy choice.
- **Decision Workflow**:
  1. Evaluate all remaining roster gaps.
  2. Identify the best player available **now** for each slot ($V_{\text{now}}$).
  3. Forecast the best player likely to remain for that slot by **our next pick** ($V_{\text{next}}$).
  4. Calculate **Opportunity Cost**: $\text{Score} = V_{\text{now}} - V_{\text{next}}$
  5. Select the player/position that minimizes this potential loss.

> OCG quantifies the "cost of waiting," allowing for fast decisions that retain IP-like strategic foresight.

<!--
Presenter notes:
Our main heuristic is **Opportunity Cost Greedy**, or OCG.

The key idea is to measure the **cost of waiting**.

At each pick, OCG first looks at all remaining roster gaps. For each position, it identifies the best player available now, which we call \(V_{\text{now}}\).

Then it forecasts the best player who is likely to remain available by our next pick, called \(V_{\text{next}}\).

The opportunity cost is the difference between these two values. If the difference is large, waiting is expensive, so we should draft that position now. If the difference is small, we can safely delay.

This gives OCG some strategic look-ahead, while still keeping the algorithm fast enough for live decisions.
-->
---
## 9. Algorithms: Complexity Analysis

- **Implementation Details**:
  - We maintain a **Max-Heap (Priority Queue)** for every position.
  - **Lazy Deletion**: Players taken by opponents aren't removed instantly; they are validated only when popped from the heap.
- **Performance**:
  - Let $n$ = total players, $r$ = roster size, $p$ = number of positions.
  - **Total Complexity**: $\mathcal{O}(n \log n + r \cdot p)$ (same as DG)

<div class="card" style="text-align:center; margin-top:20px; color:#1e40af; font-weight:bold;">
  OCG guarantees near-linear execution time, handling millions of variables in seconds.
</div>

<!--
Presenter notes:
For implementation, we maintain a max-heap, or priority queue, for every position.

This allows the algorithm to quickly find the best available player for each roster slot.

We also use lazy deletion. When opponents draft players, we do not immediately remove those players from every heap. Instead, when a player is popped from a heap, we check whether he is still available. If not, we discard him and continue.

This improves efficiency because we avoid many unnecessary updates.

Let \(n\) be the total number of players, \(r\) be the roster size, and \(p\) be the number of positions. The total complexity is \(O(n \log n + r \cdot p)\), which is the same order as Direct Greedy.

So OCG adds strategic look-ahead without sacrificing real-time performance.
-->
---
## Real-Data Validation

Using 2026 Projection Data:

| Scoring System | Algorithm | **Optimal Gap Ratio** |
| :--- | :--- | :--- |
| **Yahoo** | **OCG (Ours)** | <span class="blue-text">**0.50%**</span> |
| | Direct Greedy | 3.24% |
| **FanGraphs** | **OCG (Ours)** | <span class="blue-text">**1.24%**</span> |
| | Direct Greedy | 3.36% |

> **Result**: OCG consistently stays within **<1.5%** of the mathematical optimum, significantly outperforming the standard greedy approach.

<!--
Presenter notes:
We first validate the algorithms using real 2026 projection data.

The table compares OCG and Direct Greedy under Yahoo and FanGraphs scoring. The metric is the optimal gap ratio, which measures how far the heuristic solution is from the IP optimum.

Under Yahoo scoring, OCG has a gap of only 0.50%, while Direct Greedy has a gap of 3.24%.

Under FanGraphs scoring, OCG has a gap of 1.24%, while Direct Greedy has a gap of 3.36%.

This shows that OCG consistently stays within 1.5% of the mathematical optimum and clearly outperforms the standard greedy approach.
-->
---
<!-- _class: impact-slide -->

# Synthetic Data & Evaluation
## Proving Robustness in Extreme Environments

<!--
Presenter notes:
Real data validation is important, but one season of data may not cover all possible market conditions.

Therefore, we also design synthetic experiments. These experiments allow us to control the environment and test whether our algorithm remains robust under extreme or unusual draft conditions.
-->
---
## Four Dimensions of Synthetic Testing

We design four factors for experiments to test the boundaries of our algorithm:

<div class="grid-2" style="gap:20px; margin-top:15px;">
<div class="card" style="padding:20px;">
  <div class="tag">Factor 1</div>
  <strong>Points Distribution</strong><br>
  The distribution of players' values. <br>
  (normal / uniform / right-skewed(1:9))
</div>
<div class="card" style="padding:20px;">
  <div class="tag">Factor 2</div>
  <strong>Position Eligibility</strong><br>
  From multi-position utility players to strict single-slot players.
</div>
<div class="card" style="padding:20px;">
  <div class="tag">Factor 3</div>
  <strong>Market Uncertainty</strong><br>
  Testing sensitivity to ADP noise and systemic bias (δ).
</div>
<div class="card" style="padding:20px;">
  <div class="tag">Factor 4</div>
  <strong>Demand Ratio</strong><br>
  Simulating "Scarcity" markets v.s. "Oversupply" markets.
</div>
</div>

<!--
Presenter notes:
We test four main dimensions.

The first is the distribution of player points. We consider normal, uniform, and star-heavy distributions.

The second is position eligibility. Some players may be flexible and eligible for multiple positions, while others may be restricted to a single position.

The third is market uncertainty. We test how sensitive the algorithm is to ADP noise and systematic bias.

The fourth is the demand ratio. This controls whether the player pool is tight or abundant relative to roster needs.

Together, these factors let us test the algorithm in a much wider range of environments than real data alone.
-->
---
<style scoped>
h2 { margin-bottom: 0.3em !important; }
table { font-size: 15px !important; }
th { padding: 6px 8px !important; }
td { padding: 4px 8px !important; }
</style>

## Synthetic Data: Scenario Matrix

| ID | Main Factor | Demand Ratio ($D$) | Points Distribution ($v_i$) | Position Eligibility ($E_i$) | ADP Noise ($\delta, \sigma$) |
| :--- | :--- | :---: | :--- | :--- | :--- |
| S1 | **Baseline** | 3 | Normal | Roster-Ratio | (0, 30) |
| S2 | Points: Uniform | 3 | **Uniform** | Roster-Ratio | (0, 30) |
| S3 | Points: Star-Heavy | 3 | **High-Low** | Roster-Ratio | (0, 30) |
| S4 | Pos: Uniform-by-Type | 3 | Normal | **Uniform-by-Type** | (0, 30) |
| S5 | Pos: Point-Flexible | 3 | Normal | **Point-Flexible** | (0, 30) |
| S6 | Pos: Single-Position | 3 | Normal | **Single-Position** | (0, 30) |
| S7 | Market: Efficient | 3 | Normal | Roster-Ratio | **(0, 0)** |
| S8 | Market: Mild Noise | 3 | Normal | Roster-Ratio | **(0, 60)** |
| S9 | Market: Chaotic | 3 | Normal | Roster-Ratio | **(+5, 30)** |
| S10 | Market: Chaotic | 3 | Normal | Roster-Ratio | **(+10, 30)** |
| S11 | Demand: High | **1** | Normal | Roster-Ratio | (0, 30) |
| S12 | Demand: Low | **10** | Normal | Roster-Ratio | (0, 30) |

<!--
Presenter notes:
This table summarizes the 14 synthetic scenarios.

Scenario S1 is the baseline. Then we change one major factor at a time, such as the points distribution, position flexibility, market accuracy, or demand ratio.

For example, S3 uses a star-heavy point distribution, where a small number of elite players account for a large share of total value.

S6 uses single-position eligibility, which makes roster construction harder because players cannot flex into multiple slots.

S13 represents a high-demand market, where available players are scarce compared with roster needs.

By comparing results across these scenarios, we can identify where OCG provides the greatest advantage.
-->
---
<style scoped>
h2 {
  margin-bottom: 0.35em !important;
}
table {
  width: 100% !important;
  font-size: 16px !important;
  line-height: 1.18 !important;
}
th {
  padding: 8px 10px !important;
}
td {
  padding: 5px 10px !important;
}
</style>

## All data result

| Scenario | Description | DG optimal_gap_ratio | OCG optimal_gap_ratio | Improve |
|---|---|---:|---:|---:|
| S1 | Baseline (Normal / Roster-Ratio / $D=3$ / $(0,30)$) | 4.79% ± 1.18% | **1.92% ± 0.57%** | 3.02% ± 1.34% |
| S2 | Points: Uniform | 3.24% ± 0.77% | **1.44% ± 0.59%** | 1.87% ± 0.65% |
| S3 | Points: Star-Heavy / High-Low | 8.39% ± 2.40% | **2.87% ± 1.32%** | <span class="highlight">6.10% ± 3.46%</span> |
| S4 | Pos: Uniform-by-Type | 4.89% ± 0.62% | **1.07% ± 0.43%** | 4.02% ± 0.82% |
| S5 | Pos: Point-Flexible | 5.36% ± 1.66% | **1.34% ± 0.68%** | 4.27% ± 1.83% |
| S6 | Pos: Single-Position | 5.11% ± 1.48% | **0.94% ± 0.65%** | <span class="highlight">4.42% ± 1.95%</span> |
| S7 | Market: Efficient / $(0,0)$ | 1.47% ± 0.48% | **0.48% ± 0.23%** | 1.00% ± 0.50% |
| S8 | Market: Mild Noise / $(0,60)$ | 5.56% ± 1.58% | **2.43% ± 1.55%** | 3.33% ± 1.43% |
| S9 | Market: Chaotic / $(+5,30)$ | 5.54% ± 1.57% | **1.64% ± 0.75%** | <span class="highlight">4.16% ± 1.50%</span> |
| S10 | Market: Chaotic / $(+10,30)$ | 5.42% ± 1.21% | **1.72% ± 0.95%** | 3.92% ± 1.03% |
| S11 | Demand: High / $D=1$ | 8.81% ± 2.19% | **2.64% ± 1.23%** | <span class="highlight">6.82% ± 3.13%</span> |
| S12 | Demand: Low / $D=10$ | 3.29% ± 0.85% | **1.16% ± 0.51%** | 2.20% ± 0.83% |

<!--
Presenter notes:
This table shows selected results from the synthetic experiments.

Across the scenarios, OCG consistently has a smaller optimality gap than Direct Greedy.

For example, in the baseline case, Direct Greedy has a gap of 4.79%, while OCG reduces it to 1.92%.

In the star-heavy case, the gap falls from 8.39% to 2.87%. In the high-demand case, it falls from 8.81% to 2.64%.

The main conclusion is that OCG remains close to the IP optimum across all 14 scenarios, usually keeping the gap under 3%.
-->
---
## Strategic Insights: Where OCG Excels

OCG shows the most dramatic improvements in the following "Stress Scenarios":

- **S3 / Star-Heavy**: In markets where superstars dominate total value, DG often misses the "cliff." OCG reduces the gap from **8.39% to 2.87%**.
- **S6 / Single-Position**: With zero flexibility, early mistakes are fatal. OCG's look-ahead prevents these traps.

| Environment Factor | Scenario | Improvement over DG |
| :--- | :---: | ---: |
| Value Curve | Star-Heavy | **+6.10%** |
| Flexibility | Single-Position | **+4.42%** |

<!--
Presenter notes:
The results show that OCG is especially strong in stress scenarios.

In the star-heavy scenario, Direct Greedy often misses the value cliff. It may focus on positional scarcity and fail to secure elite players before they disappear. OCG reduces the gap from 8.39% to 2.87%.

In the single-position scenario, early mistakes are costly because there is no positional flexibility. OCG's look-ahead helps prevent these traps.
-->
---
## Strategic Insights: Where OCG Excels

- **S9 / Chaotic Market**: Even when players are drafted slightly differently than ADP ($\delta=5$), OCG remains robust.
- **S11 / High Demand**: When the player pool is tight, OCG's ability to "secure" value before it disappears is critical.

| Environment Factor | Scenario | Improvement over DG |
| :--- | :---: | ---: |
| Market Accuracy | Chaotic Noise | **+4.16%** |
| Scarcity | High Demand | **+6.82%** |

<!--
Presenter notes:
In chaotic market scenarios, where players are drafted differently from ADP, OCG still remains robust.

Finally, in high-demand markets, the player pool is tight. OCG performs well because it can identify when waiting would cause a large loss in value.
-->
---
## Stress Testing: Runtime Scaling

**Approx. Variables** = $n \times (1 + p + r)$
*(n: Players, p: Positions, r: Roster size)*

| Stress Level | Players | Teams | DG Time | OCG Time | IP Time | Status |
| :--- | ---: | ---: | ---: | ---: | ---: | :--- |
| small | 5,760 | 12 | 0.79s | 0.85s | 4.23s | OPTIMAL |
| medium | 9,600 | 15 | 0.95s | 1.14s | 12.23s | OPTIMAL |
| large | 21,600 | 15 | 1.98s | 2.34s | 54.26s | OPTIMAL |
| xlarge | 64,000 | 20 | 6.17s | 10.36s | 276.89s | OPTIMAL |
| **timeout** | 184,320 | 24 | 17.76s | **23.28s** | **1869s+** | **TIMEOUT** |

<!--
Presenter notes:
Next, we evaluate runtime scaling.

The approximate number of variables grows with the number of players, positions, and roster size. As the test size increases, IP becomes much slower.

For small and medium cases, IP can still solve the problem optimally. But as the player pool grows, runtime increases sharply.

In the timeout case, with more than 184,000 players and 24 teams, IP runs for more than 1,869 seconds and times out.

In contrast, both DG and OCG remain fast. OCG completes the largest case in about 23 seconds.

This confirms that OCG is much more practical for large-scale or real-time draft environments.
-->
---
## Scaling Visualization

<div style="text-align: center;">
  <img src="../experiments/synthetic/scaling_summary/runtime_by_variable_count.png" width="900">
</div>

<!--
Presenter notes:
The visualization shows the same runtime pattern more clearly.

As the number of variables increases, the IP curve rises much faster than the heuristic methods.

Direct Greedy is slightly faster than OCG, but the difference is small compared with the improvement in solution quality.

This is the key trade-off of our method: OCG spends a little more computation time than a simple greedy algorithm, but it achieves much better draft quality while still remaining fast enough for practical use.
-->
---
## Draft Simulation: One OCG vs 11 DG Teams (Yahoo)

![height:500px center](../experiments/competitive_draft/ocg_vs_dg_2026/ocg_vs_dg_yahoo_by_draft_position.png)

<!--
Presenter notes:
Next, we simulate a competitive draft where one OCG team drafts against eleven Direct Greedy teams under Yahoo scoring.

The chart compares team outcomes by draft position. This test moves beyond a single-team benchmark and asks whether OCG still creates value when all teams are competing for the same player pool.

The main takeaway is that OCG remains competitive across draft positions because it makes better timing decisions during the draft.
-->
---
## Draft Simulation: One OCG vs 11 DG Teams (FanGraphs)

![height:500px center](../experiments/competitive_draft/ocg_vs_dg_2026/ocg_vs_dg_fangraph_by_draft_position.png)

<!--
Presenter notes:
We repeat the same competitive draft simulation under FanGraphs scoring.

This is important because FanGraphs scoring values batting and pitching events differently from Yahoo scoring. If OCG performs well under both scoring systems, then the method is not only tuned to one particular league format.

The result again supports the robustness of opportunity-cost reasoning in a competitive draft room.
-->
---
## 10. Conclusions & Future Extensions

1. **OCG provides a deployable balance between time efficiency and draft performance.**
-  Outperformed all baseline greedy variants in simulations across diverse draft positions.
-  Generate decisions in seconds even in large-scaled scenarios while maintaining high near-optimality.

2. **OCG offers significant Competitive Edges in scarce of tight markets.** 
3. **Future Extensions**: 
    - **Stochastic Opponent Modeling:** incorporate probability distributions and more strategies for opponent behaviors (e.g., team bias, "homer" picks).
    - **Real-World Application :** Transitioning from academic simulation to live 2026 Fantasy Baseball competition game to again validate our strategies!


<!--
 By quantifying the "delay cost," OCG captures the essence of IP logic while remaining fast enough to handle **a large scale of decision variables** under a short period of time.-->

<!--
Presenter notes:
To conclude, we provide three recommendations for fantasy baseball managers.

First, Direct Greedy is risky. Choosing only by positional scarcity or best available player can lead to significant value loss, especially in star-heavy or high-demand markets.

Second, IP is a strong benchmark, but not a practical live-draft tool. It is useful for post-draft analysis or pre-season simulation, but its runtime makes it difficult to use during a timed draft.

Third, OCG is the deployable solution. By quantifying the delay cost, OCG captures much of the strategic logic of IP while remaining fast enough for real-time decision making.

In our largest test, it handled around 50 million decision variables in under 25 seconds.

There are still several limitations and possible extensions.

First, our current model treats ADP as a deterministic threshold. In future work, we can build probabilistic opponent models that capture different drafting behaviors, such as team preferences, risk tolerance, or favorite players.

Second, player projections are treated as average values. But in reality, players have risk. Injuries, slumps, and breakout seasons can all affect performance.

Therefore, future versions can incorporate Monte Carlo simulation and risk preferences. This would allow the algorithm to balance upside and safety depending on the manager's strategy.
-->
---
<!-- _class: title-slide -->
# Thank You for Watching!

<div class="author-block">
  <strong>OR114-2 Final Project, Group 4</strong><br>
  B13705051 Chou, Meng-Cheng | B13902103 Cheng, Yu-Hung | B13303153 Chan, Shu-Yu | B11705039 Lee, Ying-Ying<br>
</div>

<!--
Presenter notes:
Thank you for your attention.

This project shows that fantasy baseball drafting can be modeled as a strategic optimization problem. By combining real data, integer programming, and a fast opportunity-cost heuristic, we can produce draft recommendations that are both high-quality and practical.

We are happy to answer any questions.
-->
