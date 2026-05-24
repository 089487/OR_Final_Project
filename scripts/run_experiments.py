from __future__ import annotations

import argparse
import os
import sys
from dataclasses import replace
from pathlib import Path

os.environ.setdefault("MPLCONFIGDIR", str(Path("results") / ".matplotlib"))
os.environ.setdefault("XDG_CACHE_HOME", str(Path("results") / ".cache"))

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

from src.draft_model import (
    ROSTER_REQUIREMENTS,
    load_players,
    snake_picks,
    solve_greedy,
    solve_ilp,
    summarize_solution,
)
from src.generate_sample_data import generate_sample_players


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run fantasy baseball snake-draft experiments.")
    parser.add_argument("--players", default="data/raw/sample_players.csv", help="Player CSV path.")
    parser.add_argument("--generate-sample", action="store_true", help="Regenerate sample data first.")
    parser.add_argument("--num-teams", type=int, default=12, help="Number of snake-draft teams.")
    parser.add_argument("--delta", type=float, default=10.0, help="ADP availability buffer.")
    parser.add_argument(
        "--delta-grid",
        default=None,
        help="Comma-separated delta values for sensitivity analysis. Overrides delta min/max/step.",
    )
    parser.add_argument("--delta-min", type=float, default=-10.0, help="Minimum delta for sensitivity analysis.")
    parser.add_argument("--delta-max", type=float, default=10.0, help="Maximum delta for sensitivity analysis.")
    parser.add_argument("--delta-step", type=float, default=1.0, help="Delta stride for sensitivity analysis.")
    parser.add_argument("--outdir", default="results", help="Output directory.")
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Write a human-readable draft result file with each pick and selected player.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    player_path = Path(args.players)
    if args.generate_sample or not player_path.exists():
        generate_sample_players(player_path)

    players = load_players(player_path)
    seasons = sorted(players["season"].unique())
    rounds = sum(ROSTER_REQUIREMENTS.values())
    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)

    summary_rows: list[dict[str, object]] = []
    roster_frames: list[pd.DataFrame] = []
    shadow_frames: list[pd.DataFrame] = []

    for season in seasons:
        season_players = players.loc[players["season"] == season].reset_index(drop=True)
        static_base_picks = snake_picks(args.num_teams, 1, rounds)
        static_base = solve_ilp(
            season_players,
            static_base_picks,
            season=season,
            draft_position=1,
            delta=args.delta,
            enforce_adp=False,
            method_name="Static IP",
        )
        middle_position = (args.num_teams + 1) // 2
        middle_picks = snake_picks(args.num_teams, middle_position, rounds)
        relaxed = solve_ilp(
            season_players,
            middle_picks,
            season=season,
            draft_position=middle_position,
            delta=args.delta,
            enforce_adp=True,
            relax=True,
            method_name="ADP-aware LP relaxation",
        )
        if relaxed.shadow_prices is not None:
            shadows = relaxed.shadow_prices.copy()
            shadows["season"] = season
            shadows["draft_position"] = middle_position
            shadows["delta"] = args.delta
            shadow_frames.append(shadows)

        for draft_position in range(1, args.num_teams + 1):
            picks = snake_picks(args.num_teams, draft_position, rounds)
            static_roster = static_base.roster.copy()
            if not static_roster.empty:
                static_roster["draft_position"] = draft_position
                static_roster["overall_pick"] = picks[: len(static_roster)]
            static_solution = replace(
                static_base,
                draft_position=draft_position,
                roster=static_roster,
            )
            solutions = [
                solve_ilp(
                    season_players,
                    picks,
                    season=season,
                    draft_position=draft_position,
                    delta=args.delta,
                    enforce_adp=True,
                    method_name="ADP-aware ILP",
                ),
                static_solution,
                solve_greedy(
                    season_players,
                    picks,
                    season=season,
                    draft_position=draft_position,
                    delta=args.delta,
                    enforce_adp=True,
                ),
            ]

            for solution in solutions:
                summary_rows.append(summarize_solution(solution))
                if not solution.roster.empty:
                    roster_frames.append(solution.roster)

    summary = pd.DataFrame(summary_rows)
    rosters = pd.concat(roster_frames, ignore_index=True) if roster_frames else pd.DataFrame()
    shadows = pd.concat(shadow_frames, ignore_index=True) if shadow_frames else pd.DataFrame()

    summary.to_csv(outdir / "draft_position_summary.csv", index=False)
    rosters.to_csv(outdir / "optimal_rosters.csv", index=False)
    shadows.to_csv(outdir / "shadow_prices.csv", index=False)

    delta_values = make_delta_values(args.delta_grid, args.delta_min, args.delta_max, args.delta_step)
    sensitivity = run_delta_sensitivity(players, seasons, args.num_teams, rounds, delta_values)
    sensitivity.to_csv(outdir / "delta_sensitivity.csv", index=False)

    make_plots(summary, shadows, sensitivity, outdir)
    write_report(summary, shadows, sensitivity, outdir)
    if args.verbose:
        verbose_path = write_verbose_draft_results(rosters, summary, outdir)
        print(f"Wrote verbose draft results to {verbose_path}")

    print(f"Wrote experiment outputs to {outdir.resolve()}")
    print(summary.groupby("method")["objective"].mean().round(2).to_string())


