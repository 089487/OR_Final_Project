from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

from src.draft_core import (
    DraftSolution,
    HITTER_POSITIONS,
    PITCHER_POSITIONS,
    ROSTER_REQUIREMENTS,
    eligible_for,
    is_hitter,
    is_pitcher,
)


HITTER_SLOT_ORDER = ("C", "1B", "2B", "3B", "SS", "OF", "OF", "OF", "Util")


@dataclass(frozen=True)
class FeasibilityState:
    hitter_dp: frozenset[int]
    sp_only: int = 0
    rp_only: int = 0
    p_flex: int = 0


@dataclass(frozen=True)
class FeasibilityConfig:
    hitter_slots: tuple[str, ...]
    slot_output_positions: tuple[str, ...]
    slot_bits_by_position: dict[str, int]
    hitter_capacity: int
    sp_capacity: int
    rp_capacity: int


def solve_greedy(
    players: pd.DataFrame,
    picks: list[int],
    *,
    season: int,
    draft_position: int,
    delta: float = 10.0,
    roster_requirements: dict[str, int] | None = None,
    enforce_adp: bool = True,
) -> DraftSolution:
    """Direct greedy: pick the highest-value currently available feasible player."""
    roster_requirements = dict(roster_requirements or ROSTER_REQUIREMENTS)
    config = build_feasibility_config(roster_requirements)
    data = players.sort_values("projected_points", ascending=False).reset_index(drop=True)
    selected: list[int] = []
    selected_set: set[int] = set()
    state = initial_state()
    rows: list[dict[str, object]] = []

    for round_idx, overall_pick in enumerate(picks):
        chosen_index = None
        chosen_state = None
        for i, row in data.iterrows():
            if i in selected_set:
                continue
            if enforce_adp and float(row["adp"]) + delta < overall_pick:
                continue
            next_state, _positions = try_add_player(state, row["eligible_positions"], config)
            if next_state is None:
                continue
            chosen_index = i
            chosen_state = next_state
            break

        if chosen_index is None or chosen_state is None:
            return _infeasible_solution("Direct Greedy", season, draft_position, delta, rows)

        selected.append(chosen_index)
        selected_set.add(chosen_index)
        state = chosen_state
        rows.append(make_roster_row(data.loc[chosen_index], season, "Direct Greedy", draft_position, round_idx, picks))

    refresh_final_assignments(rows, data, selected, config)
    roster = pd.DataFrame(rows)
    return DraftSolution(
        method="Direct Greedy",
        season=season,
        draft_position=draft_position,
        delta=delta,
        objective=float(roster["projected_points"].sum()),
        status="OPTIMAL",
        roster=roster,
    )


def solve_opportunity_cost_greedy(
    players: pd.DataFrame,
    picks: list[int],
    *,
    season: int,
    draft_position: int,
    delta: float = 10.0,
    roster_requirements: dict[str, int] | None = None,
    enforce_adp: bool = True,
) -> DraftSolution:
    """Choose expiring ADP-bucket player with largest points minus future positional best."""
    roster_requirements = dict(roster_requirements or ROSTER_REQUIREMENTS)
    config = build_feasibility_config(roster_requirements)
    data = players.reset_index(drop=True).copy()
    bucket_indices = build_adp_buckets(data, picks, delta)
    future_best = build_future_best_points(data, bucket_indices, picks, config)
    selected: list[int] = []
    selected_set: set[int] = set()
    state = initial_state()
    rows: list[dict[str, object]] = []
    current_can_choose = 0

    for round_idx, overall_pick in enumerate(picks):
        current_can_choose += 1

        while current_can_choose > 0:
            chosen = choose_opportunity_candidate(
                data=data,
                candidate_indices=bucket_indices[round_idx],
                selected_set=selected_set,
                state=state,
                config=config,
                future_best=future_best,
                round_idx=round_idx,
            )
            if chosen is None:
                break

            chosen_index, state = chosen
            selected.append(chosen_index)
            selected_set.add(chosen_index)
            current_can_choose -= 1
            rows.append(
                make_roster_row(
                    data.loc[chosen_index],
                    season,
                    "Opportunity Cost Greedy",
                    draft_position,
                    round_idx,
                    picks,
                )
            )

    if len(rows) < len(picks):
        return _infeasible_solution("Opportunity Cost Greedy", season, draft_position, delta, rows)

    refresh_final_assignments(rows, data, selected, config)
    roster = pd.DataFrame(rows)
    return DraftSolution(
        method="Opportunity Cost Greedy",
        season=season,
        draft_position=draft_position,
        delta=delta,
        objective=float(roster["projected_points"].sum()),
        status="OPTIMAL",
        roster=roster,
    )


