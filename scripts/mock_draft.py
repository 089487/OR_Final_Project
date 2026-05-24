from __future__ import annotations

import argparse
import os
import sys
from dataclasses import dataclass
from pathlib import Path

os.environ.setdefault("MPLCONFIGDIR", str(Path("mock_results") / ".matplotlib"))

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

from src.draft_model import (
    ROSTER_REQUIREMENTS,
    eligible_for,
    load_players,
    snake_picks,
    solve_draft,
)


MODEL_METHODS = ("ip", "direct_greedy", "opportunity_cost_greedy")
MOCK_METHODS = MODEL_METHODS + ("noisy_adp",)
METHOD_LABELS = {
    "ip": "IP",
    "direct_greedy": "Direct Greedy",
    "opportunity_cost_greedy": "Opportunity Cost Greedy",
    "noisy_adp": "Noisy ADP",
}


@dataclass
class TeamState:
    team: int
    remaining_slots: dict[str, int]
    roster: list[dict[str, object]]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run Monte Carlo 12-team snake mock drafts.")
    parser.add_argument("--players", default="data/processed/2026_yahoo_data.csv", help="Processed player CSV.")
    parser.add_argument("--outdir", default="mock_results", help="Output directory.")
    parser.add_argument("--num-teams", type=int, default=12)
    parser.add_argument("--draft-position", type=int, default=1, help="Our team draft position.")
    parser.add_argument("--simulations", type=int, default=50)
    parser.add_argument("--seed", type=int, default=1142)
    parser.add_argument("--delta", type=float, default=10.0, help="ADP buffer used inside our IP lookahead.")
    parser.add_argument("--adp-std", type=float, default=18.0, help="Opponent draft-board ADP noise.")
    parser.add_argument("--candidate-pool", type=int, default=12, help="Opponent samples among top noisy-ADP candidates.")
    parser.add_argument("--ip-time-limit", type=int, default=20)
    parser.add_argument(
        "--our-method",
        choices=MOCK_METHODS,
        default="ip",
        help="How the focal team drafts.",
    )
    parser.add_argument(
        "--opponent-method",
        choices=MOCK_METHODS,
        default="noisy_adp",
        help="How non-focal teams draft.",
    )
    parser.add_argument(
        "--opponent-strategy",
        choices=MOCK_METHODS,
        default=None,
        help="Backward-compatible alias for --opponent-method.",
    )
    parser.add_argument("--verbose", action="store_true", help="Write pick-by-pick mock draft logs.")
    args = parser.parse_args()
    if args.opponent_strategy is not None:
        args.opponent_method = args.opponent_strategy
    return args


def main() -> None:
    args = parse_args()
    players = load_players(args.players)
    seasons = sorted(players["season"].unique())
    if len(seasons) != 1:
        raise ValueError("mock_draft.py expects one season in the input CSV")

    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    rng = np.random.default_rng(args.seed)

    summary_rows: list[dict[str, object]] = []
    our_roster_rows: list[dict[str, object]] = []
    team_summary_rows: list[dict[str, object]] = []
    all_roster_rows: list[dict[str, object]] = []
    pick_rows: list[dict[str, object]] = []

    for simulation in range(1, args.simulations + 1):
        result = run_mock_draft(
            players=players,
            season=int(seasons[0]),
            simulation=simulation,
            num_teams=args.num_teams,
            our_draft_position=args.draft_position,
            rng=rng,
            delta=args.delta,
            adp_std=args.adp_std,
            candidate_pool=args.candidate_pool,
            ip_time_limit=args.ip_time_limit,
            our_method=args.our_method,
            opponent_method=args.opponent_method,
        )
        summary_rows.append(result["summary"])
        our_roster_rows.extend(result["our_roster"])
        team_summary_rows.extend(result["team_summary"])
        all_roster_rows.extend(result["all_rosters"])
        if args.verbose:
            pick_rows.extend(result["picks"])

    summary = pd.DataFrame(summary_rows)
    our_rosters = pd.DataFrame(our_roster_rows)
    team_summary = pd.DataFrame(team_summary_rows)
    all_rosters = pd.DataFrame(all_roster_rows)
    summary.to_csv(outdir / "mock_draft_summary.csv", index=False)
    our_rosters.to_csv(outdir / "mock_draft_our_rosters.csv", index=False)
    team_summary.to_csv(outdir / "mock_draft_team_summary.csv", index=False)
    all_rosters.to_csv(outdir / "mock_draft_all_rosters.csv", index=False)
    if args.verbose:
        picks = pd.DataFrame(pick_rows)
        picks.to_csv(outdir / "mock_draft_picks.csv", index=False)
        write_verbose_log(picks, outdir / "mock_draft_picks.txt")
    make_plots(team_summary, outdir)

    print(f"Wrote mock draft outputs to {outdir.resolve()}")
    print(summary.describe(include="all").to_string())


