---
marp: true
theme: default
paginate: true
size: 16:9
math: mathjax
style: |
  /* 導入高質感現代字體 */
  @import url('https://fonts.googleapis.com/css2?family=Montserrat:ital,wght@0,400;0,600;0,800;1,400&family=Noto+Sans+TC:wght@400;500;700;900&display=swap');

  section {
    font-family: 'Montserrat', 'Noto Sans TC', sans-serif;
    background-color: #f8fafc;
    color: #334155;
    font-size: 24px;
    line-height: 1.6;
    background-image: radial-gradient(circle at 100% 0%, rgba(219, 234, 254, 0.6) 0%, transparent 40%);
  }

  /* 標題設計 */
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

  /* 封面與重點轉場頁 (Dark Mode) */
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

  /* 強調字色 */
  .highlight { color: #ea580c; font-weight: bold; }
  .blue-text { color: #2563eb; font-weight: bold; }
  .green-text { color: #16a34a; font-weight: bold; }

  /* 專業引言區塊 */
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

  /* 高質感資料表 (修復表頭消失問題) */
  table {
    width: 100%;
    border-collapse: collapse;
    font-size: 20px;
    background: white;
    margin-top: 10px;
    display: table; /* 修復 Marp 表頭消失問題 */
    box-shadow: 0 10px 15px -3px rgba(0,0,0,0.1);
  }
  th { 
    background-color: #0f172a !important; /* 強制覆蓋 Marp 預設灰底 */
    color: #ffffff !important;           /* 強制覆蓋文字為白色 */
    font-weight: 600; 
    padding: 14px 16px; 
    text-align: center; 
    border: 1px solid #0f172a !important;
  }
  td { 
    padding: 12px 16px; 
    text-align: center; 
    border-bottom: 1px solid #e2e8f0; 
    border-left: none;
    border-right: none;
  }
  tbody tr:nth-child(even) td { background-color: #f8fafc !important; }
  tbody tr:hover td { background-color: #eff6ff !important; }

  /* UI 佈局工具 */
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
---

<!-- _class: title-slide -->

# Strategic Fantasy Baseball Draft Optimization
## 棒球制服組的決策支援系統：可擴展的選秀最佳化策略

<div class="author-block">
  <strong>OR114-2 Final Project, Group 4</strong><br>
  B13705051 周孟承 | B13902103 鄭宇宏 | B13303153 詹舒宇 | B11705039 李盈盈<br>
  Spring 2026
</div>

---

## 報告大綱 (Outline)

1. **Introduction**：棒球選秀介紹與現代制服組洞察
2. **Problem Description**：蛇形選秀環境與大谷條款
3. **Real Data Collection**：基於 FantasyPros 的真實數據爬取
4. **Model Formulation**：整數線性規劃 (ILP) 建模
5. **The Bottleneck**：為何傳統 ILP 遇到效能瓶頸？
6. **Algorithms**：機會成本貪婪演算法 (OCG)
7. **Synthetic Data & Evaluation**：合成數據生成與壓力測試
8. **Conclusions**：商業建議與未來展望

---

## 1. Introduction: 棒球建軍的基石 —— 季前選秀

**對於一支職業棒球隊來說，最划算且最重要的補強方式就是「透過選秀」。**

- **什麼是選秀 (The Draft)？**
  在球季開始前，各球隊的總管 (GM) 會齊聚一堂，輪流從龐大的「業餘球員 / 自由球員池」中挑選潛力新秀入隊。
- **選秀的本質：零和博弈與資源分配**
  - 你面對的是一個<span class="highlight">「會不斷被對手消耗的公共資源池」</span>。
  - 當你看中一名球員卻沒有立刻選他，下一次輪到你時，他可能已經被對手搶走。
- **決策的核心**：
  在有限的選秀權 (Picks) 內，如何精準填補球隊陣容的各個守備位置，並將整體戰力最大化？

<!-- 
講者備註：
各位教授、助教、同學們大家好。想像我們現在是大聯盟球隊的制服組 (Front Office)。對於球隊來說，要在聯盟中保持長期競爭力，最核心的任務就是「選秀」。選秀就像是一場搶物資的遊戲，池子裡的頂級新秀數量有限，當你猶豫不決時，對手就會把人搶走。
-->

---

## Introduction: 現代制服組的挑戰與洞察

過去的選秀仰賴老球探的「直覺」，但在大數據時代，我們觀察到兩個重要的商業洞察：

<div class="grid-2">
<div class="card">
  <div class="tag">Insight 1</div>
  <h3 style="margin-top:0;">球探數據的收斂</h3>
  各隊對「同一名球員的評價」越來越趨近相同。<br><br>
  👉 被量化出來的戰力預測值，直接對應了我們模型中的 <span class="blue-text">Projected Points (預期分數)</span>。
</div>

<div class="card card-orange">
  <div class="tag">Insight 2</div>
  <h3 style="margin-top:0;">市場預期的博弈</h3>
  專業團隊知道在某個順位之後，就絕對選不到該球員。<br><br>
  👉 這個市場的消耗時機，精準對應了模型中的 <span class="highlight">ADP (平均選秀順位)</span>。
</div>
</div>

> **「當各隊對球員的評價與落點預測都一致時，真正的優勢，在於能否執行一套數學上最佳化的選秀策略！」**

---

## 2. Problem Description I：蛇形選秀 (Snake Draft)

現實中的 MLB 選秀是依據前一年的戰績（由爛到好）進行固定順位選秀。但為了純粹探討**「選秀策略的數學優勢」**，我們將情境抽象化為更公平的<span class="highlight">蛇形選秀</span>。

- **為什麼使用蛇形選秀？**
  消除初始戰績帶來的絕對資源優勢。在蛇形選秀中，每一輪的選秀順序會反轉（第一輪最後選的人，第二輪第一個選），藉此凸顯「策略分配」本身的重要性。
- **數學順位換算公式**：
  假設共有 $M$ 位玩家，我們的初始順位為 $j$ ($1 \le j \le M$)。在第 $r$ 輪時，我們擁有的整體順位 $k$ 為：
  - **奇數輪 (Forward)**：$k = (r - 1)M + j$
  - **偶數輪 (Reverse)**：$k = rM - j + 1$

---

## Problem Description II：球員屬性與特殊簡化

在選秀池中，每位球員擁有以下三大屬性：
1. **Projected Value ($v_i$)**：賽季預期貢獻分數。
2. **Eligible Positions ($E_i$)**：球員合法的守備位置。
3. **Average Draft Position (ADP)**：市場預期平均被選順位。

<div class="card" style="margin-top: 20px;">
  <span class="highlight">⚠️ 特殊簡化：大谷翔平條款 (The Ohtani Rule)</span><br>
  為了避免位置彈性上的邏輯過於複雜，我們在模型中<b>不考慮二刀流</b>。<br>
  在後續的合成與真實數據中，大谷翔平 (Shohei Ohtani) 的「打者 (DH)」與「投手 (SP)」身份會被拆分視為<b>兩名獨立的球員</b>。
</div>

---

## Problem Description III：先發陣容需求

要完成一組有效的陣容，必須嚴格滿足以下的數量限制 (Roster Requirements)。
我們使用標準的 **16 人先發名單** 作為基礎架構：

| 守位 (Position) | C | 1B | 2B | 3B | SS | OF | Util | SP | RP |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **需求人數 (Slots)** | 1 | 1 | 1 | 1 | 1 | 3 | 1 | 5 | 2 |

*註：Util (Utility) 僅限打者，投手無法填補此空缺。這將成為 ILP 限制式的重要基準。*

<!--
講者備註：
名單必須嚴格符合這個表。這就產生了有趣的 Trade-off：外野手 (OF) 跟先發投手 (SP) 需要很多人，但游擊手 (SS) 或捕手 (C) 只有一個，如果 SS 的好球員很少，我們是不是該提早搶？這就是我們模型要解決的分配問題。
-->

---

<!-- _class: impact-slide -->

# 3. Real Data Collection
## 將真實世界的棒球市場數據化

---

## Real Data Collection: 來源與變數對應

- Player projected points $v_i$
  - 從 **FantasyPros** 網站下載 2026 球員預測成績數據
  - 採計了 yahoo, fantasy pros 兩種計分方式
- ADP $\text{adp}_i$
  - 從 **FantasyPros** 網站下載

---

#### Player projected points 取得
- 從 **FantasyPros** 網站下載 2026 球員預測成績數據![alt text](image.png)
- 分別套用 Yahoo, FanGraphs 兩種計分方式如下表：

<div class="grid-2">
<div class="card">
  <div class="tag">Yahoo Scoring</div>
  <ul>
    <li><b>打者</b>：(1B, 2B, 3B, HR, R, RBI, BB, HBP, SB, SO) = (1, 2, 3, 4, 1, 1, 1, 1, 1, -0.5)</li>
    <li><b>投手</b>：(IP, SO, W, L, SV, ER) = (3, 1, 5, -5, 5, -2)</li>
  </ul>
</div>

<div class="card card-orange">
  <div class="tag">FanGraphs Scoring</div>
  <ul>
    <li><b>打者</b>：(1B, 2B, 3B, HR, BB, HBP, SB, CS, SO) = (5.6, 2.9, 5.7, 9.4, 3, 3, 1.9, -2.8, -1)</li>
    <li><b>投手</b>：(IP, SO, BB, HBP, HR, SV, HLD) = (5, 2, -3, -3, -13, 5, 4)</li>
  </ul>
</div>
</div>

---

#### Average Draft Position (ADP) 取得
- 從 **FantasyPros** 網站下載 2026 球員 ADP 數據包括各大平台 (Yahoo, ESPN, CBS) 的平均選秀順位
![alt text](image-1.png)

---


## 4. Model Formulation I：變數與目標函數

有了真實的 $v_i$ 與 $\text{adp}_i$ 後，我們將問題建構為 **ADP-aware Integer Linear Program (ILP)**。
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
   $$ \sum_{i \in I} z_{ik} = 1 \quad \text{(每個順位選一人)} $$
   $$ \sum_{p \in P} x_{ip} = y_i \quad \text{(選入必安排唯一守位)} $$
   $$ \sum_{i \in I} x_{ip} = r_p \quad \text{(滿足各守備位置規定人數)} $$

2. **市場可用性限制 (Market Availability Constraint)**：
   $$ z_{ik} = 0 \quad \text{if } S_k > \text{adp}_i + \delta, \quad \forall i \in I, k \in K $$
   > *如果我們的選秀順位 $S_k$ 已經晚於球員的 $\text{adp}_i + \delta$ (容錯值)，系統將強制無法選取該名球員。*

---

<!-- _class: impact-slide -->

# 5. The Bottleneck
## 為什麼傳統 ILP 不夠用？
當學術模型遇上現實世界的資料量

---

## 傳統 ILP 的實戰致命傷

雖然 ADP-aware ILP 能給出**絕對完美的最佳解 (God's Eye View)**，但在現實中會面臨極大的挑戰。

<div class="grid-2">
<div class="card">
  <div class="tag">Scalability Crisis</div>
  <h3 style="margin-top:0;">指數爆炸的可擴展性</h3>
  棒球選秀的母體池極其龐大，大聯盟加上無數新秀，球員池高達十幾萬人。當球員數 ($n$) 放大，ILP 的 Branch-and-Bound 搜尋空間會呈<span class="highlight">指數爆炸</span>。
</div>

<div class="card card-orange">
  <div class="tag">Real-time execution</div>
  <h3 style="margin-top:0;">實戰的時間壓力</h3>
  選秀是有時間限制的。總管不可能在選秀室等 Gurobi 跑半個小時。在巨大規模下，ILP 會直接<span class="highlight">超時 (Timeout) 或記憶體耗盡</span>。
</div>
</div>

---

## 6. Algorithms：啟發式演算法設計 (Heuristics)

為了解決 ILP 的效能瓶頸，我們設計了兩種啟發式演算法 (Heuristics)。

### ❌ Baseline: Direct Greedy (直接貪婪法)
- **邏輯**：目光短淺 (Myopic)。每次輪到我選時，計算各守位之「稀缺度」並選擇最大者，再選下該位最強球員。
  - **公式指標**：$\max_{p} \left( \frac{\text{該守位待補人數}}{\text{市場剩餘可用球員}} \right)$
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
  2. 找出該守位**現在能選到**的最強球員 ($V_{\text{now}}$)。
  3. 預測到**我們下一輪選秀時**，該守位還剩下的最強球員 ($V_{\text{next}}$)。
  4. 計算**機會成本**： $\text{Score} = V_{\text{now}} - V_{\text{next}}$
  5. 優先選擇機會成本（損失）最大的守位與球員。

> OCG 完美捕捉了 ILP 「瞻前顧後」的戰略精髓！

---

## Algorithms: 時間複雜度分析 (Time Complexity)

要在實戰中即時運算，資料結構的選擇至關重要。

- **實作方式 (Data Structure)**：
  - 為每個守備位置維護一個 **Max-Heap (優先佇列)**。
  - 採用 **Lazy Deletion (延遲刪除)**：當球員被對手選走時不立刻重整 Heap，而是等到 pop 時再檢查有效性。
- **複雜度表現**：
  - 假設 $n$ = 球員總數， $r$ = 名單人數， $p$ = 守備位置數。
  - **總時間複雜度**：$\mathcal{O}(n \log n + r \cdot p)$ (和Direct Greedy 相同)

<div class="card" style="text-align:center; margin-top:20px; color:#1e40af; font-weight:bold;">
  數學保證 OCG 能以接近線性的時間，瞬間處理數十萬人等級的選秀池。
</div>

---

## ：Real-Data Validation

| 數據來源 (2026) | 演算法 | **Optimal Gap Ratio** |
| :--- | :--- | :--- |
| **Yahoo** | **OCG (我們的)** | <span class="blue-text">**0.50%**</span> |
| | Direct Greedy | 3.24% |
| **FanGraphs** | **OCG (我們的)** | <span class="blue-text">**1.24%**</span> |
| | Direct Greedy | 3.36% |


---

<!-- _class: impact-slide -->

# 7. Synthetic Data & Evaluation
## 我們如何證明演算法在極端環境下依然有效？

---

## 為什麼有了真實數據，還需要 Synthetic Data？

真實數據 (如 FantasyPros) 只能證明演算法在「目前的環境」下可行。但為了驗證演算法的**強健度與極限**，我們建構了合成數據生成器，對四大變因進行**壓力測試 (Stress Testing)**：

<div class="grid-2" style="gap:15px; margin-top:15px;">
<div class="card" style="padding:15px;">
  <strong>1. Points Distribution (天賦分佈)</strong><br>
  常態分佈 vs. 巨星集中 (High-Low)
</div>
<div class="card" style="padding:15px;">
  <strong>2. Positions Distribution (守位彈性)</strong><br>
  工具人氾濫 vs. 單一守位死綁
</div>
<div class="card" style="padding:15px;">
  <strong>3. Market Volatility (ADP 雜訊)</strong><br>
  市場效率 ($\sigma$) 與 容錯空間 ($\delta$)
</div>
<div class="card" style="padding:15px;">
  <strong>4. Scale & Demand (規模與供需)</strong><br>
  極度缺人的市場與海量資料池
</div>
</div>

> **實驗指標 (Optimal Gap Ratio)**：$\frac{Z_{\text{ILP}} - Z_{\text{Heuristic}}}{Z_{\text{ILP}}} \times 100\%$ （越低越好）

<!--
講者備註：
雖然我們有了前面抓下來的真實數據，但現實數據只有一種長相。如果要證明我們的 OCG 演算法是無懈可擊的，我們必須創造出各種極端平形宇宙：例如完全沒有工具人的世界、或者巨星價值極度不平均的世界，這就是 Synthetic Data 的價值。
-->

---

## 實驗 N1 ~ N3：天賦分佈與守備彈性

| 情境 (Scenario) | 參數設定 (Level) | Direct Greedy | **Opportunity Cost Greedy** |
| :--- | :--- | :---: | :---: |
| **N1: Baseline** | 基準線 (Normal) | $4.79\%$ | **$1.92\%$** |
| **N2: Points Dist.** | <span class="highlight">巨星集中 (High-Low)</span> | $8.39\%$ | <span class="highlight">**$2.87\%$**</span> |
| **N3: Pos Dist.** | 無工具人 (Single-Pos) | $5.11\%$ | <span class="blue-text">**$0.94\%$**</span> |

- **商業洞察**：
  - 在 **High-Low** (僅 10% 是超級巨星) 的環境下，Direct Greedy 表現崩盤 (8.39%)，因為它會為了填補洞口而錯失巨星。
  - **OCG** 預判到巨星失去後的價值斷層，成功保住菁英，將損失控制在 2.87%。

---

## 實驗 N4：市場供需比例 (Scale & Demand)

當球員池的「可用人數」與「聯盟總需求」比例 ($D$) 改變時：

| 供需比例 (Demand Ratio) | 市場狀態 | Direct Greedy | **Opportunity Cost Greedy** |
| :--- | :--- | :---: | :---: |
| **$D = 1$** | <span class="highlight">極度稀缺 (Scarcity)</span> | $8.81\%$ | **$2.64\%$** |
| **$D = 3$** | 基準線 (Baseline) | $4.79\%$ | **$1.92\%$** |
| **$D = 10$** | 資源氾濫 (Abundance) | $3.29\%$ | <span class="green-text">**$1.16\%$**</span> |

- **商業洞察**：
  - 在**極度稀缺**的市場 ($D=1$)，每一個選秀失誤都會直接換來「零分替補」，Direct Greedy 盲目填補洞口的策略導致崩盤 (8.81%)。
  - OCG 意識到未來的枯竭，提早佈局，成功將落差控制在 2.64%。

---

## 實驗 N5：市場波動 ($\sigma$) 與 容錯空間 ($\delta$)

當對手行為無法預測 (ADP 充滿雜訊) 時，誰能活下來？我們拆分兩種測試：

| 測試維度 | 參數設定 | Direct Greedy | **Opportunity Cost Greedy** |
| :--- | :--- | :---: | :---: |
| **N5-A: 雜訊** <br> (固定 $\delta=0$) | $\sigma=0$ (效率市場) | $1.47\%$ | **$0.48\%$** |
| | <span class="highlight">$\sigma=60$ (高度混亂)</span> | $5.56\%$ | <span class="highlight">**$2.43\%$**</span> |
| **N5-B: 容錯** <br> (固定 $\sigma=30$) | $\delta=-10$ (嚴格限制) | $4.65\%$ | **$1.90\%$** |
| | $\delta=10$ (寬鬆限制) | $5.42\%$ | **$1.72\%$** |

- **結論**：無論面對極度混亂的市場或嚴格的可用性限制，OCG 都能將落差穩穩控制，展現強大抗衝擊能力。

---

## 實驗 N6：Scalability 終極壓力測試

這是向制服組提案的最核心關鍵：**當球員池無限放大時，誰能不當機？**

ILP 近似變數估算公式：$\text{Vars} \approx n \times (1 + p + r)$
*(球員總數 $\times$ (選取變數 + 守位分配變數 + 輪次可用性變數))*

| 測試等級 | 近似變數數量 | ILP 運算時間 (狀態) | **OCG 運算時間** |
| :--- | ---: | :--- | :--- |
| `stress_small` | 334,080 | 4.23 秒 (最佳解) | **0.85 秒** |
| `stress_large` | 2,289,600 | 54.26 秒 (最佳解) | **2.34 秒** |
| `timeout_target` | <span class="highlight">49,029,120</span> | <span class="highlight">**1869.8 秒 (TIMEOUT 崩潰)**</span> | <span class="blue-text">**23.28 秒**</span> |

---

<!-- 建議圖片：將 runtime_by_variable_count.png 放進來 -->
![bg right:45% 90%](../experiments/synthetic/scaling_summary/runtime_by_variable_count.png)

## N6 壓力測試圖表分析

從圖表可以看出兩種演算法本質上的差異：

- **紅線/藍線 (ILP)**：
  隨著問題規模變大，Branch-and-Bound 的搜尋空間呈**指數型 (Exponential) 爆炸**。
- **綠線 (OCG Heuristic)**：
  呈現完美的**線性成長 (Linear)**。無論球探部門丟入多少萬筆農場數據，系統都能在幾十秒內給出決策。

---

## 8. Conclusions & Business Recommendations

**給球隊總管 (GM) 的最終建議：**

1. **傳統的「選最好球員 (BPA)」策略已經過時**：
   在巨星價值高度集中或缺乏工具人的選秀年中，不考慮機會成本的貪婪選秀會讓球隊流失極大的預期戰力。
2. **完美最佳化 (ILP) 不具備實戰操作性**：
   選秀有時間限制。當考量全聯盟農場與潛力新秀時，指數爆炸的 ILP 無法作為 Real-time 的輔助工具。
3. **導入 Opportunity Cost Greedy (OCG) 系統**：
   OCG 成功捕捉了 ILP 的策略精髓（預判未來），將最佳化落差控制在極小範圍，且擁有應付五千萬級變數的即時運算能力。

---

## Limitations & Future Extensions

我們未來的系統升級方向：

- **對手行為的機率模型 (Probabilistic Opponent Modeling)**：
  - 目前 ADP 只是一個確定性指標 (Deterministic)。未來可加入對手偏好（如：傾向選本土球員、特定球隊迷）的機率分佈。
- **結合蒙地卡羅模擬 (Monte Carlo Simulations)**：
  - 球員的預測分數帶有變異數（如受傷風險、低潮風險）。未來目標是將 OCG 升級為能處理變異數風險的 AI 決策系統。

---

<!-- _class: title-slide -->
# Thank You for Listening!
## Q&A Session

<div class="author-block">
  <strong>OR114-2 Final Project, Group 4</strong><br>
  B13705051 周孟承 | B13902103 鄭宇宏 | B13303153 詹舒宇 | B11705039 李盈盈<br>
</div>
