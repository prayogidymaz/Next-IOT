"""Flight replay — full telemetry time series for mission playback."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime, timedelta
from typing import Any

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import CurrentUser
from app.devices.service import _get_device_for_user
from app.models.telemetry_anomaly import TelemetryAnomaly
from app.models.telemetry_reading import TelemetryReading
from app.telemetry.schemas import (
    FlightReplayAnomalyBrief,
    FlightReplayResponse,
    FlightReplaySample,
)

ALLOWED_HOURS = frozenset({1, 24})
MAX_SAMPLES = 2000


def _metric_float(metrics: dict[str, Any], *keys: str) -> float | None:
    for key in keys:
        if key in metrics and metrics[key] is not None:
            try:
                return float(metrics[key])
            except (TypeError, ValueError):
                continue
    return None


def _build_sample(
    reading: TelemetryReading,
    anomalies_by_reading: dict[uuid.UUID, list[TelemetryAnomaly]],
) -> FlightReplaySample | None:
    metrics = reading.metrics or {}
    lat = _metric_float(metrics, "latitude", "lat")
    lon = _metric_float(metrics, "longitude", "lon")
    if lat is None or lon is None:
        return None

    linked = anomalies_by_reading.get(reading.id, [])
    return FlightReplaySample(
        timestamp=reading.recorded_at,
        lat=round(lat, 7),
        lon=round(lon, 7),
        alt=_metric_float(metrics, "altitude_m", "altitude", "alt"),
        speed=_metric_float(metrics, "speed", "speed_mps", "ground_speed", "velocity"),
        heading=_metric_float(metrics, "yaw", "heading", "course"),
        rssi=_metric_float(metrics, "rssi", "signal_rssi"),
        anomalies=[
            FlightReplayAnomalyBrief(
                id=row.id,
                severity=row.severity,
                anomaly_type=row.anomaly_type,
                message=row.message,
            )
            for row in linked
        ],
    )


async def get_flight_replay(
    db: AsyncSession,
    user: CurrentUser,
    *,
    device_id: uuid.UUID,
    hours: int | None = 24,
    start_time: datetime | None = None,
    end_time: datetime | None = None,
) -> FlightReplayResponse:
    await _get_device_for_user(db, device_id, user)

    now = datetime.now(UTC)

    def _to_utc(value: datetime) -> datetime:
        if value.tzinfo is None:
            return value.replace(tzinfo=UTC)
        return value.astimezone(UTC)

    if start_time is not None or end_time is not None:
        session_end = _to_utc(end_time) if end_time is not None else now
        session_start = _to_utc(start_time) if start_time is not None else session_end - timedelta(hours=24)
        lookback_hours = None
    else:
        if hours not in ALLOWED_HOURS:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="hours must be 1 or 24 when start_time/end_time are omitted",
            )
        session_end = now
        session_start = now - timedelta(hours=hours)
        lookback_hours = hours

    if session_start >= session_end:
        raise HTTPException(status_code=422, detail="start_time must be before end_time")

    reading_query = (
        select(TelemetryReading)
        .where(
            TelemetryReading.device_id == device_id,
            TelemetryReading.recorded_at >= session_start,
            TelemetryReading.recorded_at <= session_end,
        )
        .order_by(TelemetryReading.recorded_at.asc())
        .limit(MAX_SAMPLES)
    )
    if not user.is_super_admin:
        reading_query = reading_query.where(TelemetryReading.tenant_id == user.tenant_id)

    readings = (await db.scalars(reading_query)).all()

    anomaly_query = (
        select(TelemetryAnomaly)
        .where(
            TelemetryAnomaly.device_id == device_id,
            TelemetryAnomaly.recorded_at >= session_start,
            TelemetryAnomaly.recorded_at <= session_end,
        )
        .order_by(TelemetryAnomaly.recorded_at.asc())
    )
    if not user.is_super_admin:
        anomaly_query = anomaly_query.where(TelemetryAnomaly.tenant_id == user.tenant_id)

    anomalies = (await db.scalars(anomaly_query)).all()
    anomalies_by_reading: dict[uuid.UUID, list[TelemetryAnomaly]] = {}
    for row in anomalies:
        if row.reading_id is None:
            continue
        anomalies_by_reading.setdefault(row.reading_id, []).append(row)

    samples: list[FlightReplaySample] = []
    for reading in readings:
        sample = _build_sample(reading, anomalies_by_reading)
        if sample is not None:
            samples.append(sample)

    effective_start = samples[0].timestamp if samples else session_start
    effective_end = samples[-1].timestamp if samples else session_end

    return FlightReplayResponse(
        device_id=device_id,
        session_start=effective_start,
        session_end=effective_end,
        hours=lookback_hours,
        count=len(samples),
        samples=samples,
    )
