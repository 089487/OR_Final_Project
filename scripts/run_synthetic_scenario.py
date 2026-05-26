from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RUNNER = ROOT / "scripts" / "run_synthetic_benchmark.py"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run a full synthetic experiment scenario.")
    parser.add_argument("--scenario", required=True, choices=["N1", "N2", "N3", "N4", "N5", "N6"])
    parser.add_argument("--include-n6-ip", action="store_true", help="Also attempt optional large/xlarge IP runs.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    for command in scenario_commands(args.scenario, args.include_n6_ip):
        print("$ " + " ".join(command), flush=True)
        subprocess.run(command, cwd=ROOT, check=True)


def base_command(**kwargs: object) -> list[str]:
    command = [sys.executable, str(RUNNER)]
    for key, value in kwargs.items():
        option = "--" + key.replace("_", "-")
        if isinstance(value, list):
            command.extend([option, ",".join(str(item) for item in value)])
        else:
            command.extend([option, str(value)])
    return command


def scenario_commands(scenario: str, include_n6_ip: bool) -> list[list[str]]:
    if scenario == "N1":
        return [
            base_command(
                experiment="N1_baseline",
                outdir="experiments/synthetic/N1_baseline",
                points_scenario="normal",
                position_scenario="roster_ratio",
                roster_scale=1,
                num_teams=12,
                player_demand_ratio=3,
                sigma_adp=30,
                delta=0,
                seeds="0:10",
                time_limit=0,
                methods="adp_aware_ilp,direct_greedy,opportunity_cost_greedy",
            )
        ]

    if scenario == "N2":
        return [
            base_command(
                experiment=f"N2_points_{points}",
                outdir=f"experiments/synthetic/N2_points_distribution/{points}",
                points_scenario=points,
                position_scenario="roster_ratio",
                roster_scale=1,
                num_teams=12,
                player_demand_ratio=3,
                sigma_adp=30,
                delta=0,
                seeds="0:10",
                time_limit=0,
                methods="adp_aware_ilp,direct_greedy,opportunity_cost_greedy",
            )
            for points in ("normal", "uniform", "high_low")
        ]

    if scenario == "N3":
        return [
            base_command(
                experiment=f"N3_position_{position}",
                outdir=f"experiments/synthetic/N3_position_distribution/{position}",
                points_scenario="normal",
                position_scenario=position,
                roster_scale=1,
                num_teams=12,
                player_demand_ratio=3,
                sigma_adp=30,
                delta=0,
                seeds="0:10",
                time_limit=0,
                methods="adp_aware_ilp,direct_greedy,opportunity_cost_greedy",
            )
            for position in ("uniform_by_type", "point_flexible", "single_position", "roster_ratio")
        ]

    if scenario == "N4":
        commands = []
        for scale in (1, 2, 3):
            for ratio in (1, 3, 10):
                commands.append(
                    base_command(
                        experiment=f"N4_scale_s{scale}_ratio{ratio}",
                        outdir=f"experiments/synthetic/N4_scaling/s{scale}_ratio{ratio}",
                        points_scenario="normal",
                        position_scenario="roster_ratio",
                        roster_scale=scale,
                        num_teams=12,
                        player_demand_ratio=ratio,
                        sigma_adp=30,
                        delta=0,
                        seeds="0:5",
                        time_limit=0,
                        methods="adp_aware_ilp,direct_greedy,opportunity_cost_greedy",
                    )
                )
        return commands

    if scenario == "N5":
        return [
            base_command(
                experiment=f"N5_adp_sigma{sigma}",
                outdir=f"experiments/synthetic/N5_adp_uncertainty/sigma{sigma}",
                points_scenario="normal",
                position_scenario="roster_ratio",
                roster_scale=1,
                num_teams=12,
                player_demand_ratio=3,
                sigma_adp=sigma,
                delta_min=-10,
                delta_max=10,
                delta_step=1,
                seeds="0:10",
                time_limit=0,
                methods="adp_aware_ilp,direct_greedy,opportunity_cost_greedy",
            )
            for sigma in (0, 10, 30, 60, 100)
        ]

    if scenario == "N6":
        commands = [
            base_command(
                experiment="N6_stress_small",
                outdir="experiments/synthetic/N6_large_scale_stress/stress_small",
                points_scenario="high_low",
                position_scenario="single_position",
                roster_scale=3,
                num_teams=12,
                player_demand_ratio=10,
                sigma_adp=60,
                delta=0,
                seeds="0:3",
                time_limit=300,
                methods="adp_aware_ilp,direct_greedy,opportunity_cost_greedy",
            ),
            base_command(
                experiment="N6_stress_medium",
                outdir="experiments/synthetic/N6_large_scale_stress/stress_medium",
                points_scenario="high_low",
                position_scenario="single_position",
                roster_scale=4,
                num_teams=15,
                player_demand_ratio=10,
                sigma_adp=60,
                delta=0,
                seeds="0:3",
                time_limit=1800,
                methods="adp_aware_ilp,direct_greedy,opportunity_cost_greedy",
            ),
            base_command(
                experiment="N6_stress_large_heuristic",
                outdir="experiments/synthetic/N6_large_scale_stress/stress_large_heuristic",
                points_scenario="high_low",
                position_scenario="single_position",
                roster_scale=6,
                num_teams=15,
                player_demand_ratio=15,
                sigma_adp=60,
                delta=0,
                seeds="0:3",
                time_limit=300,
                methods="direct_greedy,opportunity_cost_greedy",
            ),
            base_command(
                experiment="N6_stress_xlarge_heuristic",
                outdir="experiments/synthetic/N6_large_scale_stress/stress_xlarge_heuristic",
                points_scenario="high_low",
                position_scenario="single_position",
                roster_scale=10,
                num_teams=20,
                player_demand_ratio=20,
                sigma_adp=60,
                delta=0,
                seeds="0:3",
                time_limit=300,
                methods="direct_greedy,opportunity_cost_greedy",
            ),
            base_command(
                experiment="N6_stress_timeout_target_heuristic",
                outdir="experiments/synthetic/N6_large_scale_stress/stress_timeout_target_heuristic",
                points_scenario="high_low",
                position_scenario="single_position",
                roster_scale=16,
                num_teams=24,
                player_demand_ratio=30,
                sigma_adp=60,
                delta=0,
                seeds="0:3",
                time_limit=300,
                methods="direct_greedy,opportunity_cost_greedy",
            ),
        ]
        if include_n6_ip:
            commands.extend(
                [
                    base_command(
                        experiment="N6_stress_large_ip",
                        outdir="experiments/synthetic/N6_large_scale_stress/stress_large_ip",
                        points_scenario="high_low",
                        position_scenario="single_position",
                        roster_scale=6,
                        num_teams=15,
                        player_demand_ratio=15,
                        sigma_adp=60,
                        delta=0,
                        seeds="0:1",
                        time_limit=1800,
                        methods="adp_aware_ilp",
                    ),
                    base_command(
                        experiment="N6_stress_xlarge_ip_tl1800",
                        outdir="experiments/synthetic/N6_large_scale_stress/stress_xlarge_ip_tl1800",
                        points_scenario="high_low",
                        position_scenario="single_position",
                        roster_scale=10,
                        num_teams=20,
                        player_demand_ratio=20,
                        sigma_adp=60,
                        delta=0,
                        seeds="0:1",
                        time_limit=1800,
                        methods="adp_aware_ilp",
                    ),
                    base_command(
                        experiment="N6_stress_timeout_target_ip",
                        outdir="experiments/synthetic/N6_large_scale_stress/stress_timeout_target_ip",
                        points_scenario="high_low",
                        position_scenario="single_position",
                        roster_scale=16,
                        num_teams=24,
                        player_demand_ratio=30,
                        sigma_adp=60,
                        delta=0,
                        seeds="0:1",
                        time_limit=1800,
                        methods="adp_aware_ilp",
                    ),
                ]
            )
        return commands

    raise ValueError(f"Unknown scenario: {scenario}")


if __name__ == "__main__":
    main()
