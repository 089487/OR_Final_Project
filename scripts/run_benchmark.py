from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

os.environ.setdefault("MPLCONFIGDIR", str(Path("experiments") / ".matplotlib"))

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

from src.draft_core import ROSTER_REQUIREMENTS, load_players, snake_picks
from src.heuristics import solve_greedy, solve_opportunity_cost_greedy
from src.ip_model import solve_ilp


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run unified draft-method benchmark.")
    parser.add_argument("--players", default="data/processed/2026_yahoo_data.csv", help="Processed player CSV.")
    parser.add_argument("--outdir", default="experiments/benchmark/yahoo_2026", help="Output directory.")
    parser.add_argument("--scoring", default="yahoo", help="Scoring label written to output tables.")
    parser.add_argument("--num-teams", type=int, default=12)
    parser.add_argument("--delta-grid", default=None, help="Comma-separated delta values.")
    parser.add_argument("--delta-min", type=float, default=-10.0)
    parser.add_argument("--delta-max", type=float, default=10.0)
    parser.add_argument("--delta-step", type=float, default=1.0)
    parser.add_argument("--time-limit", type=int, default=0, help="Gurobi time limit in seconds. Use 0 for no limit.")
    parser.add_argument("--verbose", action="store_true", help="Write selected rosters for every method.")
    return parser.parse_args()


def make_delta_values(delta_grid: str | None, delta_min: float, delta_max: float, delta_step: float) -> list[float]:
    if delta_grid:
        return [float(value.strip()) for value in delta_grid.split(",") if value.strip()]
    values = []
    current = delta_min
    while current <= delta_max + 1e-9:
        values.append(round(current, 10))
        current += delta_step
    return values


