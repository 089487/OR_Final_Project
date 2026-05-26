from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

os.environ.setdefault("MPLCONFIGDIR", str(Path("experiments") / ".matplotlib"))

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns


HEURISTIC_METHODS = {"Direct Greedy", "Opportunity Cost Greedy"}
IP_METHOD = "ADP-aware ILP"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Combine synthetic benchmark outputs and plot scaling diagnostics."
    )
    parser.add_argument(
        "--roots",
        nargs="+",
        default=["experiments/synthetic/N4_scaling", "experiments/synthetic/N6_large_scale_stress"],
        help="Experiment roots containing */summary/benchmark_results.csv files.",
    )
    parser.add_argument("--outdir", default="experiments/synthetic/scaling_summary")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)

    results = load_results([Path(root) for root in args.roots])
    if results.empty:
        raise SystemExit("No benchmark_results.csv files found.")

    results = ensure_scaling_columns(results)
    results = add_ip_reference_columns(results)
    results.to_csv(outdir / "scaling_benchmark_results.csv", index=False)
    summarize_by_method_size(results).to_csv(outdir / "scaling_summary_by_method_size.csv", index=False)
    summarize_ip_status(results).to_csv(outdir / "ip_status_by_variable_count.csv", index=False)
    make_plots(results, outdir)
    print(f"Wrote scaling summary to {outdir.resolve()}")


def load_results(roots: list[Path]) -> pd.DataFrame:
    frames = []
    seen_paths: set[Path] = set()
    for root in roots:
        for path in sorted(root.glob("**/summary/benchmark_results.csv")):
            resolved = path.resolve()
            if resolved in seen_paths:
                continue
            seen_paths.add(resolved)
            frame = pd.read_csv(path)
            frame["source_file"] = str(path)
            frame["source_run"] = path.parent.parent.name
            frame["source_root"] = str(root)
            frames.append(frame)
    if not frames:
        return pd.DataFrame()
    return pd.concat(frames, ignore_index=True)


def add_ip_reference_columns(results: pd.DataFrame) -> pd.DataFrame:
    results = results.copy()
    keys = [
        "source_file",
        "experiment",
        "seed",
        "delta",
        "draft_position",
        "points_scenario",
        "position_scenario",
        "roster_scale",
        "num_teams",
        "player_demand_ratio",
        "sigma_adp",
    ]
    keys = [key for key in keys if key in results.columns]
    ip_rows = results.loc[results["method"] == IP_METHOD, keys + ["status", "objective", "mip_gap", "best_bound"]].copy()
    if ip_rows.empty:
        results["adp_aware_status"] = pd.NA
        results["adp_aware_mip_gap_ref"] = pd.NA
        results["adp_aware_best_bound_ref"] = pd.NA
        return results

    ip_rows = ip_rows.rename(
        columns={
            "status": "adp_aware_status",
            "objective": "adp_aware_objective_ref",
            "mip_gap": "adp_aware_mip_gap_ref",
            "best_bound": "adp_aware_best_bound_ref",
        }
    )
    return results.merge(ip_rows, on=keys, how="left")


def ensure_scaling_columns(results: pd.DataFrame) -> pd.DataFrame:
    results = results.copy()
    if "num_positions" not in results.columns:
        results["num_positions"] = 9
    if "num_players" not in results.columns:
        results["num_players"] = (
            pd.to_numeric(results.get("roster_size"), errors="coerce")
            * pd.to_numeric(results.get("num_teams"), errors="coerce")
            * pd.to_numeric(results.get("player_demand_ratio"), errors="coerce")
        )
    if "approx_variable_count" not in results.columns:
        results["approx_variable_count"] = (
            pd.to_numeric(results["num_players"], errors="coerce")
            * (
                1
                + pd.to_numeric(results["num_positions"], errors="coerce")
                + pd.to_numeric(results.get("roster_size"), errors="coerce")
            )
        )
    if "approx_constraint_count" not in results.columns:
        results["approx_constraint_count"] = (
            pd.to_numeric(results["num_players"], errors="coerce")
            * (
                pd.to_numeric(results["num_positions"], errors="coerce")
                + pd.to_numeric(results.get("roster_size"), errors="coerce")
                + 2
            )
            + pd.to_numeric(results["num_positions"], errors="coerce")
            + pd.to_numeric(results.get("roster_size"), errors="coerce")
        )
    return results


def summarize_by_method_size(results: pd.DataFrame) -> pd.DataFrame:
    group_cols = [
        "method",
        "approx_variable_count",
        "num_players",
        "roster_size",
        "roster_scale",
        "num_teams",
        "player_demand_ratio",
    ]
    group_cols = [col for col in group_cols if col in results.columns]
    return (
        results.groupby(group_cols, as_index=False)
        .agg(
            mean_runtime_seconds=("runtime_seconds", "mean"),
            median_runtime_seconds=("runtime_seconds", "median"),
            mean_objective=("objective", "mean"),
            mean_optimal_gap_pct=("optimal_gap_pct", "mean"),
            mean_mip_gap=("mip_gap", "mean"),
            optimal_cases=("status", lambda values: int((values == "OPTIMAL").sum())),
            cases=("status", "size"),
        )
        .sort_values(["approx_variable_count", "method"])
    )