def build_feasibility_config(roster_requirements: dict[str, int]) -> FeasibilityConfig:
    hitter_slots = []
    slot_output_positions = []
    for position in ("C", "1B", "2B", "3B", "SS", "OF", "Util"):
        for _ in range(roster_requirements.get(position, 0)):
            hitter_slots.append(position)
            slot_output_positions.append(position)

    slot_bits_by_position: dict[str, int] = {}
    for slot_index, position in enumerate(hitter_slots):
        slot_bits_by_position[position] = slot_bits_by_position.get(position, 0) | (1 << slot_index)

    return FeasibilityConfig(
        hitter_slots=tuple(hitter_slots),
        slot_output_positions=tuple(slot_output_positions),
        slot_bits_by_position=slot_bits_by_position,
        hitter_capacity=len(hitter_slots),
        sp_capacity=roster_requirements.get("SP", 0),
        rp_capacity=roster_requirements.get("RP", 0),
    )


def initial_state() -> FeasibilityState:
    return FeasibilityState(hitter_dp=frozenset({0}))


def try_add_player(
    state: FeasibilityState,
    player_positions: tuple[str, ...],
    config: FeasibilityConfig,
) -> tuple[FeasibilityState | None, set[str]]:
    if is_pitcher(player_positions) and not is_hitter(player_positions):
        return try_add_pitcher(state, player_positions, config)
    if is_hitter(player_positions):
        return try_add_hitter(state, player_positions, config)
    return None, set()


def try_add_hitter(
    state: FeasibilityState,
    player_positions: tuple[str, ...],
    config: FeasibilityConfig,
) -> tuple[FeasibilityState | None, set[str]]:
    player_mask = hitter_slot_mask(player_positions, config)
    if player_mask == 0:
        return None, set()

    new_masks: set[int] = set()
    added_positions: set[str] = set()
    for old_mask in state.hitter_dp:
        available = player_mask & ~old_mask
        while available:
            slot_bit = available & -available
            available -= slot_bit
            slot_index = slot_bit.bit_length() - 1
            new_masks.add(old_mask | slot_bit)
            added_positions.add(config.slot_output_positions[slot_index])

    if not new_masks:
        return None, set()
    return (
        FeasibilityState(
            hitter_dp=frozenset(new_masks),
            sp_only=state.sp_only,
            rp_only=state.rp_only,
            p_flex=state.p_flex,
        ),
        added_positions,
    )


def try_add_pitcher(
    state: FeasibilityState,
    player_positions: tuple[str, ...],
    config: FeasibilityConfig,
) -> tuple[FeasibilityState | None, set[str]]:
    can_sp = "SP" in player_positions
    can_rp = "RP" in player_positions
    sp_only = state.sp_only
    rp_only = state.rp_only
    p_flex = state.p_flex

    if can_sp and can_rp:
        p_flex += 1
        possible_positions = {"SP", "RP"}
    elif can_sp:
        sp_only += 1
        possible_positions = {"SP"}
    elif can_rp:
        rp_only += 1
        possible_positions = {"RP"}
    else:
        return None, set()

    total_pitchers = sp_only + rp_only + p_flex
    if sp_only > config.sp_capacity or rp_only > config.rp_capacity:
        return None, set()
    if total_pitchers > config.sp_capacity + config.rp_capacity:
        return None, set()

    open_positions = set()
    if sp_only + p_flex <= config.sp_capacity:
        open_positions.add("SP")
    if rp_only + p_flex <= config.rp_capacity:
        open_positions.add("RP")
    possible_positions &= open_positions or possible_positions
    return FeasibilityState(state.hitter_dp, sp_only, rp_only, p_flex), possible_positions


