---
marp: true
theme: default
paginate: true
size: 16:9
math: mathjax
style: |
  section {
    font-family: 'Helvetica Neue', 'PingFang TC', 'Microsoft JhengHei', sans-serif;
  }
  h1, h2 {
    color: #1f2937;
  }
  .highlight {
    color: #b45309;
    font-weight: bold;
  }
  .blue-text {
    color: #2563eb;
    font-weight: bold;
  }
  .grid-2 {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 40px;
  }
---

# Strategic Fantasy Baseball Draft Optimization
## 棒球制服組的決策支援系統：可擴展的選秀最佳化策略
<br>

**OR114-2 Final Project, Group 4**
B13705051 周孟承 | B13902103 鄭宇宏 
B13303153 詹舒宇 | B11705039 李盈盈
Spring 2026

---

## 報告大綱 (Outline)

1. **Introduction**：大聯盟制服組的視角與挑戰
2. **Problem Description**：蛇形選秀環境與大谷條款
3. **Model Formulation**：整數線性規劃 (ILP) 建模
4. **The Bottleneck**：為何傳統 ILP 遇到瓶頸？
5. **Algorithms**：機會成本貪婪演算法 (OCG)
6. **Data & Evaluation**：合成數據與壓力測試
7. **Conclusions**：商業建議與未來展望

---

## 1. Introduction: The Front Office Perspective

**「當各隊的球探數據趨於一致時，優勢在哪裡？」**

<div class="grid-2">
<div>

### 現代棒球的挑戰
- 各大聯盟 (MLB) 球隊的球探與數據投影模型（如 WAR、Fantasy Points）已高度收斂。
- 真正的競爭優勢從「單純評估球員能力」轉移到了「<span class="highlight">選秀策略與市場時機 (Draft Strategy)</span>」。

</div>
<div>

### 核心決策困境
- **Myopic Trap (短視陷阱)**：「我該現在選下這名頂級巨星？還是該先補齊稀缺的守備位置？」
- 我們的目標是將這個充滿互相依賴性的選秀決策，轉化為嚴謹的**作業研究最佳化問題**。

</div>
</div>

<!-- 
講者備註：
各位教授、助教、同學們大家好。想像我們是大聯盟球隊的制服組 (Front Office)。在現代數據棒球時代，各隊對球員的分數評估非常接近。這代表未來的優勢不在於你認不認識好球員，而在於你「什麼時候選他」。我們這組的專案，就是要用 OR 的方法，為球隊打造一套極致的選秀最佳化系統。
-->

---

## 2. Problem Description I：蛇形選秀 (Snake Draft)

現實中的 MLB 選秀是依據前一年的戰績（由爛到好）進行固定順位選秀。但為了純粹探討**「選秀策略的數學優勢」**，我們將情境抽象化為更公平的<span class="highlight">蛇形選秀</span>。

- **為什麼使用蛇形選秀？**
  消除初始順位帶來的絕對優勢，讓所有玩家的整體選秀資源相近，藉此凸顯「選秀策略」本身的重要性。每輪的選秀順序會反轉。
- **數學順位換算公式**：
  假設共有 $M$ 位玩家，我們的初始順位為 $j$ ($1 \le j \le M$)。在第 $r$ 輪時，我們擁有的整體順位 $k$ 為：
  - **奇數輪 (Forward)**：$k = (r - 1)M + j$
  - **偶數輪 (Reverse)**：$k = rM - j + 1$

<!-- 
講者備註：
為了做學術與策略上的探討，我們排除了戰績帶來的初始資源優勢，採用蛇形選秀。第一輪順位越後面的人，在第二輪就能越早選。順位的決定變成了一種可以被數學嚴格定義的序列，我們就是要在這個序列中找出利益最大化的路徑。
-->

---

## Problem Description II：球員屬性與特殊簡化