def main() -> None:
    args = parse_args()
    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    summary_dir = outdir / "summary"
    summary_dir.mkdir(parents=True, exist_ok=True)

    players = load_players(args.players)
    seasons = sorted(players["season"].unique())
    rounds = sum(ROSTER_REQUIREMENTS.values())
    deltas = make_delta_values(args.delta_grid, args.delta_min, args.delta_max, args.delta_step)

    result_rows: list[dict[str, object]] = []
    roster_frames: list[pd.DataFrame] = []
    total_cases = len(seasons) * args.num_teams * len(deltas)
    completed_cases = 0

    for season in seasons:
        season_players = players.loc[players["season"] == season].reset_index(drop=True)
        print(f"Solving Static IP for season={season}", flush=True)
        static_solution = solve_ilp(
            season_players,
            snake_picks(args.num_teams, 1, rounds),
            season=season,
            draft_position=1,
            delta=0.0,
            enforce_adp=False,
            method_name="Static IP",
            time_limit=args.time_limit,
        )

        for draft_position in range(1, args.num_teams + 1):
            picks = snake_picks(args.num_teams, draft_position, rounds)
            for delta in deltas:
                completed_cases += 1
                print(
                    f"[{completed_cases}/{total_cases}] "
                    f"season={season} draft_position={draft_position} delta={delta}",
                    flush=True,
                )
                adp_aware = solve_ilp(
                    season_players,
                    picks,
                    season=season,
                    draft_position=draft_position,
                    delta=delta,
                    enforce_adp=True,
                    method_name="ADP-aware ILP",
                    time_limit=args.time_limit,
                )
                solutions = [
                    adp_aware,
                    static_solution,
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

                for solution in solutions:
                    result_rows.append(
                        make_result_row(
                            solution=solution,
                            adp_aware=adp_aware,
                            scoring=args.scoring,
                            season=season,
                            draft_position=draft_position,
                            delta=delta,
                        )
                    )
                    if args.verbose and not solution.roster.empty:
                        roster_frames.append(
                            solution.roster.assign(
                                scoring=args.scoring,
                                benchmark_draft_position=draft_position,
                                benchmark_delta=delta,
                        )
                    )

                pd.DataFrame(result_rows).to_csv(summary_dir / "benchmark_results.csv", index=False)

    results = pd.DataFrame(result_rows)
    representative_rosters = build_representative_rosters(
        players=players,
        seasons=seasons,
        num_teams=args.num_teams,
        scoring=args.scoring,
        time_limit=args.time_limit,
    )
    write_benchmark_outputs(results, representative_rosters, outdir)
    if args.verbose and roster_frames:
        pd.concat(roster_frames, ignore_index=True).to_csv(outdir / "summary" / "benchmark_rosters.csv", index=False)

    make_plots(results, outdir / "summary")
    print(f"Wrote benchmark outputs to {outdir.resolve()}")
    print(summarize_by_method(results).to_string(index=False))


def make_result_row(
    *,
    solution,
    adp_aware,
    scoring: str,
    season: int,
    draft_position: int,
    delta: float,
) -> dict[str, object]:
    objective = float(solution.objective)
    adp_objective = float(adp_aware.objective)
    gap = adp_objective - objective
    static_adp_cost = objective - adp_objective if solution.method == "Static IP" else float("nan")
    is_gap_method = solution.method in {"Direct Greedy", "Opportunity Cost Greedy"}
    return {
        "season": season,
        "scoring": scoring,
        "draft_position": draft_position,
        "delta": delta,
        "method": solution.method,
        "objective": objective,
        "runtime_seconds": solution.runtime_seconds,
        "mip_gap": solution.mip_gap,
        "best_bound": solution.best_bound,
        "adp_aware_objective": adp_objective,
        "optimal_gap": gap if is_gap_method else 0.0 if solution.method == "ADP-aware ILP" else float("nan"),
        "optimal_gap_pct": gap / adp_objective if is_gap_method and adp_objective else 0.0 if solution.method == "ADP-aware ILP" else float("nan"),
        "adp_cost": static_adp_cost,
        "status": solution.status,
        "adp_aware_status": adp_aware.status,
    }


def build_representative_rosters(
    *,
    players: pd.DataFrame,
    seasons: list[int],
    num_teams: int,
    scoring: str,
    time_limit: int,
) -> dict[str, pd.DataFrame]:
    draft_position = 6
    delta = 0.0
    rounds = sum(ROSTER_REQUIREMENTS.values())
    picks = snake_picks(num_teams, draft_position, rounds)
    rosters: dict[str, list[pd.DataFrame]] = {
        "Static IP": [],
        "ADP-aware ILP": [],
        "Direct Greedy": [],
        "Opportunity Cost Greedy": [],
    }

    for season in seasons:
        season_players = players.loc[players["season"] == season].reset_index(drop=True)
        solutions = [
            solve_ilp(
                season_players,
                picks,
                season=season,
                draft_position=draft_position,
                delta=delta,
                enforce_adp=False,
                method_name="Static IP",
                time_limit=time_limit,
            ),
            solve_ilp(
                season_players,
                picks,
                season=season,
                draft_position=draft_position,
                delta=delta,
                enforce_adp=True,
                method_name="ADP-aware ILP",
                time_limit=time_limit,
            ),
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

        for solution in solutions:
            if solution.roster.empty:
                continue
            roster = solution.roster.copy()
            roster.insert(1, "scoring", scoring)
            roster["representative_draft_position"] = draft_position
            roster["representative_delta"] = delta
            roster["objective"] = float(solution.objective)
            rosters[solution.method].append(roster)

    return {
        method: pd.concat(frames, ignore_index=True) if frames else pd.DataFrame()
        for method, frames in rosters.items()
    }


def write_benchmark_outputs(
    results: pd.DataFrame,
    representative_rosters: dict[str, pd.DataFrame],
    outdir: Path,
) -> None:
    method_dirs = {
        "Static IP": "static_IP",
        "ADP-aware ILP": "adp_aware_ILP",
        "Direct Greedy": "heuristic_greedy",
        "Opportunity Cost Greedy": "heuristic_opportunity_cost",
    }
    summary_dir = outdir / "summary"
    summary_dir.mkdir(parents=True, exist_ok=True)

    results.to_csv(summary_dir / "benchmark_results.csv", index=False)
    summarize_by_method(results).to_csv(summary_dir / "summary_by_method.csv", index=False)
    summarize_by_position(results).to_csv(summary_dir / "summary_by_position.csv", index=False)
    summarize_by_delta(results).to_csv(summary_dir / "summary_by_delta.csv", index=False)

    for method, dirname in method_dirs.items():
        method_dir = outdir / dirname
        method_dir.mkdir(parents=True, exist_ok=True)
        method_results = results.loc[results["method"] == method].copy()
        method_results.to_csv(method_dir / "results.csv", index=False)
        summarize_single_method(method_results).to_csv(method_dir / "summary.csv", index=False)

        representative = representative_rosters.get(method, pd.DataFrame())
        if not representative.empty:
            representative.to_csv(method_dir / "draft_result_position6_delta0.csv", index=False)

    representative_frames = [frame for frame in representative_rosters.values() if not frame.empty]
    if representative_frames:
        combined = pd.concat(representative_frames, ignore_index=True)
        combined.to_csv(
            summary_dir / "draft_result_position6_delta0_all_methods.csv",
            index=False,
        )
        write_representative_markdown(
            combined,
            summary_dir / "position6_delta0_roster_comparison.md",
        )


def summarize_single_method(results: pd.DataFrame) -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "method": results["method"].iloc[0] if not results.empty else "",
                "mean_objective": results["objective"].mean(),
                "median_objective": results["objective"].median(),
                "mean_optimal_gap": results["optimal_gap"].mean(),
                "mean_optimal_gap_pct": results["optimal_gap_pct"].mean(),
                "mean_runtime_seconds": results["runtime_seconds"].mean(),
                "mean_mip_gap": results["mip_gap"].mean(),
                "mean_adp_cost": results["adp_cost"].mean(),
                "cases": len(results),
            }
        ]
    )


