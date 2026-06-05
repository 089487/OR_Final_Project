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

---

## 1. Introduction: The Cornerstone of Roster Building

- **What is the Draft?**
  Before the season begins, General Managers (GMs) take turns selecting players from a pool of amateur or free-agent talent.
- **The Challenge**:
  How to precisely fill roster slots and maximize total team value given limited picks and intense competition?

<div class="img-right">
  <img src="image-2.jpeg" width="500">
</div>

---

<!-- _class: impact-slide -->

# Problem Settings

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

---

## 3. Problem Settings II: Snake Draft Mechanism

While the MLB uses a fixed-order draft based on the previous year's record, we utilize a **"Snake Draft"** mechanism to focus purely on **strategic optimization**.

- **Why and What is Snake Draft?**
  The order reverses every round (1-2-3, 3-2-1), which eliminates the absolute resource advantage of the first pick. The mechanism is also utilized in the game Fantasy Baseball.
- **Mathematical Slot Mapping**:
  For $M$ managers and our initial pick $j$ ($1 \le j \le M$), our absolute pick $k$ in round $r$ is:
  - **Odd Rounds (Forward)**: $k = (r - 1)M + j$
  - **Even Rounds (Reverse)**: $k = rM - j + 1$

---

## 4. Problem Settings III: Roster Requirements

A valid team must strictly satisfy specific roster constraints shown below:

**The 16-slot starting lineup**

| Position | C | 1B | 2B | 3B | SS | OF | Util | SP | RP |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Required Slots** | 1 | 1 | 1 | 1 | 1 | 3 | 1 | 5 | 2 |

*Note: The **Util (Utility)** slot is restricted to hitters only. (pitchers cannot fill the spot!)*

---

<!-- _class: impact-slide -->

# Real Data Collection
## Transforming the Baseball Market into Data

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

---

#### 2. Average Draft Position (ADP)
- Collected aggregate ADP from **FantasyPros**, combining data across Yahoo, ESPN, CBS, and NFBC.
- Used to define the "availability window" for each player in the draft pool.

![alt text](image-1.png)

---

<!-- _class: impact-slide -->

# Model Formulation

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

---

## 6. Model Formulation II: Constraints

1. **Draft Logic & Roster Integrity**:
   $$ \sum_{i \in I} z_{ik} = 1 \quad \forall k \in K \quad \text{(One player per pick)} $$
   $$ \sum_{p \in P} x_{ip} = y_i \quad \forall i \in I \quad \text{(Assign position if drafted)} $$
   $$ \sum_{i \in I} x_{ip} = r_p \quad \forall p \in P \quad \text{(Satisfy roster requirements)} $$

2. **Market Availability Constraint**:
   $$ z_{ik} = 0 \quad \text{if } S_k > \text{adp}_i + \delta, \quad \forall i \in I, k \in K $$
   > *If our pick $S_k$ is later than the player's $\text{adp}_i + \delta$ (buffer), the player is considered "unavailable."*

---

<!-- _class: impact-slide -->

# The Bottleneck
## Why Traditional IP Isn't Enough?

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

---

## 7. Algorithms: Heuristic Design

To bridge the gap between optimality and speed, we designed two heuristics.

### ❌ Baseline: Direct Greedy (DG)
- **Logic**: When it's our turn, calculate the "Scarcity" of each remaining position and pick the best player for the most scarce slot.
  - **Scarcity Calculation**: $\max_{p} \left( \frac{\text{Slots Remaining}}{\text{Available Players in Market}} \right)$
- **Flaw**: It is purely myopic: One might pick a mediocre Catcher just because the position is "scarce," missing out on a once-in-a-generation superstar at another position.

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

---

<!-- _class: impact-slide -->

# Synthetic Data & Evaluation
## Proving Robustness in Extreme Environments

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
| S9, 10 | Market: Chaotic | 3 | Normal | Roster-Ratio | **(±5, 30)** |
| S11, 12 | Market: Chaotic | 3 | Normal | Roster-Ratio | **(±10, 30)** |
| S13 | Demand: High | **1** | Normal | Roster-Ratio | (0, 30) |
| S14 | Demand: Low | **10** | Normal | Roster-Ratio | (0, 30) |

---

## Strategic Insights: Where OCG Excels

OCG shows the most dramatic improvements in the following "Stress Scenarios":