在選秀池中，每位球員擁有以下三大屬性：
1. **Projected Value ($v_i$)**：賽季預期貢獻分數（目標函數的基礎）。
2. **Eligible Positions ($E_i$)**：球員合法的守備位置。
3. **Average Draft Position (ADP)**：市場預期平均被選順位（用來模擬對手行為）。

<span class="highlight">**⚠️ 特殊簡化：大谷翔平條款 (The Ohtani Rule)**</span>
為了避免位置彈性上的邏輯過於複雜，我們在模型中**不考慮二刀流**。
- 在合成數據 (Synthetic Data) 中，不生成同時具備打者與投手身份的球員。
- 在真實的 2026 年 Yahoo/FanGraphs 數據中，大谷翔平 (Shohei Ohtani) 的「打者 (DH)」與「投手 (SP)」身份會被拆分視為**兩名獨立的球員**。

---

## Problem Description III：先發陣容需求

要完成一組有效的陣容，必須嚴格滿足以下的數量限制 (Roster Requirements)。
我們使用標準的 16 人先發名單作為基礎架構：

| 守備位置 (Position) | C | 1B | 2B | 3B | SS | OF | Util | SP | RP |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **需求人數 (Slots)** | 1 | 1 | 1 | 1 | 1 | 3 | 1 | 5 | 2 |

*註：Util (Utility) 僅限打者，投手無法填補此空缺。這將成為 ILP 限制式的重要基準。*

<!--
講者備註：
名單必須嚴格符合這個表。這就產生了有趣的 Trade-off：外野手 (OF) 跟先發投手 (SP) 需要很多人，但游擊手 (SS) 或捕手 (C) 只有一個，如果 SS 的好球員很少，我們是不是該提早搶？這就是我們模型要解決的分配問題。
-->

---

## 3. Model Formulation I：變數與目標函數

我們將問題建構為 **ADP-aware Integer Linear Program (ILP)**。
令 $I$ 為球員集合，$P$ 為守位集合，$K$ 為我們擁有的選秀籤集合。

**決策變數 (Decision Variables)**：
- $y_i \in \{0,1\}$: 是否將球員 $i$ 選入最終陣容。
- $x_{ip} \in \{0,1\}$: 是否將球員 $i$ 安排在守備位置 $p$。
- $z_{ik} \in \{0,1\}$: 是否在我們的第 $k$ 個順位，選下球員 $i$。

**目標函數 (Objective Function)**：最大化先發名單的總預期分數。
$$ \max \sum_{i \in I} v_i y_i $$

---

## Model Formulation II：核心限制式 (Constraints)

1. **選秀邏輯與名單限制**：
   $$ \sum_{i \in I} z_{ik} = 1, \quad \forall k \in K \quad \text{(每個順位選一人)} $$
   $$ \sum_{p \in P} x_{ip} = y_i, \quad \forall i \in I \quad \text{(選入必安排唯一守位)} $$
   $$ \sum_{i \in I} x_{ip} = r_p, \quad \forall p \in P \quad \text{(滿足各守備位置規定人數)} $$

2. <span class="blue-text">**市場可用性限制 (Market Availability Constraint)**</span>：
   $$ z_{ik} = 0 \quad \text{if } S_k > \text{adp}_i + \delta, \quad \forall i \in I, k \in K $$
   > *其中 $S_k$ 是該次選秀的整體順位，$\delta$ 是市場容錯緩衝值。如果我們的選秀順位已經晚於球員的 ADP+$\delta$，系統將強制我們無法選取該名球員。*

---

## 4. The Bottleneck: 為什麼傳統 ILP 不夠用？