def run_delta_sensitivity(
    players: pd.DataFrame,
    seasons: list[int],
    num_teams: int,
    rounds: int,
    deltas: list[float],
) -> pd.DataFrame:
    rows = []
    middle_position = (num_teams + 1) // 2

    for delta in deltas:
        for season in seasons:
            season_players = players.loc[players["season"] == season].reset_index(drop=True)
            picks = snake_picks(num_teams, middle_position, rounds)
            solution = solve_ilp(
                season_players,
                picks,
                season=season,
                draft_position=middle_position,
                delta=delta,
                enforce_adp=True,
                method_name="ADP-aware ILP",
            )
            rows.append(summarize_solution(solution))
    return pd.DataFrame(rows)


def make_delta_values(
    delta_grid: str | None,
    delta_min: float,
    delta_max: float,
    delta_step: float,
) -> list[float]:
    if delta_grid:
        return [float(value.strip()) for value in delta_grid.split(",") if value.strip()]
    if delta_step <= 0:
        raise ValueError("delta_step must be positive")
    if delta_max < delta_min:
        raise ValueError("delta_max must be greater than or equal to delta_min")

    values = []
    current = delta_min
    tolerance = delta_step / 1_000_000
    while current <= delta_max + tolerance:
        values.append(round(current, 10))
        current += delta_step
    return values


def make_plots(
    summary: pd.DataFrame,
    shadows: pd.DataFrame,
    sensitivity: pd.DataFrame,
    outdir: Path,
) -> None:
    sns.set_theme(style="whitegrid")

    plt.figure(figsize=(10, 5.6))
    plot_data = (
        summary.loc[summary["status"] == "OPTIMAL"]
        .groupby(["draft_position", "method"], as_index=False)["objective"]
        .mean()
    )
    sns.lineplot(
        data=plot_data,
        x="draft_position",
        y="objective",
        hue="method",
        marker="o",
    )
    plt.title("Average projected points by snake-draft position")
    plt.xlabel("Draft position")
    plt.ylabel("Projected points")
    plt.tight_layout()
    plt.savefig(outdir / "draft_position_comparison.png", dpi=180)
    plt.close()

    if not shadows.empty:
        plt.figure(figsize=(9, 5.4))
        shadow_data = shadows.groupby("position", as_index=False)["shadow_price"].mean()
        order = shadow_data.sort_values("shadow_price", ascending=False)["position"]
        sns.barplot(data=shadow_data, x="position", y="shadow_price", order=order)
        plt.title("Average LP shadow price by roster position")
        plt.xlabel("Position")
        plt.ylabel("Shadow price")
        plt.tight_layout()
        plt.savefig(outdir / "position_shadow_prices.png", dpi=180)
        plt.close()

    plt.figure(figsize=(8, 5))
    sensitivity_plot = (
        sensitivity.loc[sensitivity["status"] == "OPTIMAL"]
        .groupby("delta", as_index=False)["objective"]
        .mean()
    )
    sns.lineplot(data=sensitivity_plot, x="delta", y="objective", marker="o")
    plt.title("ADP buffer sensitivity")
    plt.xlabel("Delta")
    plt.ylabel("Projected points")
    plt.tight_layout()
    plt.savefig(outdir / "delta_sensitivity.png", dpi=180)
    plt.close()