def write_representative_markdown(results: pd.DataFrame, path: Path) -> None:
    lines = [
        "# Representative Case: Draft Position 6, Delta 0",
        "",
        "| method | objective | players |",
        "| --- | ---: | --- |",
    ]
    for method, group in results.sort_values(["method", "round"]).groupby("method"):
        objective = float(group["objective"].iloc[0])
        players = ", ".join(
            f"{row.player} ({row.assigned_position}, {float(row.projected_points):.1f})"
            for row in group.itertuples(index=False)
        )
        lines.append(f"| {method} | {objective:.2f} | {players} |")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def summarize_by_method(results: pd.DataFrame) -> pd.DataFrame:
    return (
        results.groupby("method", as_index=False)
        .agg(
            mean_objective=("objective", "mean"),
            median_objective=("objective", "median"),
            mean_optimal_gap=("optimal_gap", "mean"),
            median_optimal_gap=("optimal_gap", "median"),
            max_optimal_gap=("optimal_gap", "max"),
            mean_optimal_gap_pct=("optimal_gap_pct", "mean"),
            mean_runtime_seconds=("runtime_seconds", "mean"),
            mean_mip_gap=("mip_gap", "mean"),
            mean_adp_cost=("adp_cost", "mean"),
            cases=("objective", "size"),
        )
        .sort_values("mean_objective", ascending=False)
    )


def summarize_by_position(results: pd.DataFrame) -> pd.DataFrame:
    return (
        results.groupby(["draft_position", "method"], as_index=False)
        .agg(
            mean_objective=("objective", "mean"),
            mean_optimal_gap=("optimal_gap", "mean"),
            mean_optimal_gap_pct=("optimal_gap_pct", "mean"),
            mean_runtime_seconds=("runtime_seconds", "mean"),
            cases=("objective", "size"),
        )
        .sort_values(["draft_position", "method"])
    )


def summarize_by_delta(results: pd.DataFrame) -> pd.DataFrame:
    return (
        results.groupby(["delta", "method"], as_index=False)
        .agg(
            mean_objective=("objective", "mean"),
            mean_optimal_gap=("optimal_gap", "mean"),
            mean_optimal_gap_pct=("optimal_gap_pct", "mean"),
            mean_runtime_seconds=("runtime_seconds", "mean"),
            cases=("objective", "size"),
        )
        .sort_values(["delta", "method"])
    )


