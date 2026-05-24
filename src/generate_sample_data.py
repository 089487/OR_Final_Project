from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd


POSITION_POOL = {
    "C": {"count": 28, "base": 410, "spread": 65, "scarcity": 1.08},
    "1B": {"count": 34, "base": 500, "spread": 80, "scarcity": 0.98},
    "2B": {"count": 34, "base": 470, "spread": 75, "scarcity": 1.02},
    "3B": {"count": 34, "base": 485, "spread": 78, "scarcity": 1.00},
    "SS": {"count": 36, "base": 495, "spread": 82, "scarcity": 1.04},
    "OF": {"count": 80, "base": 475, "spread": 95, "scarcity": 0.96},
    "SP": {"count": 82, "base": 515, "spread": 105, "scarcity": 1.00},
    "RP": {"count": 45, "base": 425, "spread": 70, "scarcity": 1.03},
}

MULTI_POSITION_CHANCES = {
    "1B": ["3B", "OF"],
    "2B": ["SS", "OF"],
    "3B": ["1B", "SS"],
    "SS": ["2B", "3B"],
    "OF": ["1B"],
    "SP": ["RP"],
    "RP": ["SP"],
}


def generate_sample_players(
    output_path: str | Path = "data/raw/sample_players.csv",
    seasons: tuple[int, ...] = (2021, 2022, 2023, 2024),
    seed: int = 1142,
) -> pd.DataFrame:
    """Create a deterministic MLB-like player pool for reproducible experiments."""
    rng = np.random.default_rng(seed)
    rows = []

    for season in seasons:
        season_shift = rng.normal(0, 12)
        player_counter = 1
        for position, spec in POSITION_POOL.items():
            for rank in range(1, int(spec["count"]) + 1):
                talent = max(0, rng.normal(0, 1))
                decay = rank * rng.uniform(2.1, 3.3)
                projected_points = (
                    float(spec["base"])
                    + float(spec["spread"]) * talent
                    - decay
                    + season_shift
                    + rng.normal(0, 20)
                )
                projected_points = max(120, projected_points)

                eligible_positions = [position]
                if position in MULTI_POSITION_CHANCES and rng.random() < 0.20:
                    eligible_positions.append(rng.choice(MULTI_POSITION_CHANCES[position]))

                rows.append(
                    {
                        "season": season,
                        "player": f"{season}_{position}_{player_counter:03d}",
                        "projected_points": round(projected_points, 2),
                        "primary_position": position,
                        "eligible_positions": ";".join(dict.fromkeys(eligible_positions)),
                    }
                )
                player_counter += 1

    players = pd.DataFrame(rows)
    players["adp_score"] = (
        players["projected_points"]
        * players["primary_position"].map(lambda pos: POSITION_POOL[pos]["scarcity"])
        + rng.normal(0, 26, size=len(players))
    )
    players["adp"] = (
        players.groupby("season")["adp_score"]
        .rank(method="first", ascending=False)
        .astype(float)
    )
    players["adp"] = (players["adp"] + rng.normal(0, 7, size=len(players))).clip(lower=1).round(1)
    players = players.drop(columns=["adp_score"]).sort_values(["season", "adp"]).reset_index(drop=True)

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    players.to_csv(output_path, index=False)
    return players


if __name__ == "__main__":
    generated = generate_sample_players()
    print(f"Wrote {len(generated)} players to data/raw/sample_players.csv")
