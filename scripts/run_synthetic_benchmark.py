from __future__ import annotations

import argparse
import os
import sys
from math import ceil
from pathlib import Path
from time import perf_counter

os.environ.setdefault("MPLCONFIGDIR", str(Path("experiments") / ".matplotlib"))

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

from src.draft_core import DraftSolution, load_players, snake_picks
from src.heuristics import solve_greedy, solve_opportunity_cost_greedy
from src.ip_model import solve_ilp
from src.synthetic_data import (
    SyntheticConfig,
    generate_synthetic_players,
    metadata_row,
    scale_roster_requirements,
    write_synthetic_players,
)


METHOD_DIRS = {
    "Static IP": "static_IP",
    "ADP-aware ILP": "adp_aware_ILP",
    "Direct Greedy": "heuristic_greedy",
    "Opportunity Cost Greedy": "heuristic_opportunity_cost",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run synthetic draft benchmarks.")
    parser.add_argument("--experiment", default="N1_baseline")
    parser.add_argument("--outdir", default="experiments/synthetic/N1_baseline")
    parser.add_argument("--instances-dir", default=None)
    parser.add_argument("--metadata-out", default=None)
    parser.add_argument("--points-scenario", default="normal", choices=["normal", "uniform", "high_low"])
    parser.add_argument(
        "--position-scenario",
        default="roster_ratio",
        choices=["uniform_by_type", "point_flexible", "single_position", "roster_ratio"],
    )
    parser.add_argument("--roster-scale", type=int, default=1)
    parser.add_argument("--num-teams", type=int, default=12)
    parser.add_argument("--draft-position", type=int, default=None)
    parser.add_argument("--player-demand-ratio", type=int, default=3)
    parser.add_argument("--sigma-adp", type=float, default=30.0)
    parser.add_argument("--delta", type=float, default=0.0)
    parser.add_argument("--delta-grid", default=None, help="Comma-separated delta values.")
    parser.add_argument("--delta-min", type=float, default=None)
    parser.add_argument("--delta-max", type=float, default=None)
    parser.add_argument("--delta-step", type=float, default=1.0)
    parser.add_argument("--seeds", default="0", help="Comma-separated seeds or range like 0:10.")
    parser.add_argument("--season", type=int, default=9999)
    parser.add_argument("--time-limit", type=int, default=0, help="Gurobi time limit in seconds. Use 0 for no limit.")
    parser.add_argument(
        "--methods",
        default="adp_aware_ilp,direct_greedy,opportunity_cost_greedy",
        help="Comma-separated methods: static_ip, adp_aware_ilp, direct_greedy, opportunity_cost_greedy.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    outdir = Path(args.outdir)
    instances_dir = Path(args.instances_dir) if args.instances_dir else Path("data/synthetic/instances") / args.experiment
    metadata_out = Path(args.metadata_out) if args.metadata_out else Path("data/synthetic/metadata") / f"{args.experiment}_metadata.csv"
    summary_dir = outdir / "summary"
    summary_dir.mkdir(parents=True, exist_ok=True)
    instances_dir.mkdir(parents=True, exist_ok=True)
    metadata_out.parent.mkdir(parents=True, exist_ok=True)

    seeds = parse_seeds(args.seeds)
    deltas = parse_deltas(args)
    methods = parse_methods(args.methods)
    roster_requirements = scale_roster_requirements(scale=args.roster_scale)
    rounds = sum(roster_requirements.values())
    draft_position = args.draft_position or ceil(args.num_teams / 2)
    picks = snake_picks(args.num_teams, draft_position, rounds)

    result_rows: list[dict[str, object]] = []
    roster_frames: list[pd.DataFrame] = []
    metadata_rows: list[dict[str, object]] = []

    total_cases = len(seeds) * len(deltas)
    completed = 0
    for seed in seeds:
        config = SyntheticConfig(
            points_scenario=args.points_scenario,
            position_scenario=args.position_scenario,
            roster_scale=args.roster_scale,
            num_teams=args.num_teams,
            player_demand_ratio=args.player_demand_ratio,
            sigma_adp=args.sigma_adp,
            seed=seed,
            season=args.season,
        )
        instance_path = instances_dir / f"seed_{seed}.csv"
        players = generate_synthetic_players(config)
        write_synthetic_players(players, instance_path)
        metadata_rows.append({"experiment": args.experiment, "instance_path": str(instance_path), **metadata_row(config, players)})
        players = load_players(instance_path)

        for delta in deltas:
            completed += 1
            print(
                f"[{completed}/{total_cases}] experiment={args.experiment} seed={seed} delta={delta}",
                flush=True,
            )
            solutions = run_methods(
                methods=methods,
                players=players,
                picks=picks,
                season=args.season,
                draft_position=draft_position,
                delta=delta,
                roster_requirements=roster_requirements,
                time_limit=args.time_limit,
            )
            adp_aware = next((solution for solution in solutions if solution.method == "ADP-aware ILP"), None)
            for solution in solutions:
                result_rows.append(
                    make_result_row(
                        solution=solution,
                        adp_aware=adp_aware,
                        experiment=args.experiment,
                        seed=seed,
                        delta=delta,
                        draft_position=draft_position,
                        config=config,
                        roster_size=rounds,
                        num_players=len(players),
                    )
                )
                if not solution.roster.empty:
                    roster_frames.append(
                        solution.roster.assign(
                            experiment=args.experiment,
                            seed=seed,
                            benchmark_delta=delta,
                            roster_scale=args.roster_scale,
                            num_teams=args.num_teams,
                            player_demand_ratio=args.player_demand_ratio,
                        )
                    )

            pd.DataFrame(result_rows).to_csv(summary_dir / "benchmark_results.csv", index=False)

    results = pd.DataFrame(result_rows)
    write_outputs(results, roster_frames, outdir)
    write_metadata(metadata_rows, metadata_out)
    make_plots(results, summary_dir)
    print(f"Wrote synthetic benchmark outputs to {outdir.resolve()}")
    if not results.empty:
        print(summarize_by_method(results).to_string(index=False))


def parse_seeds(value: str) -> list[int]:
    if ":" in value:
        start, stop = value.split(":", maxsplit=1)
        return list(range(int(start), int(stop)))
    return [int(seed.strip()) for seed in value.split(",") if seed.strip()]


def parse_deltas(args: argparse.Namespace) -> list[float]:
    if args.delta_grid:
        return [float(value.strip()) for value in args.delta_grid.split(",") if value.strip()]
    if args.delta_min is not None and args.delta_max is not None:
        values = []
        current = args.delta_min
        while current <= args.delta_max + 1e-9:
            values.append(round(current, 10))
            current += args.delta_step
        return values
    return [args.delta]


def parse_methods(value: str) -> list[str]:
    aliases = {
        "static_ip": "Static IP",
        "static": "Static IP",
        "adp_aware_ilp": "ADP-aware ILP",
        "adp": "ADP-aware ILP",
        "ip": "ADP-aware ILP",
        "direct_greedy": "Direct Greedy",
        "greedy": "Direct Greedy",
        "opportunity_cost_greedy": "Opportunity Cost Greedy",
        "opportunity_cost": "Opportunity Cost Greedy",
    }
    methods = []
    for raw in value.split(","):
        key = raw.strip().lower().replace("-", "_").replace(" ", "_")
        if not key:
            continue
        if key not in aliases:
            raise ValueError(f"Unknown method: {raw}")
        methods.append(aliases[key])
    return list(dict.fromkeys(methods))


def run_methods(
    *,
    methods: list[str],
    players: pd.DataFrame,
    picks: list[int],
    season: int,
    draft_position: int,
    delta: float,
    roster_requirements: dict[str, int],
    time_limit: int,
):
    solutions = []
    for method in methods:
        start = perf_counter()
        try:
            if method == "Static IP":
                solution = solve_ilp(
                    players,
                    picks,
                    season=season,
                    draft_position=draft_position,
                    delta=0.0,
                    roster_requirements=roster_requirements,
                    enforce_adp=False,
                    method_name="Static IP",
                    time_limit=time_limit,
                )
            elif method == "ADP-aware ILP":
                solution = solve_ilp(
                    players,
                    picks,
                    season=season,
                    draft_position=draft_position,
                    delta=delta,
                    roster_requirements=roster_requirements,
                    enforce_adp=True,
                    method_name="ADP-aware ILP",
                    time_limit=time_limit,
                )
            elif method == "Direct Greedy":
                solution = solve_greedy(
                    players,
                    picks,
                    season=season,
                    draft_position=draft_position,
                    delta=delta,
                    roster_requirements=roster_requirements,
                    enforce_adp=True,
                )
            elif method == "Opportunity Cost Greedy":
                solution = solve_opportunity_cost_greedy(
                    players,
                    picks,
                    season=season,
                    draft_position=draft_position,
                    delta=delta,
                    roster_requirements=roster_requirements,
                    enforce_adp=True,
                )
            else:
                raise ValueError(f"Unknown method: {method}")
        except Exception as exc:
            elapsed = perf_counter() - start
            print(f"[ERROR] method={method} failed with {type(exc).__name__}: {exc}", flush=True)
            solution = DraftSolution(
                method=method,
                season=season,
                draft_position=draft_position,
                delta=delta,
                objective=float("nan"),
                status=f"ERROR_{type(exc).__name__}",
                roster=pd.DataFrame(),
                runtime_seconds=elapsed,
            )

        if solution.runtime_seconds is None:
            object.__setattr__(solution, "runtime_seconds", perf_counter() - start)
        solutions.append(solution)
    return solutions


def make_result_row(
    *,
    solution,
    adp_aware,
    experiment: str,
    seed: int,
    delta: float,
    draft_position: int,
    config: SyntheticConfig,
    roster_size: int,
    num_players: int,
) -> dict[str, object]:
    objective = float(solution.objective)
    adp_objective = float(adp_aware.objective) if adp_aware is not None else float("nan")
    is_heuristic = solution.method in {"Direct Greedy", "Opportunity Cost Greedy"}
    optimal_gap = adp_objective - objective if is_heuristic and pd.notna(adp_objective) else float("nan")
    optimal_gap_pct = optimal_gap / adp_objective if is_heuristic and adp_objective and pd.notna(adp_objective) else float("nan")
    gap_to_bound = (
        (float(solution.best_bound) - objective) / float(solution.best_bound)
        if solution.best_bound not in (None, 0) and pd.notna(objective)
        else float("nan")
    )
    num_positions = len(scale_roster_requirements(scale=config.roster_scale))
    approx_variable_count = num_players * (1 + num_positions + roster_size)
    approx_constraint_count = num_players * (num_positions + roster_size + 2) + num_positions + roster_size
    return {
        "experiment": experiment,
        "season": config.season,
        "seed": seed,
        "method": solution.method,
        "status": solution.status,
        "objective": objective,
        "runtime_seconds": solution.runtime_seconds,
        "mip_gap": solution.mip_gap,
        "best_bound": solution.best_bound,
        "gap_to_best_bound": gap_to_bound,
        "adp_aware_objective": adp_objective,
        "optimal_gap": optimal_gap,
        "optimal_gap_pct": optimal_gap_pct,
        "draft_position": draft_position,
        "delta": delta,
        "points_scenario": config.points_scenario,
        "position_scenario": config.position_scenario,
        "roster_scale": config.roster_scale,
        "roster_size": roster_size,
        "num_players": num_players,
        "num_positions": num_positions,
        "approx_variable_count": approx_variable_count,
        "approx_constraint_count": approx_constraint_count,
        "num_teams": config.num_teams,
        "player_demand_ratio": config.player_demand_ratio,
        "sigma_adp": config.sigma_adp,
    }


def write_outputs(results: pd.DataFrame, roster_frames: list[pd.DataFrame], outdir: Path) -> None:
    summary_dir = outdir / "summary"
    summary_dir.mkdir(parents=True, exist_ok=True)
    results.to_csv(summary_dir / "benchmark_results.csv", index=False)
    summarize_by_method(results).to_csv(summary_dir / "summary_by_method.csv", index=False)
    summarize_by_seed(results).to_csv(summary_dir / "summary_by_seed.csv", index=False)
    summarize_by_delta(results).to_csv(summary_dir / "summary_by_delta.csv", index=False)

    if roster_frames:
        rosters = pd.concat(roster_frames, ignore_index=True)
        rosters.to_csv(summary_dir / "selected_rosters.csv", index=False)
    else:
        rosters = pd.DataFrame()

    for method, dirname in METHOD_DIRS.items():
        method_dir = outdir / dirname
        method_results = results.loc[results["method"] == method].copy()
        if method_results.empty:
            continue
        method_dir.mkdir(parents=True, exist_ok=True)
        method_results.to_csv(method_dir / "results.csv", index=False)
        summarize_single_method(method_results).to_csv(method_dir / "summary.csv", index=False)
        if not rosters.empty:
            method_rosters = rosters.loc[rosters["method"] == method]
            if not method_rosters.empty:
                method_rosters.to_csv(method_dir / "selected_rosters.csv", index=False)


def write_metadata(rows: list[dict[str, object]], path: Path) -> None:
    new_metadata = pd.DataFrame(rows)
    if path.exists():
        existing = pd.read_csv(path)
        metadata = pd.concat([existing, new_metadata], ignore_index=True)
    else:
        metadata = new_metadata
    metadata.to_csv(path, index=False)


def summarize_single_method(results: pd.DataFrame) -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "method": results["method"].iloc[0] if not results.empty else "",
                "mean_objective": results["objective"].mean(),
                "median_objective": results["objective"].median(),
                "mean_runtime_seconds": results["runtime_seconds"].mean(),
                "mean_variable_count": results["approx_variable_count"].mean(),
                "mean_optimal_gap_pct": results["optimal_gap_pct"].mean(),
                "mean_mip_gap": results["mip_gap"].mean(),
                "cases": len(results),
            }
        ]
    )


