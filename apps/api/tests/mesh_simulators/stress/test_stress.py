"""Stress and chaos simulator tests."""

from __future__ import annotations

from pathlib import Path

from app.mesh_simulators.stress.chaos_injector import ChaosInjector
from app.mesh_simulators.stress.load_test_report import export_json, generate_html_report
from app.mesh_simulators.stress.stress_runner import StressRunner


def test_stress_runner_spawns_correct_count() -> None:
    runner = StressRunner()
    spawned = runner.spawn_devices(100, "soil_sensor", 10_000)
    assert len(spawned) == 100
    counts = runner.bootstrap_default_mesh()
    assert counts["soil_sensor"] == 100
    assert counts["camera"] == 50


def test_chaos_packet_loss_rate() -> None:
    chaos = ChaosInjector(seed=1)
    dropped = sum(1 for _ in range(1000) if chaos.packet_loss(0.05))
    assert 20 < dropped < 80


def test_chaos_broker_disconnect_recovery() -> None:
    chaos = ChaosInjector()
    chaos.broker_disconnect(0)
    assert chaos.broker_disconnected is False


def test_load_report_generation(tmp_path: Path) -> None:
    runner = StressRunner()
    for ms in (5.0, 10.0, 20.0, 40.0):
        runner.record_message(ms)
    html = generate_html_report(runner.metrics, tmp_path / "report.html")
    js = export_json(runner.metrics, tmp_path / "report.json")
    assert html.exists()
    assert js.exists()


def test_stress_metrics_percentiles() -> None:
    runner = StressRunner()
    runner.record_message(10.0)
    runner.record_message(20.0)
    assert runner.metrics.percentile(50) >= 10.0


def test_device_crash_restarts_subset() -> None:
    chaos = ChaosInjector(seed=2)
    devices = list(range(10))
    after = chaos.device_crash(devices, 3)
    assert len(after) == 10


def test_chaos_latency_returns_ms() -> None:
    chaos = ChaosInjector(seed=3)
    delay = chaos.network_latency(1, 2)
    assert delay >= 1.0


def test_runner_dropped_messages() -> None:
    runner = StressRunner()
    runner.record_message(1.0, dropped=True)
    assert runner.metrics.messages_dropped == 1
