"""Flight telemetry analytics summary aggregator."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime, timedelta
from typing import Any

from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import CurrentUser
from app.devices.service import _get_device_for_user
from app.models.telemetry_anomaly import TelemetryAnomaly
from app.models.telemetry_reading import TelemetryReading
from app.telemetry.schemas import TelemetryAnalyticsResponse
from app.telemetry.swarm_distance import SwarmDistanceCalculator

ALLOWED_HOURS = frozenset({1, 24})
MAX_READINGS = 5000


def _metric_float(metrics: dict[str, Any], *keys: str) -> float | None:
    for key in keys:
        if key in metrics and metrics[key] is not None:
            try:
                return float(metrics[key])
            except (TypeError, ValueError):
                continue
    return None


def _compute_total_distance_m(readings: list[TelemetryReading]) -> float:
    calculator = SwarmDistanceCalculator()
    total = 0.0
    prev_lat: float | None = None
    prev_lon: float | None = None

    for reading in readings:
        metrics = reading.metrics or {}
        lat = _metric_float(metrics, "latitude", "lat")
        lon = _metric_float(metrics, "longitude", "lon")
        if lat is None or lon is None:
            continue
        if prev_lat is not None and prev_lon is not None:
            total += calculator.haversine_m(prev_lat, prev_lon, lat, lon)
        prev_lat, prev_lon = lat, lon

    return round(total, 2)


def _aggregate_readings(readings: list[TelemetryReading]) -> dict[str, float | None]:
    speeds: list[float] = []
    altitudes: list[float] = []
    voltages: list[float] = []

    for reading in readings:
        metrics = reading.metrics or {}
        speed = _metric_float(metrics, "speed", "speed_mps", "ground_speed", "velocity")
        altitude = _metric_float(metrics, "altitude_m", "altitude", "alt")
        voltage = _metric_float(metrics, "voltage", "battery_voltage", "batt_voltage")

        if speed is not None:
            speeds.append(speed)
        if altitude is not None:
            altitudes.append(altitude)
        if voltage is not None:
            voltages.append(voltage)

    max_speed = round(max(speeds), 2) if speeds else None
    avg_altitude = round(sum(altitudes) / len(altitudes), 2) if altitudes else None
    min_voltage = round(min(voltages), 2) if voltages else None

    return {
        "max_speed_m_s": max_speed,
        "avg_altitude_m": avg_altitude,
        "min_voltage_v": min_voltage,
    }


async def get_telemetry_analytics(
    db: AsyncSession,
    user: CurrentUser,
    *,
    device_id: uuid.UUID,
    hours: int = 24,
) -> TelemetryAnalyticsResponse:
    if hours not in ALLOWED_HOURS:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="hours must be 1 or 24",
        )

    await _get_device_for_user(db, device_id, user)
    since = datetime.now(UTC) - timedelta(hours=hours)

    reading_query = (
        select(TelemetryReading)
        .where(
            TelemetryReading.device_id == device_id,
            TelemetryReading.recorded_at >= since,
        )
        .order_by(TelemetryReading.recorded_at.asc())
        .limit(MAX_READINGS)
    )
    if not user.is_super_admin:
        reading_query = reading_query.where(TelemetryReading.tenant_id == user.tenant_id)

    readings = (await db.scalars(reading_query)).all()
    stats = _aggregate_readings(readings)
    total_distance_m = _compute_total_distance_m(readings)

    anomaly_query = select(func.count()).select_from(TelemetryAnomaly).where(
        TelemetryAnomaly.device_id == device_id,
        TelemetryAnomaly.recorded_at >= since,
    )
    if not user.is_super_admin:
        anomaly_query = anomaly_query.where(TelemetryAnomaly.tenant_id == user.tenant_id)

    anomaly_count = int(await db.scalar(anomaly_query) or 0)

    return TelemetryAnalyticsResponse(
        device_id=device_id,
        hours=hours,
        reading_count=len(readings),
        max_speed_m_s=stats["max_speed_m_s"],
        avg_altitude_m=stats["avg_altitude_m"],
        min_voltage_v=stats["min_voltage_v"],
        total_distance_m=total_distance_m,
        anomaly_count=anomaly_count,
    )