def write_report(
    summary: pd.DataFrame,
    shadows: pd.DataFrame,
    sensitivity: pd.DataFrame,
    outdir: Path,
) -> None:
    optimal = summary.loc[summary["status"] == "OPTIMAL"].copy()
    method_means = optimal.groupby("method")["objective"].mean().sort_values(ascending=False)
    slot_means = (
        optimal.loc[optimal["method"] == "ADP-aware ILP"]
        .groupby("draft_position")["objective"]
        .mean()
        .sort_values(ascending=False)
    )

    lines = [
        "# Fantasy Baseball Snake-Draft Optimization Report",
        "",
        "## Experiment setup",
        "",
        "- Solver: Gurobi integer programming.",
        "- League: 12-team snake draft by default.",
        f"- Roster: {ROSTER_REQUIREMENTS}.",
        "- Objective: maximize total projected fantasy points.",
        "- Availability rule: player i is unavailable at pick k when ADP_i + delta < pick_k.",
        "",
        "## Method comparison",
        "",
        method_means.round(2).to_markdown(),
        "",
        "## Draft-position advantage",
        "",
        "Best ADP-aware draft slots by average projected points:",
        "",
        slot_means.head(5).round(2).to_markdown(),
        "",
    ]

    if not shadows.empty:
        shadow_means = shadows.groupby("position")["shadow_price"].mean().sort_values(ascending=False)
        lines.extend(
            [
                "## Positional scarcity from LP shadow prices",
                "",
                shadow_means.round(2).to_markdown(),
                "",
            ]
        )

    sensitivity_means = sensitivity.groupby("delta")["objective"].mean()
    lines.extend(
        [
            "## ADP buffer sensitivity",
            "",
            sensitivity_means.round(2).to_markdown(),
            "",
            "Generated charts:",
            "",
            "- `draft_position_comparison.png`",
            "- `position_shadow_prices.png`",
            "- `delta_sensitivity.png`",
        ]
    )

    (outdir / "summary_report.md").write_text("\n".join(lines), encoding="utf-8")


def write_verbose_draft_results(rosters: pd.DataFrame, summary: pd.DataFrame, outdir: Path) -> Path:
    output_path = outdir / "draft_pick_results.txt"
    if rosters.empty:
        output_path.write_text("No roster results were produced.\n", encoding="utf-8")
        return output_path

    objective_lookup = {
        (int(row.season), str(row.method), int(row.draft_position)): row.objective
        for row in summary.itertuples(index=False)
    }
    sort_columns = ["season", "method", "draft_position", "round", "overall_pick"]
    roster_view = rosters.sort_values(sort_columns)
    lines: list[str] = []

    for (season, method, draft_position), group in roster_view.groupby(
        ["season", "method", "draft_position"],
        sort=True,
    ):
        objective = objective_lookup.get((int(season), str(method), int(draft_position)))
        objective_text = "" if pd.isna(objective) else f" | objective={float(objective):.2f}"
        lines.append(f"Season {season} | {method} | draft position {draft_position}{objective_text}")

        for row in group.itertuples(index=False):
            lines.append(
                "  "
                f"Round {int(row.round):02d}, "
                f"overall pick {int(row.overall_pick):03d}: "
                f"{row.player} -> {row.assigned_position} "
                f"(eligible: {row.eligible_positions}, "
                f"ADP: {float(row.adp):.2f}, "
                f"points: {float(row.projected_points):.2f})"
            )
        lines.append("")

    output_path.write_text("\n".join(lines), encoding="utf-8")
    return output_path


if __name__ == "__main__":
    main()
