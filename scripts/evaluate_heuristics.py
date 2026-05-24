from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

os.environ.setdefault("MPLCONFIGDIR", str(Path("heuristic_results") / ".matplotlib"))

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

from run_experiments import make_delta_values
from src.draft_model import (
    ROSTER_REQUIREMENTS,
    load_players,
    snake_picks,
    solve_greedy,
    solve_ilp,
    solve_opportunity_cost_greedy,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Evaluate greedy heuristics against optimal ILP.")
    parser.add_argument("--players", default="data/processed/2026_yahoo_data.csv", help="Processed player CSV.")
    parser.add_argument("--outdir", default="heuristic_results", help="Output directory.")
    parser.add_argument("--num-teams", type=int, default=12)
    parser.add_argument("--delta-grid", default=None, help="Comma-separated delta values.")
    parser.add_argument("--delta-min", type=float, default=-10.0)
    parser.add_argument("--delta-max", type=float, default=10.0)
    parser.add_argument("--delta-step", type=float, default=1.0)
    parser.add_argument("--time-limit", type=int, default=60)
    parser.add_argument("--verbose", action="store_true", help="Write selected rosters for all methods.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)

    players = load_players(args.players)
    seasons = sorted(players["season"].unique())
    rounds = sum(ROSTER_REQUIREMENTS.values())
    deltas = make_delta_values(args.delta_grid, args.delta_min, args.delta_max, args.delta_step)

    result_rows: list[dict[str, object]] = []
    roster_frames: list[pd.DataFrame] = []

    for season in seasons:
        season_players = players.loc[players["season"] == season].reset_index(drop=True)
        for draft_position in range(1, args.num_teams + 1):
            picks = snake_picks(args.num_teams, draft_position, rounds)
            for delta in deltas:
                optimal = solve_ilp(
                    season_players,
                    picks,
                    season=season,
                    draft_position=draft_position,
                    delta=delta,
                    enforce_adp=True,
                    method_name="ADP-aware ILP",
                    time_limit=args.time_limit,
                )
                heuristics = [
                    solve_greedy(
                        season_players,
                        picks,
                        season=season,
                        draft_position=draft_position,
                        delta=delta,
                        enforce_adp=True,
                    ),
                    solve_opportunity_cost_greedy(
                        season_players,
                        picks,
                        season=season,
                        draft_position=draft_position,
                        delta=delta,
                        enforce_adp=True,
                    ),
                ]

                result_rows.append(make_result_row(optimal, optimal, "Optimal"))
                if args.verbose and not optimal.roster.empty:
                    roster_frames.append(optimal.roster.assign(delta=delta))

                for heuristic in heuristics:
                    result_rows.append(make_result_row(heuristic, optimal, heuristic.method))
                    if args.verbose and not heuristic.roster.empty:
                        roster_frames.append(heuristic.roster.assign(delta=delta))

    results = pd.DataFrame(result_rows)
    results.to_csv(outdir / "heuristic_optimal_gap.csv", index=False)
    summary = summarize_results(results)
    summary.to_csv(outdir / "heuristic_gap_summary.csv", index=False)
    if args.verbose and roster_frames:
        pd.concat(roster_frames, ignore_index=True).to_csv(outdir / "heuristic_rosters.csv", index=False)

    make_plots(results, outdir)
    print(f"Wrote heuristic evaluation outputs to {outdir.resolve()}")
    print(summary.to_string(index=False))


def make_result_row(solution, optimal, method: str) -> dict[str, object]:
    optimal_objective = float(optimal.objective)
    objective = float(solution.objective)
    gap = optimal_objective - objective
    return {
        "season": solution.season,
        "draft_position": solution.draft_position,
        "delta": solution.delta,
        "method": method,
        "objective": objective,
        "optimal_objective": optimal_objective,
        "optimal_gap": gap,
        "optimal_gap_pct": gap / optimal_objective if optimal_objective else float("nan"),
        "status": solution.status,
        "optimal_status": optimal.status,
    }


def summarize_results(results: pd.DataFrame) -> pd.DataFrame:
    heuristics = results.loc[results["method"] != "Optimal"].copy()
    return (
        heuristics.groupby("method", as_index=False)
        .agg(
            mean_gap=("optimal_gap", "mean"),
            median_gap=("optimal_gap", "median"),
            max_gap=("optimal_gap", "max"),
            mean_gap_pct=("optimal_gap_pct", "mean"),
            optimal_matches=("optimal_gap", lambda values: int((values.abs() < 1e-6).sum())),
            cases=("optimal_gap", "size"),
        )
        .sort_values("mean_gap")
    )


def make_plots(results: pd.DataFrame, outdir: Path) -> None:
    heuristics = results.loc[results["method"] != "Optimal"].copy()
    if heuristics.empty:
        return

    sns.set_theme(style="whitegrid")
    plt.figure(figsize=(9, 5.2))
    sns.barplot(data=heuristics, x="method", y="optimal_gap", errorbar="sd")
    plt.title("Average optimal gap by heuristic")
    plt.xlabel("Method")
    plt.ylabel("Optimal gap")
    plt.tight_layout()
    plt.savefig(outdir / "heuristic_average_gap.png", dpi=180)
    plt.close()

    by_position = heuristics.groupby(["draft_position", "method"], as_index=False)["optimal_gap"].mean()
    plt.figure(figsize=(10, 5.6))
    sns.lineplot(data=by_position, x="draft_position", y="optimal_gap", hue="method", marker="o")
    plt.title("Mean optimal gap by draft position")
    plt.xlabel("Draft position")
    plt.ylabel("Optimal gap")
    plt.tight_layout()
    plt.savefig(outdir / "heuristic_gap_by_draft_position.png", dpi=180)
    plt.close()

    by_delta = heuristics.groupby(["delta", "method"], as_index=False)["optimal_gap"].mean()
    plt.figure(figsize=(10, 5.6))
    sns.lineplot(data=by_delta, x="delta", y="optimal_gap", hue="method", marker="o")
    plt.title("Mean optimal gap by ADP delta")
    plt.xlabel("Delta")
    plt.ylabel("Optimal gap")
    plt.tight_layout()
    plt.savefig(outdir / "heuristic_gap_by_delta.png", dpi=180)
    plt.close()

    for method, method_data in heuristics.groupby("method"):
        heatmap = method_data.pivot_table(
            index="draft_position",
            columns="delta",
            values="optimal_gap",
            aggfunc="mean",
        )
        plt.figure(figsize=(12, 5.8))
        sns.heatmap(heatmap, cmap="mako_r", cbar_kws={"label": "Optimal gap"})
        plt.title(f"Optimal gap heatmap: {method}")
        plt.xlabel("Delta")
        plt.ylabel("Draft position")
        plt.tight_layout()
        filename = method.lower().replace(" ", "_").replace("-", "_")
        plt.savefig(outdir / f"{filename}_gap_heatmap.png", dpi=180)
        plt.close()


if __name__ == "__main__":
    main()
