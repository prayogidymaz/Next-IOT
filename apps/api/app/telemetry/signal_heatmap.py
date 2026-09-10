"""Aggregate RSSI/SNR telemetry into map heatmap points."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime, timedelta
from typing import Any

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import CurrentUser
from app.devices.service import _get_device_for_user
from app.models.telemetry_reading import TelemetryReading
from app.telemetry.schemas import SignalHeatmapPoint, SignalHeatmapResponse

ALLOWED_HOURS = frozenset({1, 24})


def _metric_float(metrics: dict[str, Any], *keys: str) -> float | None:
    for key in keys:
        if key in metrics and metrics[key] is not None:
            try:
                return float(metrics[key])
            except (TypeError, ValueError):
                continue
    return None


def compute_signal_score(rssi: float) -> int:
    """Map RSSI dBm to 0-100 score aligned with heatmap bands."""
    if rssi > -85:
        return int(min(100, max(80, 80 + (rssi + 85) * (20 / 25))))
    if rssi >= -105:
        return int(max(40, min(79, 40 + (rssi + 105) * (39 / 20))))
    return int(max(0, min(39, (rssi + 125) * (39 / 20))))


def classify_signal_strength(rssi: float) -> str:
    if rssi > -85:
        return "strong"
    if rssi >= -105:
        return "marginal"
    return "weak"


def _extract_point(reading: TelemetryReading) -> SignalHeatmapPoint | None:
    metrics = reading.metrics or {}
    lat = _metric_float(metrics, "latitude", "lat")
    lon = _metric_float(metrics, "longitude", "lon")
    rssi = _metric_float(metrics, "rssi")
    if lat is None or lon is None or rssi is None:
        return None

    snr = _metric_float(metrics, "snr")
    return SignalHeatmapPoint(
        lat=lat,
        lon=lon,
        rssi=round(rssi, 1),
        snr=round(snr, 1) if snr is not None else None,
        signal_score=compute_signal_score(rssi),
        signal_strength=classify_signal_strength(rssi),
        recorded_at=reading.recorded_at,
    )


async def get_signal_heatmap(
    db: AsyncSession,
    user: CurrentUser,
    *,
    device_id: uuid.UUID,
    hours: int = 24,
) -> SignalHeatmapResponse:
    if hours not in ALLOWED_HOURS:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="hours must be 1 or 24",
        )

    await _get_device_for_user(db, device_id, user)
    since = datetime.now(UTC) - timedelta(hours=hours)

    query = (
        select(TelemetryReading)
        .where(
            TelemetryReading.device_id == device_id,
            TelemetryReading.recorded_at >= since,
        )
        .order_by(TelemetryReading.recorded_at.asc())
        .limit(2000)
    )
    if not user.is_super_admin:
        query = query.where(TelemetryReading.tenant_id == user.tenant_id)

    readings = (await db.scalars(query)).all()
    points: list[SignalHeatmapPoint] = []
    for reading in readings:
        point = _extract_point(reading)
        if point is not None:
            points.append(point)

    return SignalHeatmapResponse(
        device_id=device_id,
        hours=hours,
        count=len(points),
        points=points,
    )