- **S3 / Star-Heavy**: In markets where superstars dominate total value, DG often misses the "cliff." OCG reduces the gap from **8.39% to 2.87%**.
- **S6 / Single-Position**: With zero flexibility, early mistakes are fatal. OCG's look-ahead prevents these traps.

| Environment Factor | Scenario | Improvement over DG |
| :--- | :---: | ---: |
| Value Curve | Star-Heavy | **+6.10%** |
| Flexibility | Single-Position | **+4.42%** |

---

## Strategic Insights: Where OCG Excels

- **S10 / Chaotic Market**: Even when players are drafted slightly differently than ADP ($\delta=+5$), OCG remains robust.
- **S13 / High Demand**: When the player pool is tight, OCG's ability to "secure" value before it disappears is critical.

| Environment Factor | Scenario | Improvement over DG |
| :--- | :---: | ---: |
| Market Accuracy | Chaotic Noise | **+4.16%** |
| Scarcity | High Demand | **+6.82%** |

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

## all data result

| Scenario | Description | DG optimal_gap_ratio | OCG optimal_gap_ratio |
|---|---|---:|---:|
| S1 | Baseline (Normal / Roster-Ratio / 3:1 / $(0,30)$) | 4.79% ± 1.18% | **1.92% ± 0.57%** |
| S2 | Points: Uniform | 3.24% ± 0.77% | **1.44% ± 0.59%** |
| S3 | Points: Star-Heavy / High-Low | 8.39% ± 2.40% | **2.87% ± 1.32%** |
| S4 | Pos: Uniform-by-Type | 4.89% ± 0.62% | **1.07% ± 0.43%** |
| S5 | Pos: Point-Flexible | 5.36% ± 1.66% | **1.34% ± 0.68%** |
| S6 | Pos: Single-Position | 5.11% ± 1.48% | **0.94% ± 0.65%** |
| S7 | Market: Efficient / $(0,0)$ | 1.47% ± 0.48% | **0.48% ± 0.23%** |
| S8 | Market: Mild Noise / $(0,60)$ | 5.56% ± 1.58% | **2.43% ± 1.55%** |
| S9 | Market: Chaotic / $(-5,30)$ | 4.90% ± 1.24% | **1.83% ± 0.82%** |
| S10 | Market: Chaotic / $(+5,30)$ | 5.54% ± 1.57% | **1.64% ± 0.75%** |
| S11 | Market: Chaotic / $(-10,30)$ | 4.65% ± 1.32% | **1.90% ± 0.77%** |
| S12 | Market: Chaotic / $(+10,30)$ | 5.42% ± 1.21% | **1.72% ± 0.95%** |
| S13 | Demand: High / $D=1$ | 8.81% ± 2.19% | **2.64% ± 1.23%** |
| S14 | Demand: Low / $D=10$ | 3.29% ± 0.85% | **1.16% ± 0.51%** |

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

---

## Scaling Visualization

<div style="text-align: center;">
  <img src="../experiments/synthetic/scaling_summary/runtime_by_variable_count.png" width="900">
</div>

---

## 10. Conclusions & Business Recommendations

**Final Strategic Recommendations for GMs:**

1. **Direct Greedy is Risky**: Relying on "scarcity" or "best-player-available" without considering timing leads to significant value loss, especially in star-heavy markets.
2. **IP is a Benchmark, not a Tool**: Use IP for post-draft analysis or pre-season simulation. Its runtime makes it unviable for live, high-stakes draft environments.
3. **OCG is the Deployable Solution**: By quantifying the "delay cost," OCG captures the essence of IP logic while remaining fast enough to handle **50 million decision variables** in under 25 seconds.

---

## Limitations & Future Extensions

Our roadmap for "System 2.0":

- **Probabilistic Opponent Modeling**:
  Currently, ADP is treated as a deterministic threshold. Future versions will incorporate probability distributions for opponent behavior (e.g., team bias, "homer" picks).
- **Monte Carlo Risk Integration**:
  Player projections are averages. Incorporating variance (injury risk, slump risk) will allow the OCG to optimize for "Upside" vs. "Safety" depending on team needs.

---

<!-- _class: title-slide -->
# Thank You for Your Attention!

<div class="author-block">
  <strong>OR114-2 Final Project, Group 4</strong><br>
  B13705051 Chou, Meng-Cheng | B13902103 Cheng, Yu-Hung | B13303153 Chan, Shu-Yu | B11705039 Lee, Ying-Ying<br>
</div>