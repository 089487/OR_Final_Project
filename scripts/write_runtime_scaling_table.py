from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd


INTERRUPTED_IP_ROW = {
    "level": "timeout_target",
    "method": "ADP-aware ILP",
    "approx_variable_count": 49_029_120,
    "num_players": 184_320,
    "roster_size": 256,
    "runtime_seconds": pd.NA,
    "runtime_display": "> monitoring window; interrupted",
    "status": "MANUAL_INTERRUPT_NO_OUTPUT",
    "cases": 1,
    "note": "No benchmark_results.csv was produced before manual interruption.",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Write report-ready runtime scaling tables.")
    parser.add_argument(
        "--summary",
        default="experiments/synthetic/scaling_summary/scaling_summary_by_method_size.csv",
    )
    parser.add_argument("--outdir", default="experiments/synthetic/scaling_summary")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    summary = pd.read_csv(args.summary)
    table = build_runtime_table(summary)
    table.to_csv(outdir / "runtime_scaling_table.csv", index=False)
    write_markdown(table, outdir / "runtime_scaling_table.md")
    print(f"Wrote runtime scaling table to {outdir.resolve()}")


def build_runtime_table(summary: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for row in summary.to_dict("records"):
        level = infer_level(int(row["approx_variable_count"]))
        rows.append(
            {
                "level": level,
                "method": row["method"],
                "approx_variable_count": int(row["approx_variable_count"]),
                "num_players": int(row["num_players"]),
                "roster_size": int(row["roster_size"]),
                "runtime_seconds": row["mean_runtime_seconds"],
                "runtime_display": f"{row['mean_runtime_seconds']:.3f}s",
                "status": "OPTIMAL" if int(row["optimal_cases"]) == int(row["cases"]) else "PARTIAL_OR_INFEASIBLE",
                "cases": int(row["cases"]),
                "note": "",
            }
        )
    rows.append(INTERRUPTED_IP_ROW)
    table = pd.DataFrame(rows)
    method_order = {"ADP-aware ILP": 0, "Opportunity Cost Greedy": 1, "Direct Greedy": 2}
    table["_method_order"] = table["method"].map(method_order).fillna(99)
    table = table.sort_values(["approx_variable_count", "_method_order", "method"]).drop(columns="_method_order")
    return table


def infer_level(variable_count: int) -> str:
    levels = {
        334_080: "stress_small / N4 largest",
        710_400: "stress_medium",
        2_289_600: "stress_large",
        10_880_000: "stress_xlarge",
        49_029_120: "timeout_target",
    }
    return levels.get(variable_count, "N4_scaling")


def write_markdown(table: pd.DataFrame, path: Path) -> None:
    columns = [
        "level",
        "method",
        "approx_variable_count",
        "num_players",
        "roster_size",
        "runtime_display",
        "status",
        "cases",
        "note",
    ]
    markdown = simple_markdown_table(table[columns])
    path.write_text("# Runtime Scaling Table\n\n" + markdown + "\n", encoding="utf-8")


def simple_markdown_table(frame: pd.DataFrame) -> str:
    rows = [[str(value) if pd.notna(value) else "" for value in row] for row in frame.to_numpy()]
    headers = list(frame.columns)
    widths = [
        max(len(header), *(len(row[col_idx]) for row in rows))
        for col_idx, header in enumerate(headers)
    ]
    header_line = "| " + " | ".join(header.ljust(widths[idx]) for idx, header in enumerate(headers)) + " |"
    sep_line = "| " + " | ".join("-" * widths[idx] for idx in range(len(headers))) + " |"
    body_lines = [
        "| " + " | ".join(row[idx].ljust(widths[idx]) for idx in range(len(headers))) + " |"
        for row in rows
    ]
    return "\n".join([header_line, sep_line, *body_lines])


if __name__ == "__main__":
    main()