def summarize_by_method(results: pd.DataFrame) -> pd.DataFrame:
    if results.empty:
        return pd.DataFrame()
    return (
        results.groupby("method", as_index=False)
        .agg(
            mean_objective=("objective", "mean"),
            median_objective=("objective", "median"),
            mean_runtime_seconds=("runtime_seconds", "mean"),
            mean_variable_count=("approx_variable_count", "mean"),
            mean_optimal_gap_pct=("optimal_gap_pct", "mean"),
            mean_mip_gap=("mip_gap", "mean"),
            solved_cases=("status", lambda values: int((values == "OPTIMAL").sum())),
            cases=("objective", "size"),
        )
        .sort_values("mean_objective", ascending=False)
    )


def summarize_by_seed(results: pd.DataFrame) -> pd.DataFrame:
    if results.empty:
        return pd.DataFrame()
    return (
        results.groupby(["seed", "method"], as_index=False)
        .agg(
            mean_objective=("objective", "mean"),
            mean_runtime_seconds=("runtime_seconds", "mean"),
            mean_variable_count=("approx_variable_count", "mean"),
            mean_optimal_gap_pct=("optimal_gap_pct", "mean"),
            cases=("objective", "size"),
        )
        .sort_values(["seed", "method"])
    )


def summarize_by_delta(results: pd.DataFrame) -> pd.DataFrame:
    if results.empty:
        return pd.DataFrame()
    return (
        results.groupby(["delta", "method"], as_index=False)
        .agg(
            mean_objective=("objective", "mean"),
            mean_runtime_seconds=("runtime_seconds", "mean"),
            mean_variable_count=("approx_variable_count", "mean"),
            mean_optimal_gap_pct=("optimal_gap_pct", "mean"),
            cases=("objective", "size"),
        )
        .sort_values(["delta", "method"])
    )


