"""Telemetry export service — fetch readings and render downloadable payloads."""

from __future__ import annotations

import uuid
from datetime import datetime

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import CurrentUser
from app.models.telemetry_reading import TelemetryReading
from app.telemetry.export_generator import render_export

MAX_EXPORT_SAMPLES = 50_000


async def fetch_export_readings(
    db: AsyncSession,
    user: CurrentUser,
    *,
    device_id: uuid.UUID,
    start: datetime,
    end: datetime,
) -> list[TelemetryReading]:
    from app.telemetry.timeseries import fetch_readings_window

    readings = await fetch_readings_window(
        db, user, device_id=device_id, start=start, end=end
    )
    return readings[:MAX_EXPORT_SAMPLES]


async def export_telemetry(
    db: AsyncSession,
    user: CurrentUser,
    *,
    device_id: uuid.UUID,
    export_format: str,
    hours: int | None = 24,
    start_time: datetime | None = None,
    end_time: datetime | None = None,
) -> tuple[str, str, str]:
    from app.telemetry.timeseries import resolve_time_window

    start, end = resolve_time_window(start_time=start_time, end_time=end_time, hours=hours)
    if start >= end:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="start_time must be before end_time",
        )

    readings = await fetch_export_readings(
        db, user, device_id=device_id, start=start, end=end
    )

    lookback_hours = hours if hours is not None else max(1, int((end - start).total_seconds() // 3600))

    try:
        return render_export(
            readings,
            device_id=device_id,
            hours=lookback_hours,
            export_format=export_format,
        )
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)) from exc