def summarize_ip_status(results: pd.DataFrame) -> pd.DataFrame:
    ip = results.loc[results["method"] == IP_METHOD].copy()
    if ip.empty:
        return pd.DataFrame()
    group_cols = [
        "approx_variable_count",
        "num_players",
        "roster_size",
        "roster_scale",
        "num_teams",
        "player_demand_ratio",
        "status",
    ]
    group_cols = [col for col in group_cols if col in ip.columns]
    return (
        ip.groupby(group_cols, as_index=False)
        .agg(
            cases=("status", "size"),
            mean_runtime_seconds=("runtime_seconds", "mean"),
            mean_mip_gap=("mip_gap", "mean"),
            mean_best_bound=("best_bound", "mean"),
            mean_objective=("objective", "mean"),
        )
        .sort_values(["approx_variable_count", "status"])
    )


def make_plots(results: pd.DataFrame, outdir: Path) -> None:
    sns.set_theme(style="whitegrid")
    plot_runtime(results, outdir)
    plot_heuristic_gap(results, outdir)
    plot_ip_status_mip_gap(results, outdir)


def plot_runtime(results: pd.DataFrame, outdir: Path) -> None:
    data = results.dropna(subset=["approx_variable_count", "runtime_seconds"]).copy()
    data = data.loc[data["runtime_seconds"] > 0]
    if data.empty:
        return
    plt.figure(figsize=(10, 5.8))
    sns.lineplot(
        data=data,
        x="approx_variable_count",
        y="runtime_seconds",
        hue="method",
        marker="o",
        errorbar="sd",
    )
    plt.xscale("log")
    plt.yscale("log")
    plt.title("Runtime vs approximate IP variable count")
    plt.xlabel("Approximate IP variable count")
    plt.ylabel("Runtime seconds")
    plt.tight_layout()
    plt.savefig(outdir / "runtime_by_variable_count.png", dpi=180)
    plt.close()


def plot_heuristic_gap(results: pd.DataFrame, outdir: Path) -> None:
    data = results.loc[
        results["method"].isin(HEURISTIC_METHODS)
        & (results["adp_aware_status"] == "OPTIMAL")
        & results["optimal_gap_pct"].notna()
    ].copy()
    if data.empty:
        return
    plt.figure(figsize=(10, 5.8))
    sns.lineplot(
        data=data,
        x="approx_variable_count",
        y="optimal_gap_pct",
        hue="method",
        marker="o",
        errorbar="sd",
    )
    plt.xscale("log")
    plt.title("Heuristic optimality gap vs approximate IP variable count")
    plt.xlabel("Approximate IP variable count")
    plt.ylabel("Optimality gap ratio")
    plt.tight_layout()
    plt.savefig(outdir / "heuristic_gap_by_variable_count.png", dpi=180)
    plt.close()


def plot_ip_status_mip_gap(results: pd.DataFrame, outdir: Path) -> None:
    ip = results.loc[results["method"] == IP_METHOD].copy()
    if ip.empty:
        return

    fig, axes = plt.subplots(1, 2, figsize=(14, 5.8))

    status_counts = (
        ip.groupby(["approx_variable_count", "status"], as_index=False)
        .size()
        .rename(columns={"size": "cases"})
    )
    sns.scatterplot(
        data=status_counts,
        x="approx_variable_count",
        y="status",
        size="cases",
        sizes=(80, 320),
        ax=axes[0],
        legend=False,
    )
    axes[0].set_xscale("log")
    axes[0].set_title("IP status by model size")
    axes[0].set_xlabel("Approximate IP variable count")
    axes[0].set_ylabel("Gurobi status")

    mip = ip.dropna(subset=["mip_gap"]).copy()
    if mip.empty:
        axes[1].text(0.5, 0.5, "No MIPGap values", ha="center", va="center")
        axes[1].set_axis_off()
    else:
        sns.lineplot(
            data=mip,
            x="approx_variable_count",
            y="mip_gap",
            marker="o",
            errorbar="sd",
            ax=axes[1],
        )
        axes[1].set_xscale("log")
        axes[1].set_title("IP MIPGap by model size")
        axes[1].set_xlabel("Approximate IP variable count")
        axes[1].set_ylabel("MIPGap")

    fig.tight_layout()
    fig.savefig(outdir / "ip_status_mip_gap_by_variable_count.png", dpi=180)
    plt.close(fig)


if __name__ == "__main__":
    main()