def make_plots(results: pd.DataFrame, outdir: Path) -> None:
    if results.empty:
        return
    sns.set_theme(style="whitegrid")

    plt.figure(figsize=(10, 5.6))
    sns.barplot(data=results, x="method", y="objective", errorbar="sd")
    plt.title("Synthetic objective by method")
    plt.xlabel("Method")
    plt.ylabel("Objective")
    plt.xticks(rotation=20, ha="right")
    plt.tight_layout()
    plt.savefig(outdir / "objective_by_method.png", dpi=180)
    plt.close()

    plt.figure(figsize=(10, 5.6))
    sns.barplot(data=results, x="method", y="runtime_seconds", errorbar="sd")
    plt.title("Synthetic runtime by method")
    plt.xlabel("Method")
    plt.ylabel("Runtime seconds")
    plt.xticks(rotation=20, ha="right")
    plt.tight_layout()
    plt.savefig(outdir / "runtime_by_method.png", dpi=180)
    plt.close()

    gap = results.loc[results["method"].isin(["Direct Greedy", "Opportunity Cost Greedy"])]
    if results["approx_variable_count"].nunique() > 1:
        plt.figure(figsize=(10, 5.6))
        sns.lineplot(
            data=results,
            x="approx_variable_count",
            y="runtime_seconds",
            hue="method",
            marker="o",
            errorbar="sd",
        )
        plt.xscale("log")
        plt.yscale("log")
        plt.title("Runtime by approximate IP variable count")
        plt.xlabel("Approximate IP variable count")
        plt.ylabel("Runtime seconds")
        plt.tight_layout()
        plt.savefig(outdir / "runtime_by_variable_count.png", dpi=180)
        plt.close()

        if gap["optimal_gap_pct"].notna().any():
            plt.figure(figsize=(10, 5.6))
            sns.lineplot(
                data=gap,
                x="approx_variable_count",
                y="optimal_gap_pct",
                hue="method",
                marker="o",
                errorbar="sd",
            )
            plt.xscale("log")
            plt.title("Heuristic gap by approximate IP variable count")
            plt.xlabel("Approximate IP variable count")
            plt.ylabel("Optimal gap ratio")
            plt.tight_layout()
            plt.savefig(outdir / "heuristic_gap_by_variable_count.png", dpi=180)
            plt.close()

    if not gap.empty and gap["optimal_gap_pct"].notna().any():
        plt.figure(figsize=(10, 5.6))
        sns.barplot(data=gap, x="method", y="optimal_gap_pct", errorbar="sd")
        plt.title("Synthetic heuristic optimal gap")
        plt.xlabel("Method")
        plt.ylabel("Optimal gap ratio")
        plt.xticks(rotation=20, ha="right")
        plt.tight_layout()
        plt.savefig(outdir / "heuristic_gap_by_method.png", dpi=180)
        plt.close()

    if results["delta"].nunique() > 1:
        plt.figure(figsize=(10, 5.6))
        sns.lineplot(data=results, x="delta", y="objective", hue="method", marker="o")
        plt.title("Synthetic objective by ADP delta")
        plt.xlabel("Delta")
        plt.ylabel("Objective")
        plt.tight_layout()
        plt.savefig(outdir / "objective_by_delta.png", dpi=180)
        plt.close()


if __name__ == "__main__":
    main()
