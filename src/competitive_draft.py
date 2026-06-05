from __future__ import annotations

from dataclasses import dataclass
from time import perf_counter

import pandas as pd

from src.draft_core import ROSTER_REQUIREMENTS, eligible_for


@dataclass(frozen=True)
class CompetitiveDraftResult:
    scoring: str
    season: int
    num_teams: int
    mode: str
    ocg_team: int | None
    dg_team: int | None
    status: str
    runtime_seconds: float
    picks: pd.DataFrame
    rosters: pd.DataFrame
    summary: pd.DataFrame


def simulate_competitive_draft(
    players: pd.DataFrame,
    *,
    scoring: str,
    season: int = 2026,
    num_teams: int = 12,
    ocg_team: int | None = 6,
    dg_team: int | None = None,
    mode: str = "single_ocg",
    roster_requirements: dict[str, int] | None = None,
) -> CompetitiveDraftResult:
    """Simulate a snake draft with configurable DG/OCG team strategies.

    Availability is driven only by actual selections in this simulated draft room;
    ADP is recorded for context but is not used as a constraint.
    """
    team_strategies = build_team_strategies(
        mode=mode,
        num_teams=num_teams,
        ocg_team=ocg_team,
        dg_team=dg_team,
    )
    start_time = perf_counter()
    roster_requirements = dict(roster_requirements or ROSTER_REQUIREMENTS)
    rounds = sum(roster_requirements.values())
    data = players.reset_index(drop=True).copy()
    if "player" not in data.columns and "player_name" in data.columns:
        data = data.rename(columns={"player_name": "player"})
    if "projected_points" not in data.columns and "points" in data.columns:
        data = data.rename(columns={"points": "projected_points"})

    positions = tuple(roster_requirements)
    eligible_indices = build_eligible_indices(data, positions)
    remaining_by_team = {
        team: dict(roster_requirements)
        for team in range(1, num_teams + 1)
    }
    selected: set[int] = set()
    pick_rows: list[dict[str, object]] = []
    status = "COMPLETE"

    for overall_pick in range(1, num_teams * rounds + 1):
        round_number = (overall_pick - 1) // num_teams + 1
        team = team_for_pick(overall_pick, num_teams)
        strategy = team_strategies[team]
        if strategy == "OCG":
            choice = choose_ocg_pick(
                data=data,
                eligible_indices=eligible_indices,
                selected=selected,
                remaining_by_team=remaining_by_team,
                team=team,
                num_teams=num_teams,
                overall_pick=overall_pick,
            )
        else:
            choice = choose_dg_pick(
                data=data,
                eligible_indices=eligible_indices,
                selected=selected,
                remaining=remaining_by_team[team],
            )

        if choice is None:
            status = "INFEASIBLE"
            break

        player_index, assigned_position = choice
        selected.add(player_index)
        remaining_by_team[team][assigned_position] -= 1
        row = data.loc[player_index]
        pick_rows.append(
            {
                "scoring": scoring,
                "season": season,
                "overall_pick": overall_pick,
                "round": round_number,
                "team": team,
                "strategy": strategy,
                "player": row["player"],
                "assigned_position": assigned_position,
                "eligible_positions": ";".join(row["eligible_positions"]),
                "projected_points": float(row["projected_points"]),
                "adp": float(row["adp"]),
            }
        )

    picks = pd.DataFrame(pick_rows)
    rosters = picks.copy()
    summary = summarize_competitive_rosters(
        rosters=rosters,
        remaining_by_team=remaining_by_team,
        num_teams=num_teams,
        team_strategies=team_strategies,
        scoring=scoring,
        season=season,
    )
    return CompetitiveDraftResult(
        scoring=scoring,
        season=season,
        num_teams=num_teams,
        mode=mode,
        ocg_team=ocg_team,
        dg_team=dg_team,
        status=status,
        runtime_seconds=perf_counter() - start_time,
        picks=picks,
        rosters=rosters,
        summary=summary,
    )


def build_team_strategies(
    *,
    mode: str,
    num_teams: int,
    ocg_team: int | None,
    dg_team: int | None,
) -> dict[int, str]:
    if mode == "all_ocg":
        return {team: "OCG" for team in range(1, num_teams + 1)}
    if mode == "all_dg":
        return {team: "DG" for team in range(1, num_teams + 1)}
    if mode == "single_dg":
        if dg_team is None:
            raise ValueError("dg_team is required for single_dg mode")
        if not 1 <= dg_team <= num_teams:
            raise ValueError("dg_team must be between 1 and num_teams")
        return {
            team: "DG" if team == dg_team else "OCG"
            for team in range(1, num_teams + 1)
        }
    if mode == "single_ocg":
        if ocg_team is None:
            raise ValueError("ocg_team is required for single_ocg mode")
        if not 1 <= ocg_team <= num_teams:
            raise ValueError("ocg_team must be between 1 and num_teams")
        return {
            team: "OCG" if team == ocg_team else "DG"
            for team in range(1, num_teams + 1)
        }
    raise ValueError(f"Unknown competitive draft mode: {mode}")


def team_for_pick(overall_pick: int, num_teams: int) -> int:
    round_index = (overall_pick - 1) // num_teams
    within_round = (overall_pick - 1) % num_teams
    if round_index % 2 == 0:
        return within_round + 1
    return num_teams - within_round


