from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd

from src.draft_core import ROSTER_REQUIREMENTS


MIN_POINTS = 10.0
MAX_POINTS = 800.0
HITTER_SINGLE_POSITIONS = ("C", "1B", "2B", "3B", "SS", "OF")
PITCHER_SINGLE_POSITIONS = ("SP", "RP")
HITTER_PATTERNS = (
    "C",
    "1B",
    "2B",
    "3B",
    "SS",
    "OF",
    "1B;3B",
    "2B;SS",
    "2B;3B",
    "3B;SS",
    "1B;OF",
    "OF;Util",
)
PITCHER_PATTERNS = ("SP", "RP", "SP;RP")
MULTI_HITTER_PATTERNS_2 = ("1B;3B", "2B;SS", "2B;3B", "3B;SS", "1B;OF", "OF;Util")
MULTI_HITTER_PATTERNS_3 = ("1B;3B;OF", "2B;SS;3B")


@dataclass(frozen=True)
class SyntheticConfig:
    points_scenario: str = "normal"
    position_scenario: str = "roster_ratio"
    roster_scale: int = 1
    num_teams: int = 12
    player_demand_ratio: int = 3
    sigma_adp: float = 30.0
    seed: int = 0
    season: int = 9999


def scale_roster_requirements(
    base_requirements: dict[str, int] | None = None,
    scale: int = 1,
) -> dict[str, int]:
    if scale < 1:
        raise ValueError("roster scale must be >= 1")
    base = base_requirements or ROSTER_REQUIREMENTS
    return {position: int(count) * scale for position, count in base.items()}


def generate_synthetic_players(config: SyntheticConfig) -> pd.DataFrame:
    roster_requirements = scale_roster_requirements(scale=config.roster_scale)
    roster_size = sum(roster_requirements.values())
    total_draft_demand = roster_size * config.num_teams
    n_players = total_draft_demand * config.player_demand_ratio
    rng = np.random.default_rng(config.seed)

    points = generate_points(n_players, config.points_scenario, rng)
    positions = generate_positions(points, config.position_scenario, roster_requirements, rng)
    adp = generate_adp(points, config.sigma_adp, rng)

    return pd.DataFrame(
        {
            "season": config.season,
            "player": [f"SYN_{config.seed:03d}_{i + 1:06d}" for i in range(n_players)],
            "projected_points": np.round(points, 2),
            "adp": np.round(adp, 2),
            "eligible_positions": positions,
        }
    )


def generate_points(n_players: int, scenario: str, rng: np.random.Generator) -> np.ndarray:
    normalized = _normalize_name(scenario)
    if normalized == "normal":
        points = rng.normal(400.0, 120.0, size=n_players)
    elif normalized == "uniform":
        points = rng.uniform(MIN_POINTS, MAX_POINTS, size=n_players)
    elif normalized in {"high_low", "highlow"}:
        is_high = rng.random(n_players) < 0.1
        points = np.empty(n_players)
        points[is_high] = rng.uniform(500.0, MAX_POINTS, size=int(is_high.sum()))
        points[~is_high] = rng.uniform(MIN_POINTS, 500.0, size=int((~is_high).sum()))
    else:
        raise ValueError(f"Unknown points scenario: {scenario}")
    return np.clip(points, MIN_POINTS, MAX_POINTS)


def generate_positions(
    points: np.ndarray,
    scenario: str,
    roster_requirements: dict[str, int],
    rng: np.random.Generator,
) -> list[str]:
    normalized = _normalize_name(scenario)
    n_players = len(points)
    if normalized == "uniform_by_type":
        return _generate_uniform_by_type(n_players, roster_requirements, rng)
    if normalized == "point_flexible":
        return _generate_point_flexible(points, roster_requirements, rng)
    if normalized == "single_position":
        return _generate_single_position(n_players, roster_requirements, rng)
    if normalized == "roster_ratio":
        return _generate_roster_ratio(n_players, roster_requirements, rng)
    raise ValueError(f"Unknown position scenario: {scenario}")


def generate_adp(points: np.ndarray, sigma_adp: float, rng: np.random.Generator) -> np.ndarray:
    order = np.argsort(-points, kind="mergesort")
    true_rank = np.empty(len(points), dtype=float)
    true_rank[order] = np.arange(1, len(points) + 1, dtype=float)
    adp = true_rank + rng.normal(0.0, sigma_adp, size=len(points))
    return np.clip(adp, 1.0, float(len(points)))


def write_synthetic_players(players: pd.DataFrame, path: str | Path) -> None:
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    players.to_csv(output, index=False)


