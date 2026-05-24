from __future__ import annotations

import gurobipy as gp
import pandas as pd
from gurobipy import GRB

from src.draft_core import DraftSolution, ROSTER_REQUIREMENTS, eligible_for


def solve_ilp(
    players: pd.DataFrame,
    picks: list[int],
    *,
    season: int,
    draft_position: int,
    delta: float = 10.0,
    roster_requirements: dict[str, int] | None = None,
    enforce_adp: bool = True,
    relax: bool = False,
    method_name: str | None = None,
    time_limit: int = 120,
) -> DraftSolution:
    """Solve the ADP-aware or static roster optimization model with Gurobi."""
    roster_requirements = roster_requirements or ROSTER_REQUIREMENTS
    positions = tuple(roster_requirements)
    if sum(roster_requirements.values()) != len(picks):
        raise ValueError("Number of draft picks must equal required roster size")

    data = players.reset_index(drop=True).copy()
    indices = list(data.index)
    vtype = GRB.CONTINUOUS if relax else GRB.BINARY
    model = gp.Model("fantasy_baseball_draft")
    model.Params.OutputFlag = 0
    model.Params.TimeLimit = time_limit

    y = model.addVars(indices, lb=0.0, ub=1.0, vtype=vtype, name="drafted")
    x = model.addVars(indices, positions, lb=0.0, ub=1.0, vtype=vtype, name="assign")
    z = model.addVars(indices, range(len(picks)), lb=0.0, ub=1.0, vtype=vtype, name="pick")

    model.setObjective(
        gp.quicksum(float(data.at[i, "projected_points"]) * y[i] for i in indices),
        GRB.MAXIMIZE,
    )

    for pick_idx in range(len(picks)):
        model.addConstr(
            gp.quicksum(z[i, pick_idx] for i in indices) == 1,
            name=f"one_player_pick_{pick_idx + 1}",
        )

    for i in indices:
        model.addConstr(
            gp.quicksum(z[i, pick_idx] for pick_idx in range(len(picks))) == y[i],
            name=f"link_pick_player_{i}",
        )
        model.addConstr(
            gp.quicksum(x[i, pos] for pos in positions) == y[i],
            name=f"one_position_{i}",
        )
        for pos in positions:
            if not eligible_for(data.at[i, "eligible_positions"], pos):
                model.addConstr(x[i, pos] == 0, name=f"ineligible_{i}_{pos}")

    for pos, required_count in roster_requirements.items():
        model.addConstr(
            gp.quicksum(x[i, pos] for i in indices) == required_count,
            name=f"roster_{pos}",
        )

    if enforce_adp:
        for i in indices:
            adp = float(data.at[i, "adp"])
            for pick_idx, overall_pick in enumerate(picks):
                if adp + delta < overall_pick:
                    model.addConstr(z[i, pick_idx] == 0, name=f"unavailable_{i}_{pick_idx}")

    model.optimize()
    status = _status_name(model.Status)
    if model.Status not in (GRB.OPTIMAL, GRB.TIME_LIMIT, GRB.SUBOPTIMAL):
        return DraftSolution(
            method=method_name or ("ADP ILP" if enforce_adp else "Static IP"),
            season=season,
            draft_position=draft_position,
            delta=delta,
            objective=float("nan"),
            status=status,
            roster=pd.DataFrame(),
        )

    rows = []
    for i in indices:
        if y[i].X > 0.5:
            assigned_position = max(positions, key=lambda pos: x[i, pos].X)
            pick_idx = max(range(len(picks)), key=lambda idx: z[i, idx].X)
            rows.append(
                {
                    "season": season,
                    "method": method_name or ("ADP ILP" if enforce_adp else "Static IP"),
                    "draft_position": draft_position,
                    "round": pick_idx + 1,
                    "overall_pick": picks[pick_idx],
                    "player": data.at[i, "player"],
                    "projected_points": float(data.at[i, "projected_points"]),
                    "adp": float(data.at[i, "adp"]),
                    "eligible_positions": ";".join(data.at[i, "eligible_positions"]),
                    "assigned_position": assigned_position,
                }
            )

    roster = pd.DataFrame(rows).sort_values("round").reset_index(drop=True)
    shadow_prices = None
    if relax and model.Status == GRB.OPTIMAL:
        shadow_prices = pd.DataFrame(
            [
                {"position": pos, "shadow_price": model.getConstrByName(f"roster_{pos}").Pi}
                for pos in positions
            ]
        )

    return DraftSolution(
        method=method_name or ("ADP ILP" if enforce_adp else "Static IP"),
        season=season,
        draft_position=draft_position,
        delta=delta,
        objective=float(model.ObjVal),
        status=status,
        roster=roster,
        shadow_prices=shadow_prices,
    )


def _status_name(status_code: int) -> str:
    status_map = {
        GRB.LOADED: "LOADED",
        GRB.OPTIMAL: "OPTIMAL",
        GRB.INFEASIBLE: "INFEASIBLE",
        GRB.INF_OR_UNBD: "INF_OR_UNBD",
        GRB.UNBOUNDED: "UNBOUNDED",
        GRB.CUTOFF: "CUTOFF",
        GRB.ITERATION_LIMIT: "ITERATION_LIMIT",
        GRB.NODE_LIMIT: "NODE_LIMIT",
        GRB.TIME_LIMIT: "TIME_LIMIT",
        GRB.SOLUTION_LIMIT: "SOLUTION_LIMIT",
        GRB.INTERRUPTED: "INTERRUPTED",
        GRB.NUMERIC: "NUMERIC",
        GRB.SUBOPTIMAL: "SUBOPTIMAL",
    }
    return status_map.get(status_code, f"STATUS_{status_code}")
