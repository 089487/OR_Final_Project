# Synthetic Experiment Results by Scenario

以下內容依據 `reports/final_report.tex` 的實驗場景列表，並參考 `synthetic_factor_tables.md` 中的 N1-N5 結果，列出 Direct Greedy (DG) 與 Opportunity Cost Greedy (OCG) 的 optimal_gap_ratio。

| Scenario | Description | DG optimal_gap_ratio | OCG optimal_gap_ratio |
|---|---|---:|---:|
| S1 | Baseline (Normal / Roster-Ratio / 1:1 / $(0,30)$) | 4.79% ± 1.18% | 1.92% ± 0.57% |
| S2 | Load (Ultra-Low, 10:1) | 3.29% ± 0.85% | 1.16% ± 0.51% |
| S3 | Load (Low, 3:1) | 4.79% ± 1.18% | 1.92% ± 0.57% |
| S4 | Load (High, 1:1) | 8.81% ± 2.19% | 2.64% ± 1.23% |
| S5 | Value: Uniform | 3.24% ± 0.77% | 1.44% ± 0.59% |
| S6 | Value: Star-Heavy / High-Low | 8.39% ± 2.40% | 2.87% ± 1.32% |
| S7 | Pos: Random / Uniform-by-Type | 4.89% ± 0.62% | 1.07% ± 0.43% |
| S8 | Pos: Versatile / Value-Correlation | 5.36% ± 1.66% | 1.34% ± 0.68% |
| S9 | Pos: Rigid / Single-Position | 5.11% ± 1.48% | 0.94% ± 0.65% |
| S10 | Market: Rigid / $(0,0)$ | 1.47% ± 0.48% | 0.48% ± 0.23% |
| S11 | Market: Mild Noise / $(0,60)$ | 5.56% ± 1.58% | 2.43% ± 1.55% |
| S12 | Market: Chaotic / $(-5,30)$ | 4.90% ± 1.24% | 1.83% ± 0.82% |
| S13 | Market: Chaotic / $(+5,30)$ | 5.54% ± 1.57% | 1.64% ± 0.75% |
| S14 | Market: Chaotic / $(-10,30)$ | 4.65% ± 1.32% | 1.90% ± 0.77% |
| S15 | Market: Chaotic / $(+10,30)$ | 5.42% ± 1.21% | 1.72% ± 0.95% |

> 備註：
> - S1-S9 對應 N1/N2/N3/N4 的基礎、價值、位置與負載實驗。
> - S10-S15 對應 N5 的 ADP 噪音與可用性容忍度掃描。


(