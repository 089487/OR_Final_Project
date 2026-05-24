from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

import pandas as pd


ROSTER_REQUIREMENTS: dict[str, int] = {
    "C": 1,
    "1B": 1,
    "2B": 1,
    "3B": 1,
    "SS": 1,
    "OF": 3,
    "Util": 1,
    "SP": 5,
    "RP": 2,
}

POSITIONS = tuple(ROSTER_REQUIREMENTS)
HITTER_POSITIONS = {"C", "1B", "2B", "3B", "SS", "OF"}
PITCHER_POSITIONS = {"SP", "RP"}


@dataclass(frozen=True)
class DraftSolution:
    method: str
    season: int
    draft_position: int
    delta: float
    objective: float
    status: str
    roster: pd.DataFrame
    shadow_prices: pd.DataFrame | None = None


def snake_picks(num_teams: int, draft_position: int, rounds: int) -> list[int]:
    """Return the overall pick numbers owned by one manager in a snake draft."""
    if not 1 <= draft_position <= num_teams:
        raise ValueError("draft_position must be between 1 and num_teams")

    picks = []
    for round_number in range(1, rounds + 1):
        if round_number % 2 == 1:
            picks.append((round_number - 1) * num_teams + draft_position)
        else:
            picks.append(round_number * num_teams - draft_position + 1)
    return picks


def load_players(path: str | Path) -> pd.DataFrame:
    """Load and validate the project player CSV format."""
    players = pd.read_csv(path)
    players = players.rename(
        columns={
            "player_name": "player",
            "points": "projected_points",
        }
    )
    if "season" not in players.columns:
        players["season"] = 2026

    required = {"season", "player", "projected_points", "adp", "eligible_positions"}
    missing = required - set(players.columns)
    if missing:
        raise ValueError(f"Missing required columns: {sorted(missing)}")

    players = players.copy()
    players["projected_points"] = pd.to_numeric(players["projected_points"])
    players["adp"] = pd.to_numeric(players["adp"])
    players["eligible_positions"] = players["eligible_positions"].map(_normalize_positions)
    return players


def _normalize_positions(value: str | Iterable[str]) -> tuple[str, ...]:
    if isinstance(value, str):
        raw_positions = [part.strip() for part in value.replace("/", ";").split(";")]
    else:
        raw_positions = [str(part).strip() for part in value]

    positions = []
    for pos in raw_positions:
        if not pos:
            continue
        if pos == "P":
            positions.extend(["SP", "RP"])
        else:
            positions.append(pos)

    unknown = set(positions) - set(POSITIONS)
    if unknown:
        raise ValueError(f"Unknown position(s): {sorted(unknown)}")
    return tuple(dict.fromkeys(positions))


def eligible_for(player_positions: Iterable[str], roster_position: str) -> bool:
    positions = set(player_positions)
    if roster_position == "Util":
        return bool(positions & HITTER_POSITIONS) or "Util" in positions
    return roster_position in positions


def is_hitter(player_positions: Iterable[str]) -> bool:
    positions = set(player_positions)
    return bool(positions & HITTER_POSITIONS) or "Util" in positions


def is_pitcher(player_positions: Iterable[str]) -> bool:
    return bool(set(player_positions) & PITCHER_POSITIONS)


def summarize_solution(solution: DraftSolution) -> dict[str, object]:
    return {
        "season": solution.season,
        "method": solution.method,
        "draft_position": solution.draft_position,
        "delta": solution.delta,
        "objective": solution.objective,
        "status": solution.status,
    }
