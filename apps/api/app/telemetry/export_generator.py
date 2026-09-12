"""Telemetry history export generators — CSV, JSON, and KML."""

from __future__ import annotations

import csv
import io
import json
import uuid
from datetime import UTC, datetime
from typing import Any
from xml.sax.saxutils import escape

from app.models.telemetry_reading import TelemetryReading

EXPORT_FORMATS = frozenset({"csv", "json", "kml"})


def _metric_float(metrics: dict[str, Any], *keys: str) -> float | None:
    for key in keys:
        if key in metrics and metrics[key] is not None:
            try:
                return float(metrics[key])
            except (TypeError, ValueError):
                continue
    return None


def _flatten_reading(reading: TelemetryReading) -> dict[str, Any]:
    metrics = reading.metrics or {}
    row: dict[str, Any] = {
        "reading_id": str(reading.id),
        "recorded_at": reading.recorded_at.isoformat(),
        "ingested_at": reading.ingested_at.isoformat() if reading.ingested_at else None,
        "latitude": _metric_float(metrics, "latitude", "lat"),
        "longitude": _metric_float(metrics, "longitude", "lon"),
        "altitude_m": _metric_float(metrics, "altitude_m", "altitude", "alt"),
        "speed_m_s": _metric_float(metrics, "speed", "speed_mps", "ground_speed", "velocity"),
        "voltage": _metric_float(metrics, "voltage", "battery_voltage", "batt_voltage"),
    }
    for key, value in metrics.items():
        if key not in row:
            row[key] = value
    return row


def generate_csv(readings: list[TelemetryReading]) -> str:
    rows = [_flatten_reading(r) for r in readings]
    if not rows:
        return "reading_id,recorded_at,ingested_at,latitude,longitude,altitude_m,speed_m_s,voltage\n"

    fieldnames: list[str] = []
    seen: set[str] = set()
    for row in rows:
        for key in row:
            if key not in seen:
                seen.add(key)
                fieldnames.append(key)

    buffer = io.StringIO()
    writer = csv.DictWriter(buffer, fieldnames=fieldnames, extrasaction="ignore")
    writer.writeheader()
    for row in rows:
        writer.writerow(row)
    return buffer.getvalue()


def generate_json_export(readings: list[TelemetryReading], *, device_id: uuid.UUID, hours: int) -> str:
    payload = {
        "device_id": str(device_id),
        "hours": hours,
        "count": len(readings),
        "exported_at": datetime.now(UTC).isoformat(),
        "readings": [_flatten_reading(r) for r in readings],
    }
    return json.dumps(payload, indent=2, default=str)


def generate_kml(readings: list[TelemetryReading], *, device_id: uuid.UUID, hours: int) -> str:
    coordinates: list[str] = []
    placemarks: list[str] = []

    for reading in readings:
        metrics = reading.metrics or {}
        lat = _metric_float(metrics, "latitude", "lat")
        lon = _metric_float(metrics, "longitude", "lon")
        alt = _metric_float(metrics, "altitude_m", "altitude", "alt") or 0.0
        if lat is None or lon is None:
            continue
        coordinates.append(f"{lon:.7f},{lat:.7f},{alt:.1f}")
        placemarks.append(
            f"""    <Placemark>
      <name>{escape(reading.recorded_at.isoformat())}</name>
      <Point><coordinates>{lon:.7f},{lat:.7f},{alt:.1f}</coordinates></Point>
    </Placemark>"""
        )

    line_string = ""
    if len(coordinates) >= 2:
        line_string = f"""    <Placemark>
      <name>Flight Path</name>
      <LineString>
        <tessellate>1</tessellate>
        <coordinates>{' '.join(coordinates)}</coordinates>
      </LineString>
    </Placemark>
"""

    return f"""<?xml version="1.0" encoding="UTF-8"?>
<kml xmlns="http://www.opengis.net/kml/2.2">
  <Document>
    <name>Telemetry Export — {escape(str(device_id))}</name>
    <description>{hours}h telemetry history ({len(readings)} readings)</description>
{line_string}
{chr(10).join(placemarks)}
  </Document>
</kml>
"""


def render_export(
    readings: list[TelemetryReading],
    *,
    device_id: uuid.UUID,
    hours: int,
    export_format: str,
) -> tuple[str, str, str]:
    fmt = export_format.lower()
    if fmt not in EXPORT_FORMATS:
        raise ValueError(f"format must be one of: {', '.join(sorted(EXPORT_FORMATS))}")

    if fmt == "csv":
        content = generate_csv(readings)
        media_type = "text/csv"
        filename = f"telemetry_{device_id}_{hours}h.csv"
    elif fmt == "json":
        content = generate_json_export(readings, device_id=device_id, hours=hours)
        media_type = "application/json"
        filename = f"telemetry_{device_id}_{hours}h.json"
    else:
        content = generate_kml(readings, device_id=device_id, hours=hours)
        media_type = "application/vnd.google-earth.kml+xml"
        filename = f"telemetry_{device_id}_{hours}h.kml"

    return content, media_type, filename