雖然 ADP-aware ILP 能給出**絕對完美的最佳解 (God's Eye View)**，但在現實中會面臨極大的挑戰。

- **The Scalability Problem (可擴展性危機)**：
  - 棒球選秀的母體池極其龐大，大聯盟三十支球隊加上無數的新秀，球員池高達數萬至十幾萬人。
  - 我們設立的變數包含了 $I \times P$ 與 $I \times K$。當球員數 ($|I|$) 放下，ILP 的 Branch-and-Bound 搜尋空間會呈**指數爆炸**。
- **實戰的致命傷**：
  - 選秀是有**時間壓力 (Time Limit)** 的。總管不可能在選秀室等 Gurobi 跑半個小時。
  - 在巨大規模下，<span class="highlight">ILP 會直接超時 (Timeout) 或記憶體耗盡</span>。

<!--
講者備註：
ILP 的數學模型非常漂亮，但這就是所謂的學術與實務的落差。在球員數破十萬的資料庫裡，Gurobi 會直接當機。所以，我們不能只停在 ILP，我們需要一個速度極快、但品質又接近 ILP 的演算法。
-->

---

## 5. Algorithms：啟發式演算法設計 (Heuristics)

為了解決 ILP 的效能瓶頸，我們設計了兩種啟發式演算法。

### Baseline: Direct Greedy (直接貪婪法)
- **邏輯**：目光短淺 (Myopic)。每次輪到我選時，尋找目前「最缺人」的守位，並直接選下該守位目前分數最高的球員。
- **缺點**：沒有考慮未來。可能會為了一個替補游擊手，而放掉一個千載難逢的超級巨星。

<!--
講者備註：
Direct Greedy 就像是一般的休閒玩家，只看現在缺什麼就補什麼。這很快，但非常容易在後面吃虧，因為他完全沒有考慮到「機會成本」。
-->

---

## Algorithms: Opportunity Cost Greedy (OCG)
<span class="highlight">本專案提出的旗艦演算法：具備策略視野的貪婪法</span>

- **核心概念**：計算「等待的代價 (Delay-Cost)」。
- **決策流程**：
  1. 檢視目前所有缺人的守位。
  2. 找出該守位**現在能選到**的最強球員 ($V_{now}$)。
  3. 預測到**我們下一輪選秀時**，該守位還剩下的最強球員 ($V_{next}$)。
  4. 計算**機會成本**： $\text{Score} = V_{now} - V_{next}$
  5. 優先選擇機會成本（損失）最大的守位與球員。

<!--
講者備註：
OCG 的精神就是「瞻前顧後」。如果我現在不選這個外野手，下一輪剩下的外野手分數會掉 50 分；但我如果不選捕手，下一輪剩下的捕手分數只會掉 5 分。那麼 OCG 就會聰明地優先把外野手選下來。
-->

---

## Algorithms: 時間複雜度分析 (Time Complexity)

要在實戰中即時運算，資料結構的選擇至關重要。

- **實作方式**：
  - 我們為每個守備位置維護一個 **Max-Heap (優先佇列)**。
  - 使用 **Lazy Deletion**：當球員被對手選走，或被我們選走時，不立刻重整 Heap，而是等到 pop 時再檢查有效性。
- **複雜度表現**：
  - $N$ = 球員總數， $R$ = 名單人數， $P$ = 守備位置數。
  - **總時間複雜度**：$\mathcal{O}(N \log N + R \cdot P)$
  - <span class="highlight">完美保證演算法能以接近線性的時間，處理數十萬人等級的選秀池。</span>

---

## 6. Data Collection & Generation

為了全面測試演算法，我們同時使用了 **2026 Yahoo/FanGraphs 的真實投影數據**，以及高度客製化的 **合成數據生成器 (Synthetic Data Generator)**。

為什麼需要合成數據？因為我們需要分離並壓力測試四大市場變因 (Factors)：

1. **Points Distribution (天賦分佈)**：常態分佈 vs. 巨星集中 (High-Low)
2. **Positions Distribution (守位彈性)**：工具人氾濫 vs. 單一守位死綁
3. **Market Volatility (ADP 雜訊)**：市場完全效率 ($\sigma=0$) vs. 極度混亂 ($\sigma=60$)
4. **Scale & Demand (規模與稀缺度)**：測試極度缺人的市場與海量資料池

<!--
講者備註：
真實數據可以驗證演算法的實用性，但合成數據才能讓我們做「壓力測試」。在接下來的實驗中，我們會看看這四大變因如何影響選秀難度，以及我們的 OCG 演算法是否能撐住考驗。
-->

---

## 7. Performance Evaluation (實驗評估指標)

我們使用 **Optimal Gap Ratio (最佳解落差比)** 作為核心指標：

$$ \text{Gap Ratio} = \frac{Z_{\text{ILP}} - Z_{\text{Heuristic}}}{Z_{\text{ILP}}} \times 100\% $$

> *Gap 越接近 0% 越好，代表該演算法選出來的陣容總分，越接近 ILP 算出來的「完美上帝視角解答」。*

接下來我們將展示實驗結果。

---

## 實驗 N1 ~ N3：天賦分佈與守備彈性

| 情境 (Scenario) | 參數設定 (Level) | Direct Greedy | **Opportunity Cost Greedy** |
| :--- | :--- | :---: | :---: |
| **N1: Baseline** | 基準線 (Normal) | $4.79\%$ | **$1.92\%$** |
| **N2: Points Dist.** | 巨星集中 (High-Low) | $8.39\%$ | <span class="highlight">**$2.87\%$**</span> |
| **N3: Pos Dist.** | 無工具人 (Single-Pos) | $5.11\%$ | <span class="highlight">**$0.94\%$**</span> |

- **商業洞察**：
  - 在 **High-Low** (只有 10% 是超級巨星) 且不容錯的環境下，Direct Greedy 表現崩盤 (8.39%)，因為它會為補洞而錯過巨星。
  - **OCG 幾乎不受影響**，依然將損失控制在 1~2% 左右。

<!--
講者備註：
N2 實驗非常有意思。High-low 代表這個選秀池只有少數大物新秀，其他都是雜魚。Direct Greedy 這種只看眼前缺口的演算法，很容易為了解決捕手荒，放掉外野的大物。但 OCG 因為會計算未來落差，成功保住了巨星，Gap 只有 2.87%。
-->

---

## 實驗 N5：市場波動與 ADP 雜訊 ($\sigma_{\text{adp}}$)

當對手的行為無法預測時，誰能活下來？

| 雜訊強度 | 市場狀態 | Direct Greedy | **Opportunity Cost Greedy** |
| :---: | :--- | :---: | :---: |
| $\sigma=0$ | 完美效率市場 | $1.72\%$ | **$0.42\%$** |
| $\sigma=10$ | 輕微波動 | $3.34\%$ | **$0.99\%$** |
| $\sigma=30$ | 中度波動 | $5.03\%$ | **$1.80\%$** |
| $\sigma=60$ | <span class="highlight">高度混亂 (Chaos)</span>| $5.73\%$ | <span class="highlight">**$2.43\%$**</span> |

- **結論**：OCG 基於「現在與未來的相對差值」做決策，天生具備抗雜訊 (Hedging) 的能力。

---

## 實驗 N4 & N6：Scalability 終極壓力測試

這是向制服組提案的最核心關鍵：**當球員池無限放大時，誰能不當機？**

我們將名單規模放大，球員池擴張至 **184,320 人**，這使得 ILP 的決策變數飆升至 **4,900 萬個**。

| 測試等級 | 近似變數數量 | ILP 運算時間 (狀態) | **OCG 運算時間** |
| :--- | ---: | :--- | :--- |
| `stress_small` | 334,080 | 4.23 秒 (最佳解) | **0.85 秒** |
| `stress_large` | 2,289,600 | 54.26 秒 (最佳解) | **2.34 秒** |
| `stress_xlarge` | 10,880,000 | 276.89 秒 (最佳解) | **10.36 秒** |
| `timeout_target` | <span class="highlight">49,029,120</span> | <span class="highlight">**1869.8 秒 (TIMEOUT 崩潰)**</span> | <span class="blue-text">**23.28 秒**</span> |

<!--
講者備註：
請看最後一列，這就是我們研究的價值所在。當 ILP 面臨將近 5000 萬個變數時，它在 30 分鐘內跑不出任何結果，直接宣告 TIMEOUT 崩潰。但我們的 OCG 演算法，憑藉 O(N log N) 的優秀架構，在 23 秒內就給出了高品質解答。
-->

---

<!-- 建議圖片：一張折線圖，X 軸是 Variable Count，Y 軸是 Runtime，顯示 ILP 指數上升，而 OCG 貼在地平線上呈現線性 -->
![bg right:45% 90%](../experiments/synthetic/scaling_summary/runtime_by_variable_count.png)

## N6 壓力測試圖表分析

從圖表可以看出兩種演算法本質上的差異：

- **紅線/藍線 (ILP)**：
  隨著問題規模變大，Branch-and-Bound 的搜尋空間呈**指數型 (Exponential) 爆炸**。
- **綠線 (OCG Heuristic)**：
  呈現完美的**線性成長 (Linear)**。無論球探部門丟入多少萬筆農場數據，系統都能在幾十秒內給出決策。

---

## Real-Data Validation (真實數據驗證)

為確保即將到來的賽季可用，我們在 **2026 年 Yahoo 與 FanGraphs** 投影數據上進行了驗證（測試 252 種選秀情境）。

| 數據來源 (2026) | 演算法 | 平均獲得分數 | 損失分數 (Gap) |
| :--- | :--- | :--- | :--- |
| **Yahoo** | ILP (神之視角) | 7917.2 | 0 |
| | **OCG (我們的)** | 7767.7 | <span class="blue-text">**-149.4**</span> |
| | Direct Greedy | 7662.8 | -254.3 |
| **FanGraphs** | ILP (神之視角) | 14642.9 | 0 |
| | **OCG (我們的)** | 14320.1 | <span class="blue-text">**-322.7**</span> |
| | Direct Greedy | 14097.3 | -545.5 |

*OCG 在真實世界中，同樣成功為球隊挽回了可觀的預期分數。*

---

## 8. Conclusions & Business Recommendations

**給球隊總管 (GM) 的最終建議：**

1. **傳統的「選最好球員」策略已經過時**：
   在極端天賦分佈與缺乏工具人的選秀年中，不考慮機會成本的貪婪選秀 (Direct Greedy) 會讓球隊流失極大的預期戰力。
2. **完美最佳化 (ILP) 不具備實戰操作性**：
   選秀是有時間限制的。當考量全聯盟農場與潛力新秀時，指數爆炸的 ILP 無法作為 Real-time 的輔助工具。
3. **導入 Opportunity Cost Greedy (OCG) 系統**：
   OCG 成功捕捉了 ILP 的策略精髓（預判未來），將最佳化落差控制在極小範圍，且擁有應付千萬級變數的即時運算能力。

<!--
講者備註：
總結來說，我們不該再憑感覺選秀，也不能依賴跑不動的絕對數學模型。OCG 就是介於兩者之間的完美橋樑：它具備數學的嚴謹度，又擁有極快的運算速度，是真正能搬進選秀室 (Draft Room) 的戰略武器。
-->

---

## Limitations & Future Extensions

我們未來的系統升級方向：

- **對手行為的機率模型 (Probabilistic Opponent Modeling)**：
  - 目前 ADP 只是一個確定性指標 (Deterministic)。未來可加入對手偏好（如：傾向選本土球員）的機率分佈。
- **結合蒙地卡羅模擬 (Monte Carlo Simulations)**：
  - 球員的預測分數帶有變異數（如受傷風險、低潮風險）。未來目標是將 OCG 升級為能處理變異數風險的 AI 決策系統。

---

# Thank You for Listening!
## Q&A Session

**OR114-2 Final Project, Group 4**
B13705051 周孟承 | B13902103 鄭宇宏 
B13303153 詹舒宇 | B11705039 李盈盈

---