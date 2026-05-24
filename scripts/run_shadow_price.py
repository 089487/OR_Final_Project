from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

os.environ.setdefault("MPLCONFIGDIR", str(Path("experiments") / ".matplotlib"))

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.draft_model import ROSTER_REQUIREMENTS, load_players, snake_picks, solve_ilp


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run LP-relaxation shadow price analysis.")
    parser.add_argument("--players", default="data/processed/2026_yahoo_data.csv")
    parser.add_argument("--outdir", default="experiments/shadow_prices/yahoo_2026")
    parser.add_argument("--scoring", default="yahoo")
    parser.add_argument("--num-teams", type=int, default=12)
    parser.add_argument("--draft-position", type=int, default=6)
    parser.add_argument("--delta", type=float, default=0.0)
    parser.add_argument("--time-limit", type=int, default=60)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)

    players = load_players(args.players)
    seasons = sorted(players["season"].unique())
    rounds = sum(ROSTER_REQUIREMENTS.values())
    rows = []

    for season in seasons:
        season_players = players.loc[players["season"] == season].reset_index(drop=True)
        picks = snake_picks(args.num_teams, args.draft_position, rounds)
        solution = solve_ilp(
            season_players,
            picks,
            season=season,
            draft_position=args.draft_position,
            delta=args.delta,
            enforce_adp=True,
            relax=True,
            method_name="ADP-aware LP relaxation",
            time_limit=args.time_limit,
        )
        if solution.shadow_prices is None:
            continue
        shadow_prices = solution.shadow_prices.copy()
        shadow_prices["season"] = season
        shadow_prices["scoring"] = args.scoring
        shadow_prices["draft_position"] = args.draft_position
        shadow_prices["delta"] = args.delta
        rows.append(shadow_prices)

    shadows = pd.concat(rows, ignore_index=True) if rows else pd.DataFrame()
    shadows.to_csv(outdir / "shadow_prices.csv", index=False)
    write_summary(shadows, outdir / "shadow_price_summary.md", args)
    make_plot(shadows, outdir / "position_shadow_prices.png")
    print(f"Wrote shadow price outputs to {outdir.resolve()}")


def write_summary(shadows: pd.DataFrame, path: Path, args: argparse.Namespace) -> None:
    lines = [
        "# Shadow Price Summary",
        "",
        f"- Players: `{args.players}`",
        f"- Draft position: `{args.draft_position}`",
        f"- Delta: `{args.delta}`",
        "- Model: ADP-aware LP relaxation",
        "",
        "Shadow prices are Gurobi dual values for roster-position constraints in the LP relaxation.",
        "They should be interpreted as local marginal values, not integer roster values.",
        "",
    ]
    if not shadows.empty:
        lines.extend(
            [
                "| position | shadow_price |",
                "| --- | ---: |",
            ]
        )
        for row in shadows.sort_values("shadow_price", ascending=False).itertuples(index=False):
            lines.append(f"| {row.position} | {float(row.shadow_price):.4f} |")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def make_plot(shadows: pd.DataFrame, path: Path) -> None:
    if shadows.empty:
        return
    sns.set_theme(style="whitegrid")
    plot_data = shadows.sort_values("shadow_price", ascending=False)
    plt.figure(figsize=(9, 5.2))
    sns.barplot(data=plot_data, x="position", y="shadow_price", color="#4C78A8")
    plt.title("Roster constraint shadow prices")
    plt.xlabel("Position")
    plt.ylabel("Shadow price")
    plt.tight_layout()
    plt.savefig(path, dpi=180)
    plt.close()


if __name__ == "__main__":
    main()
