from __future__ import annotations

import heapq
from time import perf_counter

import pandas as pd

from src.draft_core import DraftSolution, ROSTER_REQUIREMENTS, eligible_for


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
    """Direct greedy: fill the scarcest open position with its best available player."""
    start_time = perf_counter()
    roster_requirements = dict(roster_requirements or ROSTER_REQUIREMENTS)
    positions = tuple(roster_requirements)
    data = players.reset_index(drop=True).copy()
    data["_expiration"] = data["adp"].astype(float) + float(delta)
    eligible_positions_by_player = build_eligible_positions_by_player(data, positions)
    heaps = build_position_heaps(data, eligible_positions_by_player, positions)
    active_count = {
        position: sum(position in player_positions for player_positions in eligible_positions_by_player)
        for position in positions
    }
    alive = [True] * len(data)
    selected = [False] * len(data)
    expiration_order = build_expiration_order(data, delta)
    expire_ptr = 0
    remaining = dict(roster_requirements)
    rows: list[dict[str, object]] = []

    for round_idx, overall_pick in enumerate(picks):
        if enforce_adp:
            expire_ptr = expire_players(
                expiration_order=expiration_order,
                expire_ptr=expire_ptr,
                current_pick=overall_pick,
                alive=alive,
                selected=selected,
                active_count=active_count,
                eligible_positions_by_player=eligible_positions_by_player,
            )
        choice = choose_direct_position_and_player(
            data=data,
            heaps=heaps,
            alive=alive,
            selected=selected,
            active_count=active_count,
            remaining=remaining,
        )
        if choice is None:
            return _infeasible_solution("Direct Greedy", season, draft_position, delta, rows, perf_counter() - start_time)

        player_index, assigned_position = choice
        mark_selected(
            player_index=player_index,
            alive=alive,
            selected=selected,
            active_count=active_count,
            eligible_positions_by_player=eligible_positions_by_player,
        )
        remaining[assigned_position] -= 1
        rows.append(
            make_roster_row(
                data.loc[player_index],
                season,
                "Direct Greedy",
                draft_position,
                round_idx,
                picks,
                assigned_position,
            )
        )

    roster = pd.DataFrame(rows)
    return DraftSolution(
        method="Direct Greedy",
        season=season,
        draft_position=draft_position,
        delta=delta,
        objective=float(roster["projected_points"].sum()),
        status="OPTIMAL",
        roster=roster,
        runtime_seconds=perf_counter() - start_time,
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
    """Choose expiring ADP-bucket player-position pair with largest opportunity cost."""
    start_time = perf_counter()
    roster_requirements = dict(roster_requirements or ROSTER_REQUIREMENTS)
    positions = tuple(roster_requirements)
    data = players.reset_index(drop=True).copy()
    data["_expiration"] = data["adp"].astype(float) + float(delta)
    eligible_positions_by_player = build_eligible_positions_by_player(data, positions)
    current_heaps = build_position_heaps(data, eligible_positions_by_player, positions)
    future_heaps = build_position_heaps(data, eligible_positions_by_player, positions)
    current_alive = [True] * len(data)
    future_alive = [True] * len(data)
    current_count = {
        position: sum(position in player_positions for player_positions in eligible_positions_by_player)
        for position in positions
    }
    future_count = dict(current_count)
    expiration_order = build_expiration_order(data, delta)
    current_expire_ptr = 0
    future_expire_ptr = 0
    selected = [False] * len(data)
    remaining = dict(roster_requirements)
    rows: list[dict[str, object]] = []
    current_can_choose = 0

    for round_idx, current_pick in enumerate(picks):
        next_pick = picks[round_idx + 1] if round_idx + 1 < len(picks) else float("inf")
        current_can_choose += 1
        if enforce_adp:
            current_expire_ptr = expire_players(
                expiration_order=expiration_order,
                expire_ptr=current_expire_ptr,
                current_pick=current_pick,
                alive=current_alive,
                selected=selected,
                active_count=current_count,
                eligible_positions_by_player=eligible_positions_by_player,
            )
            future_expire_ptr = expire_players(
                expiration_order=expiration_order,
                expire_ptr=future_expire_ptr,
                current_pick=next_pick,
                alive=future_alive,
                selected=selected,
                active_count=future_count,
                eligible_positions_by_player=eligible_positions_by_player,
            )

        while current_can_choose > 0:
            choice = choose_opportunity_candidate(
                data=data,
                current_heaps=current_heaps,
                future_heaps=future_heaps,
                selected=selected,
                remaining=remaining,
                current_count=current_count,
                future_count=future_count,
                current_pick=current_pick if enforce_adp else float("-inf"),
                next_pick=next_pick if enforce_adp else float("-inf"),
            )
            if choice is None:
                break

            player_index, assigned_position = choice
            mark_selected(
                player_index=player_index,
                alive=current_alive,
                selected=selected,
                active_count=current_count,
                eligible_positions_by_player=eligible_positions_by_player,
            )
            mark_selected_if_alive(
                player_index=player_index,
                alive=future_alive,
                active_count=future_count,
                eligible_positions_by_player=eligible_positions_by_player,
            )
            remaining[assigned_position] -= 1
            current_can_choose -= 1
            rows.append(
                make_roster_row(
                    data.loc[player_index],
                    season,
                    "Opportunity Cost Greedy",
                    draft_position,
                    round_idx,
                    picks,
                    assigned_position,
                )
            )

    if len(rows) < len(picks):
        return _infeasible_solution("Opportunity Cost Greedy", season, draft_position, delta, rows, perf_counter() - start_time)

    roster = pd.DataFrame(rows)
    return DraftSolution(
        method="Opportunity Cost Greedy",
        season=season,
        draft_position=draft_position,
        delta=delta,
        objective=float(roster["projected_points"].sum()),
        status="OPTIMAL",
        roster=roster,
        runtime_seconds=perf_counter() - start_time,
    )


def choose_direct_position_and_player(
    *,
    data: pd.DataFrame,
    heaps: dict[str, list[tuple[float, int]]],
    alive: list[bool],
    selected: list[bool],
    active_count: dict[str, int],
    remaining: dict[str, int],
) -> tuple[int, str] | None:
    candidate_positions = []
    for position, need in remaining.items():
        if need <= 0:
            continue
        if active_count[position] <= 0:
            continue
        clean_heap(heaps[position], alive=alive, selected=selected)
        if not heaps[position]:
            continue
        points = -heaps[position][0][0]
        candidate_positions.append((position, points))
    if not candidate_positions:
        return None

    assigned_position, _points = max(
        candidate_positions,
        key=lambda item: (
            remaining[item[0]] / active_count[item[0]],
            item[1],
        ),
    )
    player_index = heaps[assigned_position][0][1]
    return player_index, assigned_position


def choose_opportunity_candidate(
    *,
    data: pd.DataFrame,
    current_heaps: dict[str, list[tuple[float, int]]],
    future_heaps: dict[str, list[tuple[float, int]]],
    selected: list[bool],
    remaining: dict[str, int],
    current_count: dict[str, int],
    future_count: dict[str, int],
    current_pick: float,
    next_pick: float,
) -> tuple[int, str] | None:
    best_choice = None
    best_priority: tuple[float, float, float] | None = None
    should_pick = False
    fallback_choice = None
    fallback_priority: tuple[float, float] | None = None
    for position, need in remaining.items():
        if need <= 0:
            continue
        if current_count[position] <= 0:
            continue
        clean_heap_by_pick(current_heaps[position], data=data, selected=selected, threshold=current_pick)
        if not current_heaps[position]:
            continue
        clean_heap_by_pick(future_heaps[position], data=data, selected=selected, threshold=next_pick)

        current_points = -current_heaps[position][0][0]
        current_player = current_heaps[position][0][1]
        future_points = -future_heaps[position][0][0] if future_heaps[position] else 0.0
        score = current_points - future_points
        scarcity_priority = (need / current_count[position], current_points)
        if fallback_priority is None or scarcity_priority > fallback_priority:
            fallback_choice = (current_player, position)
            fallback_priority = scarcity_priority
        forced = current_count[position] <= need or future_count[position] < need
        if forced:
            priority = (1.0, need / current_count[position], current_points)
        else:
            priority = (0.0, score, current_points)
        if best_priority is None or priority > best_priority:
            best_choice = (current_player, position)
            best_priority = priority
            should_pick = forced or score > 0

    if not should_pick:
        return fallback_choice
    return best_choice


def build_eligible_positions_by_player(data: pd.DataFrame, positions: tuple[str, ...]) -> list[tuple[str, ...]]:
    return [
        tuple(position for position in positions if eligible_for(row["eligible_positions"], position))
        for _player_index, row in data.iterrows()
    ]


def build_position_heaps(
    data: pd.DataFrame,
    eligible_positions_by_player: list[tuple[str, ...]],
    positions: tuple[str, ...],
) -> dict[str, list[tuple[float, int]]]:
    heaps = {position: [] for position in positions}
    for player_index, player_positions in enumerate(eligible_positions_by_player):
        points = -float(data.at[player_index, "projected_points"])
        for position in player_positions:
            heaps[position].append((points, player_index))
    for heap in heaps.values():
        heapq.heapify(heap)
    return heaps


def build_expiration_order(data: pd.DataFrame, delta: float) -> list[tuple[float, int]]:
    return sorted(
        (float(row["adp"]) + delta, int(player_index))
        for player_index, row in data.iterrows()
    )


def expire_players(
    *,
    expiration_order: list[tuple[float, int]],
    expire_ptr: int,
    current_pick: float,
    alive: list[bool],
    selected: list[bool],
    active_count: dict[str, int],
    eligible_positions_by_player: list[tuple[str, ...]],
) -> int:
    while expire_ptr < len(expiration_order) and expiration_order[expire_ptr][0] < current_pick:
        _expiration, player_index = expiration_order[expire_ptr]
        if alive[player_index] and not selected[player_index]:
            alive[player_index] = False
            for position in eligible_positions_by_player[player_index]:
                active_count[position] -= 1
        expire_ptr += 1
    return expire_ptr


def mark_selected(
    *,
    player_index: int,
    alive: list[bool],
    selected: list[bool],
    active_count: dict[str, int],
    eligible_positions_by_player: list[tuple[str, ...]],
) -> None:
    selected[player_index] = True
    if not alive[player_index]:
        return
    alive[player_index] = False
    for position in eligible_positions_by_player[player_index]:
        active_count[position] -= 1


def mark_selected_if_alive(
    *,
    player_index: int,
    alive: list[bool],
    active_count: dict[str, int],
    eligible_positions_by_player: list[tuple[str, ...]],
) -> None:
    if not alive[player_index]:
        return
    alive[player_index] = False
    for position in eligible_positions_by_player[player_index]:
        active_count[position] -= 1


def clean_heap(
    heap: list[tuple[float, int]],
    *,
    alive: list[bool],
    selected: list[bool],
) -> None:
    while heap and (selected[heap[0][1]] or not alive[heap[0][1]]):
        heapq.heappop(heap)


def clean_heap_by_pick(
    heap: list[tuple[float, int]],
    *,
    data: pd.DataFrame,
    selected: list[bool],
    threshold: float,
) -> None:
    while heap:
        player_index = heap[0][1]
        if selected[player_index] or float(data.at[player_index, "_expiration"]) < threshold:
            heapq.heappop(heap)
            continue
        break


def make_roster_row(
    row: pd.Series,
    season: int,
    method: str,
    draft_position: int,
    round_idx: int,
    picks: list[int],
    assigned_position: str,
) -> dict[str, object]:
    return {
        "season": season,
        "method": method,
        "draft_position": draft_position,
        "round": round_idx + 1,
        "overall_pick": picks[round_idx],
        "player": row["player"],
        "projected_points": float(row["projected_points"]),
        "adp": float(row["adp"]),
        "eligible_positions": ";".join(row["eligible_positions"]),
        "assigned_position": assigned_position,
    }


def _infeasible_solution(
    method: str,
    season: int,
    draft_position: int,
    delta: float,
    rows: list[dict[str, object]],
    runtime_seconds: float | None = None,
) -> DraftSolution:
    return DraftSolution(
        method=method,
        season=season,
        draft_position=draft_position,
        delta=delta,
        objective=float("nan"),
        status="INFEASIBLE",
        roster=pd.DataFrame(rows),
        runtime_seconds=runtime_seconds,
    )