def choose_dg_pick(
    *,
    data: pd.DataFrame,
    eligible_indices: dict[str, list[int]],
    selected: set[int],
    remaining: dict[str, int],
) -> tuple[int, str] | None:
    candidate_positions = []
    for position, need in remaining.items():
        if need <= 0:
            continue
        available = available_for_position(eligible_indices, selected, position)
        if not available:
            continue
        player_index = max(available, key=lambda idx: float(data.at[idx, "projected_points"]))
        active_count = len(available)
        candidate_positions.append(
            (
                position,
                player_index,
                need / active_count,
                float(data.at[player_index, "projected_points"]),
            )
        )
    if not candidate_positions:
        return None
    position, player_index, _scarcity, _points = max(
        candidate_positions,
        key=lambda item: (item[2], item[3]),
    )
    return player_index, position


def choose_ocg_pick(
    *,
    data: pd.DataFrame,
    eligible_indices: dict[str, list[int]],
    selected: set[int],
    remaining_by_team: dict[int, dict[str, int]],
    team: int,
    num_teams: int,
    overall_pick: int,
) -> tuple[int, str] | None:
    remaining = remaining_by_team[team]
    candidate_choices = []
    for position, need in remaining.items():
        if need <= 0:
            continue
        available = available_for_position(eligible_indices, selected, position)
        if not available:
            continue
        player_index = max(available, key=lambda idx: float(data.at[idx, "projected_points"]))
        current_points = float(data.at[player_index, "projected_points"])
        future_points = estimate_future_position_value(
            data=data,
            eligible_indices=eligible_indices,
            selected=selected,
            remaining_by_team=remaining_by_team,
            team=team,
            num_teams=num_teams,
            overall_pick=overall_pick,
            player_index=player_index,
            assigned_position=position,
        )
        active_count = len(available)
        forced = active_count <= need
        candidate_choices.append(
            (
                forced,
                current_points - future_points,
                need / active_count,
                current_points,
                player_index,
                position,
            )
        )
    if not candidate_choices:
        return None

    _forced, _delay_cost, _scarcity, _points, player_index, position = max(
        candidate_choices,
        key=lambda item: (item[0], item[1], item[2], item[3]),
    )
    return player_index, position


def estimate_future_position_value(
    *,
    data: pd.DataFrame,
    eligible_indices: dict[str, list[int]],
    selected: set[int],
    remaining_by_team: dict[int, dict[str, int]],
    team: int,
    num_teams: int,
    overall_pick: int,
    player_index: int,
    assigned_position: str,
) -> float:
    simulated_selected = set(selected)
    simulated_selected.add(player_index)
    simulated_remaining = {
        team_id: dict(remaining)
        for team_id, remaining in remaining_by_team.items()
    }
    simulated_remaining[team][assigned_position] -= 1
    if simulated_remaining[team][assigned_position] <= 0:
        return 0.0

    next_pick = next_pick_for_team(overall_pick, team, num_teams)
    if next_pick is None:
        return 0.0

    for simulated_pick in range(overall_pick + 1, next_pick):
        picking_team = team_for_pick(simulated_pick, num_teams)
        choice = choose_dg_pick(
            data=data,
            eligible_indices=eligible_indices,
            selected=simulated_selected,
            remaining=simulated_remaining[picking_team],
        )
        if choice is None:
            continue
        opponent_player, opponent_position = choice
        simulated_selected.add(opponent_player)
        simulated_remaining[picking_team][opponent_position] -= 1

    available = available_for_position(eligible_indices, simulated_selected, assigned_position)
    if not available:
        return 0.0
    return max(float(data.at[idx, "projected_points"]) for idx in available)


def next_pick_for_team(overall_pick: int, team: int, num_teams: int) -> int | None:
    total_picks = num_teams * sum(ROSTER_REQUIREMENTS.values())
    for candidate_pick in range(overall_pick + 1, total_picks + 1):
        if team_for_pick(candidate_pick, num_teams) == team:
            return candidate_pick
    return None


def build_eligible_indices(data: pd.DataFrame, positions: tuple[str, ...]) -> dict[str, list[int]]:
    return {
        position: [
            int(player_index)
            for player_index, row in data.iterrows()
            if eligible_for(row["eligible_positions"], position)
        ]
        for position in positions
    }


def available_for_position(
    eligible_indices: dict[str, list[int]],
    selected: set[int],
    position: str,
) -> list[int]:
    return [
        player_index
        for player_index in eligible_indices[position]
        if player_index not in selected
    ]


def summarize_competitive_rosters(
    *,
    rosters: pd.DataFrame,
    remaining_by_team: dict[int, dict[str, int]],
    num_teams: int,
    team_strategies: dict[int, str],
    scoring: str,
    season: int,
) -> pd.DataFrame:
    rows = []
    for team in range(1, num_teams + 1):
        team_roster = rosters.loc[rosters["team"] == team] if not rosters.empty else pd.DataFrame()
        strategy = team_strategies[team]
        rows.append(
            {
                "scoring": scoring,
                "season": season,
                "team": team,
                "strategy": strategy,
                "objective": float(team_roster["projected_points"].sum()) if not team_roster.empty else 0.0,
                "picks": len(team_roster),
                "status": "COMPLETE" if all(value == 0 for value in remaining_by_team[team].values()) else "INCOMPLETE",
                "remaining_slots": ";".join(
                    f"{position}:{need}"
                    for position, need in remaining_by_team[team].items()
                    if need
                ),
            }
        )
    return pd.DataFrame(rows).sort_values("objective", ascending=False)
