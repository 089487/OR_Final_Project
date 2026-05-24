# ADP
https://www.fantasypros.com/mlb/adp/overall.php?year=2021

# Scoring table 
we have two scoring method : one is from yahoo fantasy baseball, the other is from fangraphs. The former is used to calculate the fantasy points for each player, while the latter is used to calculate the v_i score for each player based on their performance in various statistical categories.

## Fangraphs scoring method
| 項目類型 | 統計指標 (網頁欄位名稱) | 權重分數 | 項目類型 | 統計指標 (網頁欄位名稱) | 權重分數 |
|---|---:|---:|---|---:|---:|
| ⚾ 打者 | 一壘安打 (1B) | +5.6 | § 投手 | 投球局數 (IP) | +5.0 |
|  | 二壘安打 (2B) | +2.9 |  | 三振 (SO) | +2.0 |
|  | 三壘安打 (3B) | +5.7 |  | 四壞保送 (BB) | -3.0 |
|  | 全壘打 (HR) | +9.4 |  | 被觸身球 (HBP) | -3.0 |
|  | 四壞保送 (BB) | +3.0 |  | 被全壘打 (HR) | -13.0 |
|  | 觸身球 (HBP) | +3.0 |  | 獲得救援成功 (SV) | +5.0 |
|  | 盜壘成功 (SB) | +1.9 |  | 獲得中繼成功 (HLD) | +4.0 |
|  | 盜壘失敗 (CS) | -2.8 |  |  |  |
|  | 三振 (SO) | -1.0 |  |  |  |

## Yahoo Fantasy Baseball scoring method
| 項目類型 | 統計指標 (網頁欄位名稱) | 權重分數 | 項目類型 | 統計指標 (網頁欄位名稱) | 權重分數 |
|---|---:|---:|---|---:|---:|
| ⚾ 打者 | 一壘安打 (1B) | +1.0 | § 投手 | 投球局數 (IP) | +3.0 |
|  | 二壘安打 (2B) | +2.0 |  | 三振 (SO) | +1.0 |
|  | 三壘安打 (3B) | +3.0 |  | 勝投 (W) | +5.0 |
|  | 全壘打 (HR) | +4.0 |  | 敗投 (L) | -5.0 |
|  | 得分 (R) | +1.0 |  | 救援成功 (SV) | +5.0 |
|  | 打點 (RBI) | +1.0 |  | 自責分 (ER) | -2.0 |
|  | 四壞保送 (BB) | +1.0 |  |  |  |
|  | 觸身球 (HBP) | +1.0 |  |  |  |
|  | 盜壘成功 (SB) | +1.0 |  |  |  |
|  | 三振 (SO) | -0.5 |  |  |  |
# pybaseball import data example
```py
import pandas as pd
from pybaseball import batting_stats, pitching_stats

def get_fangraphs_points_v_i(year):
    print(f"--- 正在處理 {year} 賽季數據 ---")
    
    # 1. 獲取打者數據並計算 Points
    # pybaseball 預設抓取所有流動球員，並自帶 ID 欄位 (IDfanGraphs)
    batting_df = batting_stats(year)
    batting_df['1B'] = batting_df['H'] - batting_df['2B'] - batting_df['3B'] - batting_df['HR']
    
    batting_df['v_i'] = (
        batting_df['1B'] * 5.6 + batting_df['2B'] * 2.9 + batting_df['3B'] * 5.7 + batting_df['HR'] * 9.4 +
        batting_df['BB'] * 3.0 + batting_df['HBP'] * 3.0 +
        batting_df['SB'] * 1.9 - batting_df['CS'] * 2.8 - batting_df['SO'] * 1.0
    )
    
    # 2. 獲取投手數據並計算 Points
    pitching_df = pitching_stats(year)
    pitching_df['v_i'] = (
        pitching_df['IP'] * 5.0 + pitching_df['SO'] * 2.0 + 
        pitching_df['SV'] * 5.0 + pitching_df['HLD'] * 4.0 - 
        pitching_df['BB'] * 3.0 - pitching_df['HBP'] * 3.0 - pitching_df['HR'] * 13.0
    )
    
    # 3. 篩選核心欄位以便後續與 FantasyPros 的 ADP 表進行 Merge
    b_res = batting_df[['IDfanGraphs', 'Name', 'v_i']].copy()
    p_res = pitching_df[['IDfanGraphs', 'Name', 'v_i']].copy()
    
    return b_res, p_res

# 範例：獲取 2021 年的預測/實際得分基準
batting_2021, pitching_2021 = get_fangraphs_points_v_i(2021)
print(batting_2021.head())
```