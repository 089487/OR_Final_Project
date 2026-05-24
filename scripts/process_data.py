from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Literal

import pandas as pd


DEFAULT_ADP_PATH = Path("data/adp/2026_adp.csv")
DEFAULT_HITTER_PATH = Path("data/raw/2026/FantasyPros_2026_Projections_H.csv")
DEFAULT_PITCHER_PATH = Path("data/raw/2026/FantasyPros_2026_Projections_P.csv")
DEFAULT_YAHOO_SCORING_PATH = Path("scoring/yahoo_scoring.json")
DEFAULT_FANGRAPH_SCORING_PATH = Path("scoring/fangraph_scoring.json")
DEFAULT_OUTPUT_DIR = Path("data/processed")

OUTFIELD_POSITIONS = {"LF", "CF", "RF", "OF"}
HITTER_ONLY_POSITIONS = {"C", "1B", "2B", "3B", "SS", "OF", "Util"}
PITCHER_POSITIONS = {"SP", "RP"}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Build 2026 fantasy baseball player data from ADP and FantasyPros projections."
    )
    parser.add_argument("--adp", default=DEFAULT_ADP_PATH, type=Path)
    parser.add_argument("--hitters", default=DEFAULT_HITTER_PATH, type=Path)
    parser.add_argument("--pitchers", default=DEFAULT_PITCHER_PATH, type=Path)
    parser.add_argument("--yahoo-scoring", default=DEFAULT_YAHOO_SCORING_PATH, type=Path)
    parser.add_argument("--fangraph-scoring", default=DEFAULT_FANGRAPH_SCORING_PATH, type=Path)
    parser.add_argument("--outdir", default=DEFAULT_OUTPUT_DIR, type=Path)
    parser.add_argument(
        "--adp-calibration-alpha",
        default=0.0,
        type=float,
        help="Blend raw scoring points with ADP-implied market value. 0 keeps raw points; 1 follows ADP ranking.",
    )
    parser.add_argument(
        "--suffix",
        default="",
        help="Optional filename suffix, for example _calibrated.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    args.outdir.mkdir(parents=True, exist_ok=True)

    adp = read_adp(args.adp)
    hitters = read_projection(args.hitters)
    pitchers = read_projection(args.pitchers)

    yahoo_scoring = read_scoring(args.yahoo_scoring)
    fangraph_scoring = read_scoring(args.fangraph_scoring)

    yahoo = build_player_data(
        adp,
        hitters,
        pitchers,
        yahoo_scoring,
        adp_calibration_alpha=args.adp_calibration_alpha,
    )
    fangraph = build_player_data(
        adp,
        hitters,
        pitchers,
        fangraph_scoring,
        adp_calibration_alpha=args.adp_calibration_alpha,
    )

    yahoo_path = args.outdir / f"2026_yahoo_data{args.suffix}.csv"
    fangraph_path = args.outdir / f"2026_fangraph_data{args.suffix}.csv"
    yahoo.to_csv(yahoo_path, index=False)
    fangraph.to_csv(fangraph_path, index=False)

    print(f"Wrote {len(yahoo)} rows to {yahoo_path}")
    print(f"Wrote {len(fangraph)} rows to {fangraph_path}")


def read_adp(path: Path) -> pd.DataFrame:
    adp = pd.read_csv(path).dropna(subset=["Player", "Team", "AVG"])
    adp = adp.copy()
    adp["Player"] = adp["Player"].map(clean_player_name)
    adp["Team"] = adp["Team"].map(clean_team)
    adp["adp"] = pd.to_numeric(adp["AVG"], errors="coerce")
    adp = adp.dropna(subset=["adp"])
    adp["player_key"] = adp["Player"].map(player_key)
    return adp


def read_projection(path: Path) -> pd.DataFrame:
    data = pd.read_csv(path).dropna(subset=["Player"])
    data = data.copy()
    data["Player"] = data["Player"].map(clean_player_name)
    data["Team"] = data["Team"].map(clean_team)
    data["player_key"] = data["Player"].map(player_key)

    for column in data.columns:
        if column in {"Player", "Team", "Positions", "Rost%", "player_key"}:
            continue
        data[column] = pd.to_numeric(data[column], errors="coerce").fillna(0.0)
    return data


def read_scoring(path: Path) -> dict[str, dict[str, float]]:
    with path.open(encoding="utf-8") as file:
        scoring = json.load(file)
    return {
        "batters": {key: float(value) for key, value in scoring.get("batters", {}).items()},
        "pitchers": {key: float(value) for key, value in scoring.get("pitchers", {}).items()},
    }


def build_player_data(
    adp: pd.DataFrame,
    hitters: pd.DataFrame,
    pitchers: pd.DataFrame,
    scoring: dict[str, dict[str, float]],
    *,
    adp_calibration_alpha: float = 0.0,
) -> pd.DataFrame:
    if not 0.0 <= adp_calibration_alpha <= 1.0:
        raise ValueError("adp_calibration_alpha must be between 0 and 1")

    rows: list[dict[str, object]] = []
    hitter_index = make_projection_index(hitters)
    pitcher_index = make_projection_index(pitchers)
    explicit_batter_keys = {
        str(row["player_key"])
        for _, row in adp.iterrows()
        if "(Batter)" in str(row["Player"])
    }

    for _, adp_row in adp.sort_values("adp").iterrows():
        adp_name = str(adp_row["Player"])
        team = str(adp_row["Team"])
        key = str(adp_row["player_key"])
        adp_value = float(adp_row["adp"])
        adp_positions = str(adp_row.get("Positions", ""))

        wants_batter = is_batter_adp_row(adp_name, adp_positions)
        wants_pitcher = is_pitcher_adp_row(adp_name, adp_positions)

        if "(Batter)" in adp_name:
            lookup_key = player_key(adp_name.replace("(Batter)", "").strip())
            hitter = lookup_projection(hitter_index, lookup_key, team)
            if hitter is not None:
                rows.append(make_row(hitter, adp_value, scoring, "H"))
            continue

        hitter = (
            lookup_projection(hitter_index, key, team)
            if wants_batter and key not in explicit_batter_keys
            else None
        )
        pitcher = lookup_projection(pitcher_index, key, team) if wants_pitcher else None

        if hitter is not None and pitcher is not None:
            rows.append(make_row(hitter, adp_value, scoring, "H"))
            rows.append(make_row(pitcher, adp_value, scoring, "P"))
        elif hitter is not None:
            rows.append(make_row(hitter, adp_value, scoring, "H"))
        elif pitcher is not None:
            rows.append(make_row(pitcher, adp_value, scoring, "P"))

    output = pd.DataFrame(rows)
    if output.empty:
        return pd.DataFrame(columns=["player_id", "player_name", "eligible_positions", "adp", "points"])

    output = output.drop_duplicates(subset=["player_id"], keep="first")
    output = output.sort_values(["adp", "player_id"]).reset_index(drop=True)
    if adp_calibration_alpha:
        output = calibrate_points_to_adp(output, adp_calibration_alpha)
    return output[["player_id", "player_name", "eligible_positions", "adp", "points"]]


def calibrate_points_to_adp(data: pd.DataFrame, alpha: float) -> pd.DataFrame:
    """Shrink raw scoring points toward a monotone ADP-implied market value."""
    calibrated = data.copy()
    point_curve = calibrated["points"].sort_values(ascending=False).to_numpy()
    adp_order = calibrated.sort_values(["adp", "player_id"]).index
    market_points = pd.Series(index=adp_order, data=point_curve[: len(adp_order)])
    calibrated["points"] = (
        (1.0 - alpha) * calibrated["points"] + alpha * market_points.reindex(calibrated.index)
    ).round(2)
    return calibrated


def make_projection_index(data: pd.DataFrame) -> dict[tuple[str, str], pd.Series]:
    index: dict[tuple[str, str], pd.Series] = {}
    for _, row in data.iterrows():
        key = (str(row["player_key"]), str(row["Team"]))
        if key not in index:
            index[key] = row
    return index


def lookup_projection(
    projection_index: dict[tuple[str, str], pd.Series],
    key: str,
    team: str,
) -> pd.Series | None:
    if (key, team) in projection_index:
        return projection_index[(key, team)]
    matches = [row for (player, _team), row in projection_index.items() if player == key]
    if len(matches) == 1:
        return matches[0]
    return None


def make_row(
    projection_row: pd.Series,
    adp: float,
    scoring: dict[str, dict[str, float]],
    role: Literal["H", "P"],
) -> dict[str, object]:
    player_name = str(projection_row["Player"])
    suffix = "_H" if role == "H" else "_P"
    player_id = f"{slugify(player_name)}{suffix}"
    positions = normalize_positions(str(projection_row["Positions"]), role)
    points = calculate_points(projection_row, scoring["batters" if role == "H" else "pitchers"], role)

    return {
        "player_id": player_id,
        "player_name": f"{player_name}{suffix}",
        "eligible_positions": ";".join(positions),
        "adp": round(float(adp), 2),
        "points": round(points, 2),
    }


def calculate_points(
    row: pd.Series,
    weights: dict[str, float],
    role: Literal["H", "P"],
) -> float:
    total = 0.0
    for stat, weight in weights.items():
        total += get_stat_value(row, stat, role) * weight
    return total


def get_stat_value(row: pd.Series, stat: str, role: Literal["H", "P"]) -> float:
    if stat == "1B":
        hits = float(row.get("H", 0.0))
        doubles = float(row.get("2B", 0.0))
        triples = float(row.get("3B", 0.0))
        homers = float(row.get("HR", 0.0))
        return max(0.0, hits - doubles - triples - homers)

    if role == "P" and stat == "SO":
        return float(row.get("K", 0.0))

    return float(row.get(stat, 0.0))


def normalize_positions(positions: str, role: Literal["H", "P"]) -> tuple[str, ...]:
    normalized: list[str] = []
    for raw_position in positions.split(","):
        position = raw_position.strip()
        if not position:
            continue
        if position in OUTFIELD_POSITIONS:
            position = "OF"
        elif position == "DH":
            position = "Util"

        if role == "H" and position in HITTER_ONLY_POSITIONS:
            normalized.append(position)
        elif role == "P" and position in PITCHER_POSITIONS:
            normalized.append(position)

    return tuple(dict.fromkeys(normalized))


def is_batter_adp_row(player_name: str, positions: str) -> bool:
    if "(Batter)" in player_name:
        return True
    normalized = set(normalize_positions(positions, "H"))
    return bool(normalized)


def is_pitcher_adp_row(player_name: str, positions: str) -> bool:
    if "(Batter)" in player_name:
        return False
    normalized = set(normalize_positions(positions, "P"))
    return bool(normalized)


def clean_player_name(name: object) -> str:
    return re.sub(r"\s+", " ", str(name).strip())


def clean_team(team: object) -> str:
    if pd.isna(team):
        return ""
    return str(team).strip()


def player_key(name: str) -> str:
    name = clean_player_name(name).replace("(Batter)", "").strip()
    return re.sub(r"[^a-z0-9]+", "", name.lower())


def slugify(name: str) -> str:
    return re.sub(r"_+", "_", re.sub(r"[^A-Za-z0-9]+", "_", clean_player_name(name))).strip("_")


if __name__ == "__main__":
    main()