def run_mock_draft(
    *,
    players: pd.DataFrame,
    season: int,
    simulation: int,
    num_teams: int,
    our_draft_position: int,
    rng: np.random.Generator,
    delta: float,
    adp_std: float,
    candidate_pool: int,
    ip_time_limit: int,
    our_method: str,
    opponent_method: str,
) -> dict[str, object]:
    rounds = sum(ROSTER_REQUIREMENTS.values())
    total_picks = rounds * num_teams
    team_by_pick = build_snake_team_by_pick(num_teams, rounds)
    pick_numbers_by_team = {
        team: snake_picks(num_teams, team, rounds)
        for team in range(1, num_teams + 1)
    }
    teams = {
        team: TeamState(team=team, remaining_slots=dict(ROSTER_REQUIREMENTS), roster=[])
        for team in range(1, num_teams + 1)
    }

    available = players.reset_index(drop=True).copy()
    available["mock_board_rank"] = (
        available["adp"].astype(float) + rng.normal(0.0, adp_std, size=len(available))
    ).clip(lower=1.0)
    pick_log: list[dict[str, object]] = []

    for overall_pick in range(1, total_picks + 1):
        team = team_by_pick[overall_pick]
        team_state = teams[team]
        if sum(team_state.remaining_slots.values()) == 0:
            continue

        team_method = our_method if team == our_draft_position else opponent_method
        method = METHOD_LABELS[team_method]
        if team_method == "noisy_adp":
            choice = choose_noisy_adp_pick(
                available=available,
                team_state=team_state,
                overall_pick=overall_pick,
                candidate_pool=candidate_pool,
                rng=rng,
            )
        else:
            choice = choose_model_pick(
                available=available,
                team_state=team_state,
                season=season,
                draft_position=team,
                current_pick=overall_pick,
                team_pick_numbers=pick_numbers_by_team[team],
                method=team_method,
                delta=delta,
                time_limit=ip_time_limit,
                enforce_adp=True,
            )

        if choice is None:
            continue

        row_index, assigned_position = choice
        player = available.loc[row_index]
        roster_row = make_pick_row(
            simulation=simulation,
            season=season,
            overall_pick=overall_pick,
            round_number=((overall_pick - 1) // num_teams) + 1,
            team=team,
            method=method,
            player=player,
            assigned_position=assigned_position,
        )
        team_state.remaining_slots[assigned_position] -= 1
        team_state.roster.append(roster_row)
        pick_log.append(roster_row)
        available = available.drop(index=row_index)

    our_team = teams[our_draft_position]
    our_points = sum(float(row["points"]) for row in our_team.roster)
    team_summary = []
    all_rosters = []
    for team, team_state in sorted(teams.items()):
        team_points = sum(float(row["points"]) for row in team_state.roster)
        unfilled_slots = sum(team_state.remaining_slots.values())
        team_summary.append(
            {
                "simulation": simulation,
                "season": season,
                "team": team,
                "is_our_team": team == our_draft_position,
                "our_method": our_method,
                "opponent_method": opponent_method,
                "method": METHOD_LABELS[our_method] if team == our_draft_position else METHOD_LABELS[opponent_method],
                "team_points": round(team_points, 2),
                "picked_players": len(team_state.roster),
                "unfilled_slots": unfilled_slots,
            }
        )
        all_rosters.extend(team_state.roster)

    summary = {
        "simulation": simulation,
        "season": season,
        "draft_position": our_draft_position,
        "our_method": our_method,
        "opponent_method": opponent_method,
        "team_points": round(our_points, 2),
        "picked_players": len(our_team.roster),
        "unfilled_slots": sum(our_team.remaining_slots.values()),
    }
    return {
        "summary": summary,
        "our_roster": our_team.roster,
        "team_summary": team_summary,
        "all_rosters": all_rosters,
        "picks": pick_log,
    }


def choose_model_pick(
    *,
    available: pd.DataFrame,
    team_state: TeamState,
    season: int,
    draft_position: int,
    current_pick: int,
    team_pick_numbers: list[int],
    method: str,
    delta: float,
    time_limit: int,
    enforce_adp: bool,
) -> tuple[int, str] | None:
    remaining_slots = {pos: count for pos, count in team_state.remaining_slots.items() if count > 0}
    future_picks = [pick for pick in team_pick_numbers if pick >= current_pick][: sum(remaining_slots.values())]
    if not remaining_slots or len(future_picks) != sum(remaining_slots.values()):
        return None

    solution = solve_draft(
        method,
        available.drop(columns=["mock_board_rank"], errors="ignore"),
        future_picks,
        season=season,
        draft_position=draft_position,
        delta=delta,
        roster_requirements=remaining_slots,
        enforce_adp=enforce_adp,
        time_limit=time_limit,
    )
    if solution.roster.empty:
        return choose_greedy_feasible(available, team_state)

    current_pick_row = solution.roster.loc[solution.roster["overall_pick"] == current_pick]
    if current_pick_row.empty:
        return choose_greedy_feasible(available, team_state)

    selected = current_pick_row.iloc[0]
    matches = available.index[available["player"] == selected["player"]].tolist()
    if not matches:
        return choose_greedy_feasible(available, team_state)
    return matches[0], str(selected["assigned_position"])


def choose_noisy_adp_pick(
    *,
    available: pd.DataFrame,
    team_state: TeamState,
    overall_pick: int,
    candidate_pool: int,
    rng: np.random.Generator,
) -> tuple[int, str] | None:
    feasible = feasible_players(available, team_state.remaining_slots)
    if feasible.empty:
        return None

    ranked = feasible.assign(
        draft_score=(feasible["mock_board_rank"] - overall_pick).abs()
    ).sort_values(["draft_score", "mock_board_rank", "adp"])
    pool = ranked.head(max(1, candidate_pool))
    weights = 1.0 / (np.arange(len(pool)) + 1.0)
    weights = weights / weights.sum()
    row_index = int(rng.choice(pool.index.to_numpy(), p=weights))
    assigned_position = best_open_position(available.loc[row_index]["eligible_positions"], team_state.remaining_slots)
    if assigned_position is None:
        return None
    return row_index, assigned_position


def choose_greedy_feasible(available: pd.DataFrame, team_state: TeamState) -> tuple[int, str] | None:
    feasible = feasible_players(available, team_state.remaining_slots)
    if feasible.empty:
        return None
    row_index = int(feasible.sort_values("projected_points", ascending=False).index[0])
    assigned_position = best_open_position(available.loc[row_index]["eligible_positions"], team_state.remaining_slots)
    if assigned_position is None:
        return None
    return row_index, assigned_position


def feasible_players(available: pd.DataFrame, remaining_slots: dict[str, int]) -> pd.DataFrame:
    mask = available["eligible_positions"].map(
        lambda positions: best_open_position(positions, remaining_slots) is not None
    )
    return available.loc[mask]


def best_open_position(player_positions: tuple[str, ...], remaining_slots: dict[str, int]) -> str | None:
    feasible_positions = [
        pos
        for pos, slots in remaining_slots.items()
        if slots > 0 and eligible_for(player_positions, pos)
    ]
    if not feasible_positions:
        return None
    return sorted(feasible_positions, key=lambda pos: (remaining_slots[pos], 0 if pos != "Util" else 1))[0]


def build_snake_team_by_pick(num_teams: int, rounds: int) -> dict[int, int]:
    team_by_pick = {}
    for round_number in range(1, rounds + 1):
        teams = range(1, num_teams + 1)
        if round_number % 2 == 0:
            teams = range(num_teams, 0, -1)
        for offset, team in enumerate(teams, start=1):
            overall_pick = (round_number - 1) * num_teams + offset
            team_by_pick[overall_pick] = team
    return team_by_pick


def make_pick_row(
    *,
    simulation: int,
    season: int,
    overall_pick: int,
    round_number: int,
    team: int,
    method: str,
    player: pd.Series,
    assigned_position: str,
) -> dict[str, object]:
    return {
        "simulation": simulation,
        "season": season,
        "round": round_number,
        "overall_pick": overall_pick,
        "team": team,
        "method": method,
        "player": player["player"],
        "assigned_position": assigned_position,
        "eligible_positions": ";".join(player["eligible_positions"]),
        "adp": float(player["adp"]),
        "points": float(player["projected_points"]),
    }


def write_verbose_log(picks: pd.DataFrame, output_path: Path) -> None:
    lines: list[str] = []
    for simulation, group in picks.sort_values(["simulation", "overall_pick"]).groupby("simulation"):
        lines.append(f"Simulation {simulation}")
        for row in group.itertuples(index=False):
            lines.append(
                f"  Pick {int(row.overall_pick):03d} "
                f"(R{int(row.round):02d}, Team {int(row.team):02d}, {row.method}): "
                f"{row.player} -> {row.assigned_position} "
                f"(ADP {float(row.adp):.2f}, points {float(row.points):.2f})"
            )
        lines.append("")
    output_path.write_text("\n".join(lines), encoding="utf-8")


def make_plots(team_summary: pd.DataFrame, outdir: Path) -> None:
    if team_summary.empty:
        return

    sns.set_theme(style="whitegrid")
    average_points = team_summary.groupby("team", as_index=False)["team_points"].mean()
    plt.figure(figsize=(10, 5.6))
    sns.barplot(data=average_points, x="team", y="team_points", color="#4C78A8")
    plt.title("Average mock draft points by team")
    plt.xlabel("Team")
    plt.ylabel("Projected points")
    plt.tight_layout()
    plt.savefig(outdir / "team_points_bar.png", dpi=180)
    plt.close()

    if team_summary["simulation"].nunique() > 1:
        plt.figure(figsize=(10, 5.6))
        sns.lineplot(
            data=team_summary,
            x="simulation",
            y="team_points",
            hue="team",
            marker="o",
            palette="tab20",
            legend=False,
        )
        plt.title("Team points across mock draft simulations")
        plt.xlabel("Simulation")
        plt.ylabel("Projected points")
        plt.tight_layout()
        plt.savefig(outdir / "team_points_by_simulation.png", dpi=180)
        plt.close()

        heatmap_data = team_summary.pivot(index="team", columns="simulation", values="team_points")
        plt.figure(figsize=(max(8, team_summary["simulation"].nunique() * 0.45), 5.8))
        sns.heatmap(heatmap_data, cmap="viridis", annot=False, cbar_kws={"label": "Projected points"})
        plt.title("Mock draft team points heatmap")
        plt.xlabel("Simulation")
        plt.ylabel("Team")
        plt.tight_layout()
        plt.savefig(outdir / "team_points_heatmap.png", dpi=180)
        plt.close()


if __name__ == "__main__":
    main()
