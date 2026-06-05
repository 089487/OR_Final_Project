---
marp: true
theme: default
paginate: true
size: 16:9
math: mathjax
style: |
  @import url('https://fonts.googleapis.com/css2?family=Segoe+UI:wght@400;700&family=Roboto+Mono&display=swap');

  section {
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    background-color: #ffffff;
    color: #2c3e50;
    font-size: 22px;
    background-image: linear-gradient(to bottom right, #fdfdfd, #f4f7f6);
  }

  h1 { color: #002D72; font-weight: 800; font-size: 42px; border-bottom: 3px solid #002D72; }
  h2 { color: #002D72; font-weight: 700; font-size: 30px; margin-top: 10px; border: none;}
  
  /* Baseball Thematic Colors */
  .navy { color: #002D72; } /* MLB Navy */
  .green { color: #005A32; font-weight: bold; } /* Grass Green */
  .clay { color: #A54B23; font-weight: bold; } /* Infield Clay */

  section.title-slide {
    background: #002D72;
    color: white;
    text-align: center;
    display: flex;
    flex-direction: column;
    justify-content: center;
  }
  section.title-slide h1 { color: #ffffff; border: none; font-size: 50px; }
  section.title-slide h2 { color: #D3D3D3; border: none; font-size: 28px; }

  .card {
    background: #ffffff; padding: 18px; border-radius: 8px;
    box-shadow: 0 4px 12px rgba(0,0,0,0.08); border-left: 6px solid #002D72;
    margin-bottom: 15px;
  }
  
  table { width: 100%; border-collapse: collapse; font-size: 19px; margin-top: 10px; }
  th { background-color: #002D72 !important; color: white !important; padding: 10px; }
  td { padding: 8px; border-bottom: 1px solid #ddd; text-align: center; }
  
  .grid-2 { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }
  .footer { position: absolute; bottom: 20px; left: 50px; font-size: 14px; color: #7f8c8d; }
---

<!-- _class: title-slide -->

# Strategic Fantasy Baseball Draft Optimization
## Scalable Decision-Support for Modern Front Offices

<div style="margin-top: 50px;">
  <strong>OR114-2 Final Project, Group 4</strong><br>
  周孟承 | 鄭宇宏 | 詹舒宇 | 李盈盈<br>
</div>

---

## 01. Introduction: The Analytics Revolution

**"The edge is no longer in identifying talent, but in the strategy of acquiring it."**

*   **The Convergence**: In 2026, scouting models (WAR, Statcast) have converged. Most teams value the same players similarly.
*   **The Challenge**: A draft is a **multi-period portfolio optimization problem** under extreme competition.
*   **The Problem**: How to balance current needs with future talent availability while respecting strict roster constraints.

<div class="card">
  <strong>Key Question:</strong> Which player must I draft <u>now</u> because market timing and positional scarcity will make equivalent options disappear by my next turn?
</div>

---

## 02. Problem Definition: The Snake Draft

We simulate a **Snake Draft** environment to analyze pure strategic decision-making.

*   **Format**: 12 teams, 16 rounds. The picking order reverses each round (S-curve).
*   **Strategic Interdependence**: Your choice at pick #6 directly affects the pool available at your next pick at #19.
*   **Average Draft Position (ADP)**:
    *   We treat ADP as a proxy for **Market Depletion**.
    *   If current Pick > (ADP + Tolerance $\delta$), the player is considered "off the board."

---

## 03. Roster Constraints: The "Scarcity" Puzzle

A drafted roster must perfectly fulfill the following **16 active slots**:

| Position | C | 1B | 2B | 3B | SS | OF | Util | SP | RP |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Slots** | 1 | 1 | 1 | 1 | 1 | 3 | 1 | 5 | 2 |

*   **The "Hitter-Only" Utility**: The `Util` slot adds a layer of complexity; it accepts any hitter but no pitchers, creating a "flexible vs. rigid" trade-off.
*   **Positional Weighting**: Scarcity varies by position. Shortstops (SS) are rare; Outfielders (OF) are abundant. 

---

## 04. Data Collection: 2026 Real-World Metrics

We validated our system using projected data for the **2026 MLB Season** from **FantasyPros**.

1.  **Projected Value ($v_i$)**: Calculated using two distinct benchmarks:
    *   **Yahoo**: Focuses on traditional counting stats (R, RBI, Wins).
    *   **FanGraphs**: Incorporates advanced metrics (weighted linear values).
2.  **ADP Data**: Market consensus collected across platforms (ESPN, CBS, Yahoo).

<div class="card">
  This creates a high-fidelity environment where we can test our algorithms against actual MLB player distributions.
</div>

---

## 05. Model Formulation: Integer Programming (IP)

We first formulate the exact ADP-aware Integer Linear Program (ILP) as our benchmark.

*   **Objective**: $\max \sum_{i \in I} v_i y_i$ (Maximize total roster points)
*   **Decision Variables**:
    *   $y_i \in \{0,1\}$: Player $i$ is drafted.
    *   $x_{ip} \in \{0,1\}$: Player $i$ assigned to position $p$.
    *   $z_{ik} \in \{0,1\}$: Player $i$ selected at owned pick $k$.

*   **Vital Constraint (Market Availability)**:
    $z_{ik} = 0 \quad \text{if } S_k > \text{adp}_i + \delta$
    *(A player cannot be drafted if the current pick is later than their expected depletion point).*

---

## 06. The Bottleneck: The Scalability Wall

**Why is the perfect IP solution not practical for a live draft?**

1.  **NP-Hardness**: The Draft Pool scales to **tens of thousands** of eligible players.
2.  **Exponential Explosion**: The Branch-and-Bound tree of the ILP grows exponentially with $n$.
3.  **Real-Time Pressure**: Draft rooms operate on a 60-90 second clock. 
4.  **Failure**: In large-scale scenarios (100k+ players), Gurobi exceeds memory limits or solver time-outs.

> **Requirement**: We need a heuristic that mimics IP logic but executes in linear time.

---

## 07. Algorithm 1: Direct Greedy (Baseline)

The **Direct Greedy (DG)** represents the standard "Fill a need" mentality.

*   **Logic**: At each pick, scan all open positions.
*   **Metric**: Identify the position with the highest **Scarcity Ratio**.
    $$\text{Scarcity} = \frac{\text{Remaining Need for Position } p}{\text{Active Available Players for } p}$$
*   **Action**: Pick the highest-valued player in that position.
*   **Weakness**: "Positional Blindness." It might pick a mediocre Catcher just because it's a "need," missing out on a once-in-a-generation talent in another slot.

---

## 08. Algorithm 2: Opportunity Cost Greedy (Proposed)

Our flagship algorithm, **Opportunity Cost Greedy (OCG)**, looks ahead to the **next pick**.

*   **Core Concept**: "What is the cost of waiting one more round?"
*   **Process**:
    1.  $v_{cur} \leftarrow$ Points of best player available **now** for position $p$.
    2.  $v_{fut} \leftarrow$ Points of best player available **at next pick** for position $p$.
    3.  $\text{Score} = v_{cur} - v_{fut}$ (**Delay Cost Calculation**)
*   **Decision**: Draft the player where the **Opportunity Cost** is maximized.

<div class="card">

**Data Structure**: Uses Max-Heaps with <u>Lazy Deletion</u> to maintain $\mathcal{O}(n \log n)$ efficiency.

</div>

---

## 09. Methodology: Synthetic Stress Testing

To prove robustness, we developed a **Synthetic Data Generator** to stress-test 4 factors:

1.  **Factor A (Points Distribution)**:
    *   *Normal*: standard year.
    *   *Star-Heavy*: Top 10% of players hold 50% of the value.
2.  **Factor B (Positional Rigidity)**: 
    *   *Versatile*: Many "Utility" players.
    *   *Single-Position*: Eliminates all flexibility (The hardest test).
3.  **Factor C (Market Noise)**: Introducing Gaussian error to ADP ($\sigma_{adp}$).
4.  **Factor D (Demand Ratio)**: Simulating "Extreme Scarcity" (Supply $\approx$ Demand).

---

## 10. Performance Evaluation: Real-World Results

Comparison of **Optimality Gap** (Distance from perfect IP solution):

| Dataset | Algorithm | Optimal Gap % | Improvement over DG |
| :--- | :--- | :---: | :---: |
| **Yahoo 2026** | **OCG** | <span class="green">0.50%</span> | **+2.74%** |
| | Direct Greedy | 3.24% | - |
| **FanGraphs 2026**| **OCG** | <span class="green">1.24%</span> | **+2.12%** |
| | Direct Greedy | 3.36% | - |

*   **Finding**: OCG consistently reduces the error of the Greedy baseline by **more than half**, staying within **1.3%** of the mathematical optimum.

---

## 11. Analysis: Winning in Star-Heavy Markets

**Scenario S3: Star-Heavy Points Distribution**

*   In markets where talent is concentrated in a few elites, the **"Cost of Waiting"** is massive.
*   **Direct Greedy** often "waits" on elites to fill positional needs, losing them to opponents.
*   **OCG** quantifies this cost, securing elite assets before the value **"cliff"** occurs.
*   **Result**: OCG provided a **+6.10% improvement** in total roster value in these scenarios.

<div class="card">
  This proves OCG is the superior "Big Game Hunter" for drafting superstars.
</div>

---

## 12. Analysis: Scalability Stress Test

We tested the limits by dumping 180,000+ players into the database.

| Instance | Players | IP Runtime | OCG Runtime | Status |
| :--- | :--- | :--- | :--- | :--- |
| Medium | 9,600 | 12.23 s | 1.14 s | Optimal |
| X-Large | 64,000 | 276.90 s | 10.36 s | Optimal |
| **Limit** | **184,320** | <span class="clay">1869.8 s</span> | <span class="green">23.28 s</span> | **TIMEOUT** |

*   **The Verdict**: While IP finds perfect rosters, it is **operationally dead-on-arrival** for large datasets. 
*   **OCG Efficiency**: Processes 50-million variable equivalents in **under 25 seconds**.

---

## 13. Strategic Insights: The "Wait" Logic

**Why does OCG beat standard greedy?**

1.  **Navigating Scarcity**: In environments where almost every player is drafted (Demand $\approx$ Supply), OCG anticipates future collapses and drafts "deep" positions late.
2.  **Positional Flexibility**: OCG understands when a "Utility" player is a luxury vs. a necessity.
3.  **Resilience to Noise**: Even when opponents act chaotically (Market Noise), OCG's relative difference calculation acts as a natural hedge.

---

## 14. Conclusions & Recommendations

**For the Front Office:**

*   **Discard Naive Greedy**: "Fill-the-need" mentalities bleed significant roster value (approx. 3-8% per season).
*   **Adopt OCG for Real-Time Decision Support**: It offers near-perfect optimization with the speed required for live draft rooms.
*   **Hybrid Approach**: Use **IP** for off-season simulations and **OCG** for the actual draft day.

<div class="card">
  <strong>Final Proof:</strong> Computational draft optimization is not just a theoretical exercise; it is a scalable, real-time weapon for competitive parity.
</div>

---

## 15. Future Extensions & Q&A

*   **Probabilistic Modeling**: Moving from static ADP to Monte Carlo simulations of opponent behavior.
*   **Injury Risk Variance**: Incorporating standard deviations of player projections into the objective function.
*   **Dynamic Weighting**: Updating "Opportunity Cost" in real-time as opponents' rosters are filled.

**Thank you for your attention.**

<div class="footer">Group 4 | OR114-2 Final Project | NTU</div>