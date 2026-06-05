# Synthetic Experiment Results by Scenario

以下內容依據 `reports/final_report.tex` 的實驗場景列表，並參考 `synthetic_factor_tables.md` 中的 N1-N5 結果，列出 Direct Greedy (DG) 與 Opportunity Cost Greedy (OCG) 的 optimal_gap_ratio。Improve 使用原始 objective 逐 seed 計算 $(objective_{OCG}-objective_{DG})/objective_{DG}\times100\%$ 後彙整為 $\mu \pm \sigma$。

| Scenario | Description | DG optimal_gap_ratio | OCG optimal_gap_ratio | Improve $\mu \pm \sigma$ |
|---|---|---:|---:|---:|
| S1 | Baseline (Normal / Roster-Ratio / 3:1 / $(0,30)$) | 4.79% ± 1.18% | 1.92% ± 0.57% | 3.02% ± 1.34% |
| S2 | Value: Uniform | 3.24% ± 0.77% | 1.44% ± 0.59% | 1.87% ± 0.65% |
| S3 | Value: Star-Heavy / High-Low | 8.39% ± 2.40% | 2.87% ± 1.32% | 6.10% ± 3.46% |
| S4 | Pos: Random / Uniform-by-Type | 4.89% ± 0.62% | 1.07% ± 0.43% | 4.02% ± 0.82% |
| S5 | Pos: Versatile / Value-Correlation | 5.36% ± 1.66% | 1.34% ± 0.68% | 4.27% ± 1.83% |
| S6 | Pos: Rigid / Single-Position | 5.11% ± 1.48% | 0.94% ± 0.65% | 4.42% ± 1.95% |
| S7 | Market: Rigid / $(0,0)$ | 1.47% ± 0.48% | 0.48% ± 0.23% | 1.00% ± 0.50% |
| S8 | Market: Mild Noise / $(0,60)$ | 5.56% ± 1.58% | 2.43% ± 1.55% | 3.33% ± 1.43% |
| S9 | Market: Chaotic / $(-5,30)$ | 4.90% ± 1.24% | 1.83% ± 0.82% | 3.24% ± 1.40% |
| S10 | Market: Chaotic / $(+5,30)$ | 5.54% ± 1.57% | 1.64% ± 0.75% | 4.16% ± 1.50% |
| S11 | Market: Chaotic / $(-10,30)$ | 4.65% ± 1.32% | 1.90% ± 0.77% | 2.91% ± 1.71% |
| S12 | Market: Chaotic / $(+10,30)$ | 5.42% ± 1.21% | 1.72% ± 0.95% | 3.92% ± 1.03% |
| S13 | Load (High, 1:1) | 8.81% ± 2.19% | 2.64% ± 1.23% | 6.82% ± 3.13% |
| S14 | Load (Ultra-Low, 10:1) | 3.29% ± 0.85% | 1.16% ± 0.51% | 2.20% ± 0.83% |

> 備註：
> - S1 是 baseline；S2-S3 對應 Factor A / value distribution。
> - S4-S6 對應 Factor B / position eligibility。
> - S7-S12 對應 Factor C / ADP noise and availability tolerance。
> - S13-S14 對應 Factor D / player demand ratio；D=3 baseline-supply reference 已由 S1 表示，不另列重複 scenario。
