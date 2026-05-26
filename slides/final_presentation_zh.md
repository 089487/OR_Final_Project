---
marp: true
theme: default
paginate: true
size: 16:9
math: mathjax
---

# 可擴展的夢幻棒球選秀最佳化

## ADP-aware ILP 精確 Benchmark 與 Opportunity-Cost Greedy Heuristic

#### Group 4

B13705051 周孟承  
B13902103 鄭宇宏  
B13303153 詹舒宇  
B11705039 李盈盈

---

## 研究動機

- 夢幻棒球選秀是一個具有不確定性的序列決策問題。
- 管理者需要同時考慮球員價值、守位資格與選秀可得性。
- ADP 會改變問題本身：高價值球員不一定能等到下一輪再選。
- 本專題比較精確最佳化模型與可擴展 greedy heuristics。

---

## 方法定位

| Method | Role | Main Idea |
| --- | --- | --- |
| ADP-aware ILP | Exact benchmark | 同時最佳化 roster、pick、eligibility、ADP constraints |
| Direct Greedy | Simple benchmark heuristic | 優先補最稀缺的位置 |
| Opportunity Cost Greedy | Proposed scalable heuristic | 優先選「等待會損失最多」的位置與球員 |

---

## ADP-aware ILP

決策變數：

- $y_i$：球員 $i$ 是否被選到。
- $x_{ip}$：球員 $i$ 是否被分配到位置 $p$。
- $z_{ik}$：球員 $i$ 是否在我方第 $k$ 個 pick 被選到。

目標式：

$$
\max \sum_i V_i y_i
$$

主要 availability rule：

$$
z_{ik}=0 \quad \text{if } A_i+\delta<S_k
$$

---

## Direct Greedy

Direct Greedy 是 simple benchmark heuristic。

對每個尚未補滿的位置：

$$
\text{scarcity ratio}
=
\frac{\text{remaining slots}}{\text{available eligible players}}
$$

接著選：

- scarcity ratio 最大的位置；
- 該位置目前 projected points 最高的可選球員。

---

## Opportunity Cost Greedy

Opportunity Cost Greedy 是本專題提出的 scalable heuristic。

對每個尚未補滿的位置：

$$
\text{opportunity cost}
=
\text{best current points}
-
\text{best next-pick points}
$$

當位置供給變緊時，啟動 feasibility fallback：

$$
\text{current count} \le \text{remaining slots}
\quad \text{or} \quad
\text{future count} < \text{remaining slots}
$$

---

## 實作方式

兩個 heuristics 都使用：

- 每個 roster position 一個 max-heap；
- lazy deletion 移除已選或已過期球員；
- 依照 `ADP + delta` 排序的 expiration order；
- 每個位置目前可用球員數的 active counts。

近似 heuristic complexity：

$$
O(ne \log n + rp \log n)
$$

---

## 實驗設計

Real-data validation：

- 2026 Yahoo player pool。
- 2026 FanGraphs player pool。

Synthetic experiments：

- N1 baseline。
- N2 points distribution。
- N3 position distribution。
- N4 scaling。
- N5 ADP uncertainty。
- N6 large-scale stress test。

---

## Heuristic 解品質

Opportunity Cost Greedy 更接近 exact benchmark。

| Experiment | Opportunity Cost Greedy gap | Direct Greedy gap |
| --- | ---: | ---: |
| N1 baseline | 1.919% | 4.785% |
| N2 high-low points | 2.867% | 8.390% |
| N4 scaling | 1.623% | 4.177% |
| N5 ADP uncertainty | 1.557% | 4.063% |

---

## Scaling Results

| Instance | Approx. variables | ADP-aware ILP | Opportunity Cost Greedy | Direct Greedy |
| --- | ---: | ---: | ---: | ---: |
| stress_large | 2,289,600 | 41.131s | 1.008s | 0.926s |
| stress_xlarge | 10,880,000 | 299.430s | 2.965s | 2.705s |
| timeout_target | 49,029,120 | interrupted | 9.381s | 8.744s |

Exact optimization 可以作為 benchmark，但 heuristic scalability 明顯更好。

---

## Real-Data Validation

| Dataset | Method | Mean objective | Mean gap |
| --- | --- | ---: | ---: |
| Yahoo 2026 | ADP-aware ILP | 7917.209 | 0.000 |
| Yahoo 2026 | Opportunity Cost Greedy | 7767.732 | 149.477 |
| Yahoo 2026 | Direct Greedy | 7662.866 | 254.343 |
| FanGraphs 2026 | ADP-aware ILP | 14642.927 | 0.000 |
| FanGraphs 2026 | Opportunity Cost Greedy | 14320.135 | 322.792 |
| FanGraphs 2026 | Direct Greedy | 14097.337 | 545.590 |

---

## 結論

- ADP-aware ILP 是 manageable instances 上的 exact benchmark。
- Direct Greedy 是 simple benchmark heuristic。
- Opportunity Cost Greedy 是 proposed scalable heuristic。
- Opportunity Cost Greedy 穩定降低 optimality gap。
- 大型 synthetic experiments 顯示 scalable heuristics 的必要性。

