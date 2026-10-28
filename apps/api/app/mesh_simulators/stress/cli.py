"""CLI entry for mesh stress simulations."""

from __future__ import annotations

import argparse
from pathlib import Path

from app.mesh_simulators.stress.chaos_injector import ChaosInjector
from app.mesh_simulators.stress.load_test_report import export_json, generate_html_report
from app.mesh_simulators.stress.stress_runner import StressRunner


def main() -> None:
    parser = argparse.ArgumentParser(description="Next-IOT mesh stress runner")
    parser.add_argument("--devices", type=int, default=100)
    parser.add_argument("--duration", type=int, default=600)
    parser.add_argument("--chaos", type=str, default="")
    args = parser.parse_args()

    runner = StressRunner()
    runner.spawn_devices(args.devices, "soil_sensor", 10_000)
    chaos = ChaosInjector()
    if args.chaos.startswith("packet_loss:"):
        rate = float(args.chaos.split(":", 1)[1])
        for _ in range(min(args.duration, 100)):
            dropped = chaos.packet_loss(rate)
            runner.record_message(latency_ms=12.0, dropped=dropped)
    else:
        for _ in range(20):
            runner.record_message(latency_ms=10.0)

    generate_html_report(runner.metrics, Path("stress-report.html"))
    export_json(runner.metrics, Path("stress-report.json"))


if __name__ == "__main__":
    main()