def hitter_slot_mask(player_positions: tuple[str, ...], config: FeasibilityConfig) -> int:
    positions = set(player_positions)
    mask = 0
    for position in HITTER_POSITIONS:
        if position in positions:
            mask |= config.slot_bits_by_position.get(position, 0)
    if is_hitter(player_positions):
        mask |= config.slot_bits_by_position.get("Util", 0)
    return mask


def build_adp_buckets(data: pd.DataFrame, picks: list[int], delta: float) -> list[list[int]]:
    buckets = [[] for _ in picks]
    for i, row in data.iterrows():
        availability = float(row["adp"]) + delta
        for round_idx, current_pick in enumerate(picks):
            next_pick = picks[round_idx + 1] if round_idx + 1 < len(picks) else float("inf")
            if current_pick <= availability < next_pick:
                buckets[round_idx].append(i)
                break
    return buckets


def build_future_best_points(
    data: pd.DataFrame,
    buckets: list[list[int]],
    picks: list[int],
    config: FeasibilityConfig,
) -> dict[str, list[float]]:
    positions = ("C", "1B", "2B", "3B", "SS", "OF", "Util", "SP", "RP")
    best_in_round = {position: [0.0] * len(picks) for position in positions}
    for round_idx, bucket in enumerate(buckets):
        for player_index in bucket:
            row = data.loc[player_index]
            points = float(row["projected_points"])
            for position in possible_output_positions(row["eligible_positions"], config):
                best_in_round[position][round_idx] = max(best_in_round[position][round_idx], points)

    suffix = {position: [0.0] * (len(picks) + 1) for position in positions}
    for position in positions:
        for round_idx in reversed(range(len(picks))):
            suffix[position][round_idx] = max(
                suffix[position][round_idx + 1],
                best_in_round[position][round_idx],
            )
    return suffix


def possible_output_positions(player_positions: tuple[str, ...], config: FeasibilityConfig) -> set[str]:
    state = initial_state()
    _next_state, positions = try_add_player(state, player_positions, config)
    return positions


def choose_opportunity_candidate(
    *,
    data: pd.DataFrame,
    candidate_indices: list[int],
    selected_set: set[int],
    state: FeasibilityState,
    config: FeasibilityConfig,
    future_best: dict[str, list[float]],
    round_idx: int,
) -> tuple[int, FeasibilityState] | None:
    best_choice = None
    best_score = float("-inf")
    best_points = float("-inf")
    for player_index in candidate_indices:
        if player_index in selected_set:
            continue
        row = data.loc[player_index]
        next_state, positions = try_add_player(state, row["eligible_positions"], config)
        if next_state is None:
            continue
        points = float(row["projected_points"])
        replacement = max(
            (points - future_best[position][round_idx + 1] for position in positions),
            default=float("-inf"),
        )
        if (replacement, points) > (best_score, best_points):
            best_choice = (player_index, next_state)
            best_score = replacement
            best_points = points
    if best_score < 0:
        return None
    return best_choice


def choose_direct_candidate(
    *,
    data: pd.DataFrame,
    selected_set: set[int],
    state: FeasibilityState,
    config: FeasibilityConfig,
    current_pick: int,
    delta: float,
    enforce_adp: bool,
) -> tuple[int, FeasibilityState] | None:
    for player_index, row in data.sort_values("projected_points", ascending=False).iterrows():
        if player_index in selected_set:
            continue
        if enforce_adp and float(row["adp"]) + delta < current_pick:
            continue
        next_state, _positions = try_add_player(state, row["eligible_positions"], config)
        if next_state is not None:
            return player_index, next_state
    return None


