"""Load test report generation."""

from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path

from app.mesh_simulators.stress.stress_runner import StressMetrics


def generate_html_report(metrics: StressMetrics, output_path: Path) -> Path:
    p50 = _percentile(metrics.latencies_ms, 50)
    p95 = _percentile(metrics.latencies_ms, 95)
    p99 = _percentile(metrics.latencies_ms, 99)
    html = f"""<!doctype html>
<html><head><title>Mesh Stress Report</title></head>
<body>
<h1>Mesh Stress Report</h1>
<ul>
<li>Messages sent: {metrics.messages_sent}</li>
<li>Dropped: {metrics.messages_dropped}</li>
<li>Latency p50: {p50:.2f} ms</li>
<li>Latency p95: {p95:.2f} ms</li>
<li>Latency p99: {p99:.2f} ms</li>
</ul>
</body></html>"""
    output_path.write_text(html, encoding="utf-8")
    return output_path


def export_json(metrics: StressMetrics, output_path: Path) -> Path:
    payload = asdict(metrics)
    payload["p50"] = _percentile(metrics.latencies_ms, 50)
    payload["p95"] = _percentile(metrics.latencies_ms, 95)
    payload["p99"] = _percentile(metrics.latencies_ms, 99)
    output_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return output_path


def _percentile(values: list[float], pct: float) -> float:
    if not values:
        return 0.0
    ordered = sorted(values)
    idx = int(min(len(ordered) - 1, max(0, round((pct / 100.0) * (len(ordered) - 1)))))
    return ordered[idx]