def make_plots(results: pd.DataFrame, outdir: Path) -> None:
    sns.set_theme(style="whitegrid")

    plt.figure(figsize=(10, 5.6))
    sns.barplot(data=results, x="method", y="objective", errorbar="sd")
    plt.title("Mean objective by method")
    plt.xlabel("Method")
    plt.ylabel("Objective")
    plt.xticks(rotation=20, ha="right")
    plt.tight_layout()
    plt.savefig(outdir / "method_comparison.png", dpi=180)
    plt.close()

    adp = results.loc[results["method"] == "ADP-aware ILP"]
    heatmap = adp.pivot_table(index="draft_position", columns="delta", values="objective", aggfunc="mean")
    plt.figure(figsize=(12, 5.8))
    sns.heatmap(heatmap, cmap="viridis", cbar_kws={"label": "Objective"})
    plt.title("ADP-aware ILP objective by draft position and delta")
    plt.xlabel("Delta")
    plt.ylabel("Draft position")
    plt.tight_layout()
    plt.savefig(outdir / "objective_by_position_delta.png", dpi=180)
    plt.close()

    gap_methods = results.loc[results["method"].isin(["Direct Greedy", "Opportunity Cost Greedy"])]
    if not gap_methods.empty:
        by_position = gap_methods.groupby(["draft_position", "method"], as_index=False)["optimal_gap_pct"].mean()
        plt.figure(figsize=(10, 5.6))
        sns.lineplot(data=by_position, x="draft_position", y="optimal_gap_pct", hue="method", marker="o")
        plt.title("Mean optimal gap ratio by draft position")
        plt.xlabel("Draft position")
        plt.ylabel("Optimal gap ratio")
        plt.tight_layout()
        plt.savefig(outdir / "gap_by_draft_position.png", dpi=180)
        plt.close()

        by_delta = gap_methods.groupby(["delta", "method"], as_index=False)["optimal_gap_pct"].mean()
        plt.figure(figsize=(10, 5.6))
        sns.lineplot(data=by_delta, x="delta", y="optimal_gap_pct", hue="method", marker="o")
        plt.title("Mean optimal gap ratio by delta")
        plt.xlabel("Delta")
        plt.ylabel("Optimal gap ratio")
        plt.tight_layout()
        plt.savefig(outdir / "gap_by_delta.png", dpi=180)
        plt.close()

        combined_heatmap = gap_methods.pivot_table(
            index="draft_position",
            columns="delta",
            values="optimal_gap_pct",
            aggfunc="mean",
        )
        plt.figure(figsize=(12, 5.8))
        sns.heatmap(combined_heatmap, cmap="mako_r", cbar_kws={"label": "Optimal gap ratio"})
        plt.title("Heuristic optimal gap ratio")
        plt.xlabel("Delta")
        plt.ylabel("Draft position")
        plt.tight_layout()
        plt.savefig(outdir / "optimal_gap_by_position_delta.png", dpi=180)
        plt.close()

        for method, method_data in gap_methods.groupby("method"):
            heatmap = method_data.pivot_table(
                index="draft_position",
                columns="delta",
                values="optimal_gap_pct",
                aggfunc="mean",
            )
            plt.figure(figsize=(12, 5.8))
            sns.heatmap(heatmap, cmap="mako_r", cbar_kws={"label": "Optimal gap ratio"})
            plt.title(f"Optimal gap ratio: {method}")
            plt.xlabel("Delta")
            plt.ylabel("Draft position")
            plt.tight_layout()
            filename = method.lower().replace(" ", "_").replace("-", "_")
            plt.savefig(outdir / f"{filename}_gap_by_position_delta.png", dpi=180)
            plt.close()

    static = results.loc[results["method"] == "Static IP"]
    if not static.empty:
        heatmap = static.pivot_table(index="draft_position", columns="delta", values="adp_cost", aggfunc="mean")
        plt.figure(figsize=(12, 5.8))
        sns.heatmap(heatmap, cmap="crest", cbar_kws={"label": "Static - ADP-aware objective"})
        plt.title("Estimated ADP availability cost")
        plt.xlabel("Delta")
        plt.ylabel("Draft position")
        plt.tight_layout()
        plt.savefig(outdir / "adp_cost_by_position_delta.png", dpi=180)
        plt.close()


if __name__ == "__main__":
    main()
