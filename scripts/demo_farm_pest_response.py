#!/usr/bin/env python3
"""Farm Pest Response end-to-end demo (simulators + mesh workflow)."""

from __future__ import annotations

import argparse
import sys
import time
from datetime import UTC, datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "apps" / "api"))

import httpx

DEFAULT_API = "http://localhost:8000"


def _write_report(lines: list[str]) -> Path:
    out = Path("/tmp") / f"demo-pest-response-{int(time.time())}.md"
    out.write_text("\n".join(lines), encoding="utf-8")
    return out


def main() -> int:
    parser = argparse.ArgumentParser(description="Farm Pest Response E2E demo")
    parser.add_argument("--api", default=DEFAULT_API)
    parser.add_argument("--skip-compose", action="store_true", help="Do not docker compose up simulators")
    parser.add_argument("--cctv-url", default="http://localhost:9100/simulate-motion")
    args = parser.parse_args()

    timeline: list[str] = []
    t0 = time.perf_counter()

    def mark(step: str) -> None:
        ms = int((time.perf_counter() - t0) * 1000)
        timeline.append(f"- **{ms}ms** — {step}")

    if not args.skip_compose:
        mark("Start simulators profile (run manually: docker compose --profile simulators up -d)")
    else:
        mark("Skipped docker compose (use --skip-compose)")

    mark("Wait 10s for MQTT connect")
    time.sleep(2 if args.skip_compose else 10)

    try:
        res = httpx.post(args.cctv_url, json={"confidence": 0.92}, timeout=10.0)
        mark(f"CCTV simulate-motion → HTTP {res.status_code}")
    except httpx.HTTPError as exc:
        mark(f"CCTV simulate-motion failed: {exc}")

    try:
        health = httpx.get(f"{args.api}/health", timeout=5.0)
        mark(f"API health → {health.status_code}")
    except httpx.HTTPError as exc:
        mark(f"API health check failed: {exc}")

    report_lines = [
        "# Farm Pest Response — Demo Report",
        f"Generated: {datetime.now(tz=UTC).isoformat()}",
        "",
        "## Timeline",
        *timeline,
        "",
        "## Notes",
        "- Verify workflow execution in HQ → Automations → Mesh Workflows → executions",
        "- Verify mesh events at `/mesh/graph` terminal feed",
        "- Wear companion should show alert after FCM/SSE (Week 11-12 live wire)",
    ]
    path = _write_report(report_lines)
    print(f"Report written: {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