def refresh_final_assignments(
    rows: list[dict[str, object]],
    data: pd.DataFrame,
    selected: list[int],
    config: FeasibilityConfig,
) -> None:
    assignment = reconstruct_assignment(data, selected, config)
    for row in rows:
        player_index = row.pop("_player_index")
        row["assigned_position"] = assignment.get(player_index, row["assigned_position"])


def reconstruct_assignment(
    data: pd.DataFrame,
    selected: list[int],
    config: FeasibilityConfig,
) -> dict[int, str]:
    hitter_indices = [i for i in selected if is_hitter(data.at[i, "eligible_positions"])]
    pitcher_indices = [i for i in selected if is_pitcher(data.at[i, "eligible_positions"]) and not is_hitter(data.at[i, "eligible_positions"])]
    assignment = reconstruct_hitter_assignment(data, hitter_indices, config)
    assignment.update(reconstruct_pitcher_assignment(data, pitcher_indices, config))
    return assignment


def reconstruct_hitter_assignment(
    data: pd.DataFrame,
    hitter_indices: list[int],
    config: FeasibilityConfig,
) -> dict[int, str]:
    parents: list[dict[int, tuple[int, int]]] = [{0: (-1, -1)}]
    for player_index in hitter_indices:
        prev = parents[-1]
        current: dict[int, tuple[int, int]] = {}
        player_mask = hitter_slot_mask(data.at[player_index, "eligible_positions"], config)
        for old_mask in prev:
            available = player_mask & ~old_mask
            while available:
                slot_bit = available & -available
                available -= slot_bit
                new_mask = old_mask | slot_bit
                current.setdefault(new_mask, (old_mask, slot_bit))
        parents.append(current)

    if not parents[-1]:
        return {}
    final_mask = next(iter(parents[-1]))
    assignment: dict[int, str] = {}
    for level in range(len(hitter_indices), 0, -1):
        old_mask, slot_bit = parents[level][final_mask]
        slot_index = slot_bit.bit_length() - 1
        assignment[hitter_indices[level - 1]] = config.slot_output_positions[slot_index]
        final_mask = old_mask
    return assignment


def reconstruct_pitcher_assignment(
    data: pd.DataFrame,
    pitcher_indices: list[int],
    config: FeasibilityConfig,
) -> dict[int, str]:
    assignment: dict[int, str] = {}
    flex = []
    sp_left = config.sp_capacity
    rp_left = config.rp_capacity
    for player_index in pitcher_indices:
        positions = set(data.at[player_index, "eligible_positions"])
        if "SP" in positions and "RP" in positions:
            flex.append(player_index)
        elif "SP" in positions:
            assignment[player_index] = "SP"
            sp_left -= 1
        elif "RP" in positions:
            assignment[player_index] = "RP"
            rp_left -= 1

    for player_index in flex:
        if sp_left > 0:
            assignment[player_index] = "SP"
            sp_left -= 1
        elif rp_left > 0:
            assignment[player_index] = "RP"
            rp_left -= 1
    return assignment


def make_roster_row(
    row: pd.Series,
    season: int,
    method: str,
    draft_position: int,
    round_idx: int,
    picks: list[int],
) -> dict[str, object]:
    return {
        "_player_index": int(row.name),
        "season": season,
        "method": method,
        "draft_position": draft_position,
        "round": round_idx + 1,
        "overall_pick": picks[round_idx],
        "player": row["player"],
        "projected_points": float(row["projected_points"]),
        "adp": float(row["adp"]),
        "eligible_positions": ";".join(row["eligible_positions"]),
        "assigned_position": "",
    }


def _infeasible_solution(
    method: str,
    season: int,
    draft_position: int,
    delta: float,
    rows: list[dict[str, object]],
) -> DraftSolution:
    clean_rows = [{k: v for k, v in row.items() if k != "_player_index"} for row in rows]
    return DraftSolution(
        method=method,
        season=season,
        draft_position=draft_position,
        delta=delta,
        objective=float("nan"),
        status="INFEASIBLE",
        roster=pd.DataFrame(clean_rows),
    )
