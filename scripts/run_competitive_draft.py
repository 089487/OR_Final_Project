from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import pandas as pd

from src.competitive_draft import simulate_competitive_draft
from src.draft_core import load_players


DATASETS = {
    "2026_yahoo": ("data/processed/2026_yahoo_data.csv", "2026_yahoo"),
    "2026_fangraph": ("data/processed/2026_fangraph_data.csv", "2026_fangraph"),
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Simulate a 12-team snake draft with one OCG team and DG opponents."
    )
    parser.add_argument(
        "--datasets",
        default="2026_yahoo,2026_fangraph",
        help="Comma-separated dataset keys. Defaults to 2026_yahoo,2026_fangraph.",
    )
    parser.add_argument("--num-teams", type=int, default=12)
    parser.add_argument(
        "--ocg-team",
        default="all",
        help="OCG draft slot to simulate, or 'all' for every slot. Defaults to all.",
    )
    parser.add_argument(
        "--mode",
        default="single_ocg",
        help="Comma-separated modes: single_ocg, single_dg, all_ocg, all_dg. Defaults to single_ocg.",
    )
    parser.add_argument(
        "--dg-team",
        default="all",
        help="DG draft slot for single_dg mode, or 'all' for every slot. Defaults to all.",
    )
    parser.add_argument(
        "--outdir",
        default="experiments/competitive_draft/ocg_vs_dg_2026",
        help="Output directory.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    ocg_teams = parse_ocg_teams(args.ocg_team, args.num_teams)
    dg_teams = parse_dg_teams(args.dg_team, args.num_teams)
    modes = parse_modes(args.mode)

    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    all_summary_frames: list[pd.DataFrame] = []
    ocg_result_rows: list[dict[str, object]] = []
    dg_result_rows: list[dict[str, object]] = []
    room_result_frames: list[pd.DataFrame] = []

    for dataset_key in parse_dataset_keys(args.datasets):
        players_path, scoring = DATASETS[dataset_key]
        players = load_players(players_path)
        seasons = sorted(players["season"].unique())
        for season in seasons:
            season_players = players.loc[players["season"] == season].reset_index(drop=True)
            for mode in modes:
                mode_team_pairs = build_mode_team_pairs(mode, ocg_teams, dg_teams)
                for ocg_team, dg_team in mode_team_pairs:
                    mode_label = build_mode_label(mode, ocg_team, dg_team)
                    strategy_text = build_strategy_text(mode, ocg_team, dg_team, args.num_teams)
                    print(
                        f"Simulating {scoring}: season={season}, teams={args.num_teams}, {strategy_text}",
                        flush=True,
                    )
                    result = simulate_competitive_draft(
                        season_players,
                        scoring=scoring,
                        season=int(season),
                        num_teams=args.num_teams,
                        ocg_team=ocg_team,
                        dg_team=dg_team,
                        mode=mode,
                    )
                    dataset_dir = outdir / scoring / mode_label
                    dataset_dir.mkdir(parents=True, exist_ok=True)
                    result.picks.to_csv(dataset_dir / "pick_log.csv", index=False)
                    result.rosters.to_csv(dataset_dir / "rosters.csv", index=False)
                    result.summary.to_csv(dataset_dir / "team_summary.csv", index=False)
                    write_markdown_summary(
                        result.summary,
                        dataset_dir / "summary.md",
                        scoring=scoring,
                        season=int(season),
                        num_teams=args.num_teams,
                        mode=mode,
                        ocg_team=ocg_team,
                        dg_team=dg_team,
                        status=result.status,
                        runtime_seconds=result.runtime_seconds,
                    )
                    ranked_summary = result.summary.sort_values("objective", ascending=False).reset_index(drop=True)
                    room_result_frames.append(
                        ranked_summary.assign(
                            scoring=scoring,
                            season=int(season),
                            mode=mode,
                            ocg_team=ocg_team if ocg_team is not None else "",
                            dg_team=dg_team if dg_team is not None else "",
                            rank=ranked_summary.index + 1,
                            draft_status=result.status,
                            runtime_seconds=result.runtime_seconds,
                        )
                    )
                    if mode == "single_ocg" and ocg_team is not None:
                        ocg_row = ranked_summary.loc[ranked_summary["team"] == ocg_team].iloc[0]
                        ocg_result_rows.append(
                            {
                                "scoring": scoring,
                                "season": int(season),
                                "ocg_team": ocg_team,
                                "ocg_objective": float(ocg_row["objective"]),
                                "ocg_rank": int(ranked_summary.index[ranked_summary["team"] == ocg_team][0]) + 1,
                                "best_dg_objective": float(ranked_summary.loc[ranked_summary["strategy"] == "DG", "objective"].max()),
                                "ocg_minus_best_dg": float(ocg_row["objective"])
                                - float(ranked_summary.loc[ranked_summary["strategy"] == "DG", "objective"].max()),
                                "draft_status": result.status,
                                "runtime_seconds": result.runtime_seconds,
                            }
                        )
                    if mode == "single_dg" and dg_team is not None:
                        dg_row = ranked_summary.loc[ranked_summary["team"] == dg_team].iloc[0]
                        dg_result_rows.append(
                            {
                                "scoring": scoring,
                                "season": int(season),
                                "dg_team": dg_team,
                                "dg_objective": float(dg_row["objective"]),
                                "dg_rank": int(ranked_summary.index[ranked_summary["team"] == dg_team][0]) + 1,
                                "best_ocg_objective": float(ranked_summary.loc[ranked_summary["strategy"] == "OCG", "objective"].max()),
                                "dg_minus_best_ocg": float(dg_row["objective"])
                                - float(ranked_summary.loc[ranked_summary["strategy"] == "OCG", "objective"].max()),
                                "draft_status": result.status,
                                "runtime_seconds": result.runtime_seconds,
                            }
                        )
                    all_summary_frames.append(
                        result.summary.assign(
                            mode=mode,
                            ocg_team=ocg_team if ocg_team is not None else "",
                            dg_team=dg_team if dg_team is not None else "",
                            draft_status=result.status,
                            runtime_seconds=result.runtime_seconds,
                        )
                    )

    if all_summary_frames:
        all_summary = pd.concat(all_summary_frames, ignore_index=True)
        all_summary.to_csv(outdir / "combined_team_summary.csv", index=False)
        write_combined_markdown(all_summary, outdir / "combined_summary.md")
    if room_result_frames:
        room_results = pd.concat(room_result_frames, ignore_index=True)
        room_results.to_csv(outdir / "draft_room_results.csv", index=False)
        write_room_results_markdown(room_results, outdir / "draft_room_results.md")
    if ocg_result_rows:
        ocg_results = pd.DataFrame(ocg_result_rows).sort_values(["scoring", "ocg_team"])
        ocg_results.to_csv(outdir / "ocg_team_results.csv", index=False)
        write_ocg_results_markdown(ocg_results, outdir / "ocg_team_results.md")
        print(ocg_results.to_string(index=False))
    if dg_result_rows:
        dg_results = pd.DataFrame(dg_result_rows).sort_values(["scoring", "dg_team"])
        dg_results.to_csv(outdir / "dg_team_results.csv", index=False)
        write_dg_results_markdown(dg_results, outdir / "dg_team_results.md")
        print(dg_results.to_string(index=False))
    print(f"Wrote competitive draft outputs to {outdir.resolve()}")


def parse_dataset_keys(raw: str) -> list[str]:
    keys = [key.strip() for key in raw.split(",") if key.strip()]
    unknown = sorted(set(keys) - set(DATASETS))
    if unknown:
        raise ValueError(f"Unknown dataset(s): {unknown}. Available: {sorted(DATASETS)}")
    return keys


def parse_ocg_teams(raw: str, num_teams: int) -> list[int]:
    value = raw.strip().lower()
    if value == "all":
        return list(range(1, num_teams + 1))
    teams = [int(part.strip()) for part in raw.split(",") if part.strip()]
    invalid = [team for team in teams if team < 1 or team > num_teams]
    if invalid:
        raise ValueError(f"--ocg-team values must be between 1 and {num_teams}: {invalid}")
    return teams


def parse_dg_teams(raw: str, num_teams: int) -> list[int]:
    value = raw.strip().lower()
    if value == "all":
        return list(range(1, num_teams + 1))
    teams = [int(part.strip()) for part in raw.split(",") if part.strip()]
    invalid = [team for team in teams if team < 1 or team > num_teams]
    if invalid:
        raise ValueError(f"--dg-team values must be between 1 and {num_teams}: {invalid}")
    return teams


def parse_modes(raw: str) -> list[str]:
    modes = [mode.strip() for mode in raw.split(",") if mode.strip()]
    valid = {"single_ocg", "single_dg", "all_ocg", "all_dg"}
    unknown = sorted(set(modes) - valid)
    if unknown:
        raise ValueError(f"Unknown mode(s): {unknown}. Available: {sorted(valid)}")
    return modes


def build_mode_team_pairs(
    mode: str,
    ocg_teams: list[int],
    dg_teams: list[int],
) -> list[tuple[int | None, int | None]]:
    if mode == "single_ocg":
        return [(ocg_team, None) for ocg_team in ocg_teams]
    if mode == "single_dg":
        return [(None, dg_team) for dg_team in dg_teams]
    return [(None, None)]


def build_mode_label(mode: str, ocg_team: int | None, dg_team: int | None) -> str:
    if mode == "single_ocg":
        return f"ocg_team_{ocg_team:02d}"
    if mode == "single_dg":
        return f"dg_team_{dg_team:02d}"
    return mode


def build_strategy_text(
    mode: str,
    ocg_team: int | None,
    dg_team: int | None,
    num_teams: int,
) -> str:
    if mode == "single_ocg":
        return f"OCG team={ocg_team}, DG opponents={num_teams - 1}"
    if mode == "single_dg":
        return f"DG team={dg_team}, OCG opponents={num_teams - 1}"
    return mode


def write_markdown_summary(
    summary: pd.DataFrame,
    path: Path,
    *,
    scoring: str,
    season: int,
    num_teams: int,
    mode: str,
    ocg_team: int | None,
    dg_team: int | None,
    status: str,
    runtime_seconds: float,
) -> None:
    if mode == "single_ocg":
        strategy_line = f"- OCG team: Team {ocg_team}\n- Opponents: {num_teams - 1} DG teams"
    elif mode == "single_dg":
        strategy_line = f"- DG team: Team {dg_team}\n- Opponents: {num_teams - 1} OCG teams"
    elif mode == "all_ocg":
        strategy_line = "- Strategy: all teams use OCG"
    else:
        strategy_line = "- Strategy: all teams use DG"
    lines = [
        f"# Competitive Draft Simulation: {scoring}",
        "",
        f"- Season: {season}",
        f"- Teams: {num_teams}",
        f"- Mode: {mode}",
        strategy_line,
        "- Availability model: actual picks only; no ADP constraint",
        f"- Status: {status}",
        f"- Runtime: {runtime_seconds:.3f}s",
        "",
        "| Rank | Team | Strategy | Objective | Picks | Status |",
        "| ---: | ---: | --- | ---: | ---: | --- |",
    ]
    for rank, row in enumerate(summary.itertuples(index=False), start=1):
        lines.append(
            f"| {rank} | {row.team} | {row.strategy} | {float(row.objective):.2f} | "
            f"{int(row.picks)} | {row.status} |"
        )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_combined_markdown(summary: pd.DataFrame, path: Path) -> None:
    lines = [
        "# Competitive Draft Simulation Summary",
        "",
        "| Scoring | Team | Strategy | Objective | Rank | Picks | Status |",
        "| --- | ---: | --- | ---: | ---: | ---: | --- |",
    ]
    for scoring, group in summary.groupby("scoring", sort=False):
        ranked = group.sort_values("objective", ascending=False).reset_index(drop=True)
        for rank, row in enumerate(ranked.itertuples(index=False), start=1):
            label = f"{scoring} / {row.mode}"
            if getattr(row, "ocg_team", "") != "":
                label += f" / OCG team {row.ocg_team}"
            if getattr(row, "dg_team", "") != "":
                label += f" / DG team {row.dg_team}"
            lines.append(
                f"| {label} | {row.team} | {row.strategy} | {float(row.objective):.2f} | "
                f"{rank} | {int(row.picks)} | {row.status} |"
            )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_room_results_markdown(results: pd.DataFrame, path: Path) -> None:
    lines = [
        "# Draft Room Results",
        "",
        "| Scoring | Mode | OCG Team | DG Team | Rank | Team | Strategy | Objective | Status |",
        "| --- | --- | ---: | ---: | ---: | ---: | --- | ---: | --- |",
    ]
    ordered = results.sort_values(["scoring", "mode", "rank"])
    for row in ordered.itertuples(index=False):
        lines.append(
            f"| {row.scoring} | {row.mode} | {row.ocg_team} | {row.dg_team} | {int(row.rank)} | "
            f"{int(row.team)} | {row.strategy} | {float(row.objective):.2f} | {row.status} |"
        )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_ocg_results_markdown(results: pd.DataFrame, path: Path) -> None:
    lines = [
        "# OCG Draft Slot Results",
        "",
        "| Scoring | OCG Team | OCG Objective | OCG Rank | Best DG Objective | OCG - Best DG | Status |",
        "| --- | ---: | ---: | ---: | ---: | ---: | --- |",
    ]
    for row in results.itertuples(index=False):
        lines.append(
            f"| {row.scoring} | {row.ocg_team} | {float(row.ocg_objective):.2f} | "
            f"{int(row.ocg_rank)} | {float(row.best_dg_objective):.2f} | "
            f"{float(row.ocg_minus_best_dg):+.2f} | {row.draft_status} |"
        )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_dg_results_markdown(results: pd.DataFrame, path: Path) -> None:
    lines = [
        "# DG Draft Slot Results Against OCG Room",
        "",
        "| Scoring | DG Team | DG Objective | DG Rank | Best OCG Objective | DG - Best OCG | Status |",
        "| --- | ---: | ---: | ---: | ---: | ---: | --- |",
    ]
    for row in results.itertuples(index=False):
        lines.append(
            f"| {row.scoring} | {row.dg_team} | {float(row.dg_objective):.2f} | "
            f"{int(row.dg_rank)} | {float(row.best_ocg_objective):.2f} | "
            f"{float(row.dg_minus_best_ocg):+.2f} | {row.draft_status} |"
        )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
