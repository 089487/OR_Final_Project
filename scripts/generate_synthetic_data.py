from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.synthetic_data import SyntheticConfig, generate_synthetic_players, metadata_row, write_synthetic_players


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate synthetic fantasy draft player data.")
    parser.add_argument("--out", required=True, help="Output player CSV path.")
    parser.add_argument("--metadata-out", default=None, help="Optional metadata CSV path.")
    parser.add_argument("--points-scenario", default="normal", choices=["normal", "uniform", "high_low"])
    parser.add_argument(
        "--position-scenario",
        default="roster_ratio",
        choices=["uniform_by_type", "point_flexible", "single_position", "roster_ratio"],
    )
    parser.add_argument("--roster-scale", type=int, default=1)
    parser.add_argument("--num-teams", type=int, default=12)
    parser.add_argument("--player-demand-ratio", type=int, default=3)
    parser.add_argument("--sigma-adp", type=float, default=30.0)
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--season", type=int, default=9999)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    config = SyntheticConfig(
        points_scenario=args.points_scenario,
        position_scenario=args.position_scenario,
        roster_scale=args.roster_scale,
        num_teams=args.num_teams,
        player_demand_ratio=args.player_demand_ratio,
        sigma_adp=args.sigma_adp,
        seed=args.seed,
        season=args.season,
    )
    players = generate_synthetic_players(config)
    write_synthetic_players(players, args.out)

    if args.metadata_out:
        metadata_path = Path(args.metadata_out)
        metadata_path.parent.mkdir(parents=True, exist_ok=True)
        row = metadata_row(config, players)
        if metadata_path.exists():
            existing = pd.read_csv(metadata_path)
            pd.concat([existing, pd.DataFrame([row])], ignore_index=True).to_csv(metadata_path, index=False)
        else:
            pd.DataFrame([row]).to_csv(metadata_path, index=False)

    print(f"Wrote {len(players)} synthetic players to {Path(args.out).resolve()}")


if __name__ == "__main__":
    os.environ.setdefault("PYTHONHASHSEED", "0")
    main()
