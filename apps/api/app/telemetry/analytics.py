"""Flight telemetry analytics summary aggregator."""

from __future__ import annotations

import uuid
from datetime import datetime

from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import CurrentUser
from app.models.telemetry_anomaly import TelemetryAnomaly
from app.models.telemetry_reading import TelemetryReading
from app.telemetry.schemas import TelemetryAnalyticsResponse
from app.telemetry.swarm_distance import SwarmDistanceCalculator
from app.telemetry.timeseries import aggregate_timeseries
from app.types.json_types import metric_float

MAX_READINGS = 5000


def _compute_total_distance_m(readings: list[TelemetryReading]) -> float:
    calculator = SwarmDistanceCalculator()
    total = 0.0
    prev_lat: float | None = None
    prev_lon: float | None = None

    for reading in readings:
        metrics = reading.metrics or {}
        lat = metric_float(metrics, "latitude", "lat")
        lon = metric_float(metrics, "longitude", "lon")
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
        speed = metric_float(metrics, "speed", "speed_mps", "ground_speed", "velocity")
        altitude = metric_float(metrics, "altitude_m", "altitude", "alt")
        voltage = metric_float(metrics, "voltage", "battery_voltage", "batt_voltage")

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
    hours: int | None = 24,
    metrics: list[str] | None = None,
    start_time: datetime | None = None,
    end_time: datetime | None = None,
    interval: str = "5m",
) -> TelemetryAnalyticsResponse:
    from app.telemetry.timeseries import (
        fetch_readings_window,
        parse_interval,
        resolve_time_window,
    )

    try:
        bucket = parse_interval(interval)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)) from exc

    start, end = resolve_time_window(start_time=start_time, end_time=end_time, hours=hours)
    if start >= end:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="start_time must be before end_time",
        )

    readings = await fetch_readings_window(db, user, device_id=device_id, start=start, end=end)
    if len(readings) > MAX_READINGS:
        readings = readings[:MAX_READINGS]
    stats = _aggregate_readings(readings)
    total_distance_m = _compute_total_distance_m(readings)

    anomaly_query = select(func.count()).select_from(TelemetryAnomaly).where(
        TelemetryAnomaly.device_id == device_id,
        TelemetryAnomaly.recorded_at >= start,
        TelemetryAnomaly.recorded_at <= end,
    )
    if not user.is_super_admin:
        anomaly_query = anomaly_query.where(TelemetryAnomaly.tenant_id == user.tenant_id)

    anomaly_count = int(await db.scalar(anomaly_query) or 0)

    metric_list = metrics or []
    raw_series = aggregate_timeseries(readings, metrics=metric_list, interval=bucket)

    from app.telemetry.schemas import MetricStatsSummary, MetricTimeSeries, TimeSeriesBucketPoint

    series = [
        MetricTimeSeries(
            metric=item["metric"],
            stats=MetricStatsSummary(**item["stats"]),
            points=[TimeSeriesBucketPoint(**p) for p in item["points"]],
        )
        for item in raw_series
    ]

    lookback_hours = hours
    if lookback_hours is None:
        lookback_hours = max(1, int((end - start).total_seconds() // 3600))

    return TelemetryAnalyticsResponse(
        device_id=device_id,
        start_time=start,
        end_time=end,
        interval=interval,
        hours=lookback_hours,
        reading_count=len(readings),
        max_speed_m_s=stats["max_speed_m_s"],
        avg_altitude_m=stats["avg_altitude_m"],
        min_voltage_v=stats["min_voltage_v"],
        total_distance_m=total_distance_m,
        anomaly_count=anomaly_count,
        series=series,
    )