def metadata_row(config: SyntheticConfig, players: pd.DataFrame) -> dict[str, object]:
    roster_requirements = scale_roster_requirements(scale=config.roster_scale)
    roster_size = sum(roster_requirements.values())
    return {
        "points_scenario": config.points_scenario,
        "position_scenario": config.position_scenario,
        "roster_scale": config.roster_scale,
        "num_teams": config.num_teams,
        "roster_size": roster_size,
        "total_draft_demand": roster_size * config.num_teams,
        "player_demand_ratio": config.player_demand_ratio,
        "num_players": len(players),
        "sigma_adp": config.sigma_adp,
        "seed": config.seed,
        "season": config.season,
    }


def _generate_uniform_by_type(
    n_players: int,
    roster_requirements: dict[str, int],
    rng: np.random.Generator,
) -> list[str]:
    is_hitter = _sample_is_hitter(n_players, roster_requirements, rng)
    positions = []
    for hitter in is_hitter:
        if hitter:
            positions.append(str(rng.choice(HITTER_PATTERNS)))
        else:
            positions.append(str(rng.choice(PITCHER_PATTERNS)))
    return positions


def _generate_point_flexible(
    points: np.ndarray,
    roster_requirements: dict[str, int],
    rng: np.random.Generator,
) -> list[str]:
    n_players = len(points)
    is_hitter = _sample_is_hitter(n_players, roster_requirements, rng)
    ranks = pd.Series(points).rank(method="first", ascending=False).to_numpy()
    percentiles = ranks / n_players
    positions: list[str] = []
    for percentile, hitter in zip(percentiles, is_hitter, strict=True):
        if hitter:
            positions.append(_sample_point_flexible_hitter(float(percentile), rng))
        else:
            positions.append(_sample_point_flexible_pitcher(float(percentile), rng))
    return positions


def _generate_single_position(
    n_players: int,
    roster_requirements: dict[str, int],
    rng: np.random.Generator,
) -> list[str]:
    is_hitter = _sample_is_hitter(n_players, roster_requirements, rng)
    positions = []
    for hitter in is_hitter:
        if hitter:
            positions.append(str(rng.choice(HITTER_SINGLE_POSITIONS)))
        else:
            positions.append(str(rng.choice(PITCHER_SINGLE_POSITIONS)))
    return positions


def _generate_roster_ratio(
    n_players: int,
    roster_requirements: dict[str, int],
    rng: np.random.Generator,
) -> list[str]:
    weights_by_position = {
        "C": roster_requirements.get("C", 0),
        "1B": roster_requirements.get("1B", 0),
        "2B": roster_requirements.get("2B", 0),
        "3B": roster_requirements.get("3B", 0),
        "SS": roster_requirements.get("SS", 0),
        "OF": roster_requirements.get("OF", 0),
        "SP": roster_requirements.get("SP", 0),
        "RP": roster_requirements.get("RP", 0),
    }
    positions = tuple(weights_by_position)
    weights = np.array([weights_by_position[position] for position in positions], dtype=float)
    probabilities = weights / weights.sum()
    return [str(position) for position in rng.choice(positions, size=n_players, p=probabilities)]


def _sample_is_hitter(
    n_players: int,
    roster_requirements: dict[str, int],
    rng: np.random.Generator,
) -> np.ndarray:
    hitter_slots = sum(roster_requirements.get(pos, 0) for pos in ("C", "1B", "2B", "3B", "SS", "OF", "Util"))
    pitcher_slots = sum(roster_requirements.get(pos, 0) for pos in ("SP", "RP"))
    hitter_probability = hitter_slots / (hitter_slots + pitcher_slots)
    return rng.random(n_players) < hitter_probability


def _sample_point_flexible_hitter(percentile: float, rng: np.random.Generator) -> str:
    if percentile <= 0.2:
        count = int(rng.choice((1, 2, 3), p=(0.2, 0.5, 0.3)))
    elif percentile <= 0.7:
        count = int(rng.choice((1, 2, 3), p=(0.6, 0.35, 0.05)))
    else:
        count = int(rng.choice((1, 2, 3), p=(0.9, 0.1, 0.0)))

    if count == 1:
        return str(rng.choice(HITTER_SINGLE_POSITIONS))
    if count == 2:
        return str(rng.choice(MULTI_HITTER_PATTERNS_2))
    return str(rng.choice(MULTI_HITTER_PATTERNS_3))


def _sample_point_flexible_pitcher(percentile: float, rng: np.random.Generator) -> str:
    if percentile <= 0.2:
        flex_probability = 0.2
    elif percentile <= 0.7:
        flex_probability = 0.1
    else:
        flex_probability = 0.03
    if rng.random() < flex_probability:
        return "SP;RP"
    return str(rng.choice(PITCHER_SINGLE_POSITIONS))


def _normalize_name(value: str) -> str:
    return value.lower().replace("-", "_").replace(" ", "_")
