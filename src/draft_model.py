from __future__ import annotations

import pandas as pd

from src.draft_core import (
    DraftSolution,
    HITTER_POSITIONS,
    PITCHER_POSITIONS,
    POSITIONS,
    ROSTER_REQUIREMENTS,
    eligible_for,
    is_hitter,
    is_pitcher,
    load_players,
    snake_picks,
    summarize_solution,
)
from src.heuristics import solve_greedy, solve_opportunity_cost_greedy
from src.ip_model import solve_ilp


def solve_draft(
    method: str,
    players: pd.DataFrame,
    picks: list[int],
    *,
    season: int,
    draft_position: int,
    delta: float = 10.0,
    roster_requirements: dict[str, int] | None = None,
    enforce_adp: bool = True,
    time_limit: int = 120,
) -> DraftSolution:
    """Dispatch to an IP or heuristic draft solver by method name."""
    normalized = method.lower().replace("-", "_").replace(" ", "_")
    if normalized in {"ip", "ilp", "adp_aware_ilp", "optimal"}:
        return solve_ilp(
            players,
            picks,
            season=season,
            draft_position=draft_position,
            delta=delta,
            roster_requirements=roster_requirements,
            enforce_adp=enforce_adp,
            method_name="ADP-aware ILP",
            time_limit=time_limit,
        )
    if normalized in {"direct_greedy", "greedy", "bpa"}:
        return solve_greedy(
            players,
            picks,
            season=season,
            draft_position=draft_position,
            delta=delta,
            roster_requirements=roster_requirements,
            enforce_adp=enforce_adp,
        )
    if normalized in {"opportunity_cost_greedy", "opportunity_cost", "suffix_greedy"}:
        return solve_opportunity_cost_greedy(
            players,
            picks,
            season=season,
            draft_position=draft_position,
            delta=delta,
            roster_requirements=roster_requirements,
            enforce_adp=enforce_adp,
        )
    raise ValueError(f"Unknown draft method: {method}")


__all__ = [
    "DraftSolution",
    "HITTER_POSITIONS",
    "PITCHER_POSITIONS",
    "POSITIONS",
    "ROSTER_REQUIREMENTS",
    "eligible_for",
    "is_hitter",
    "is_pitcher",
    "load_players",
    "snake_picks",
    "solve_draft",
    "solve_greedy",
    "solve_ilp",
    "solve_opportunity_cost_greedy",
    "summarize_solution",
]
