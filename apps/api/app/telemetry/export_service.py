"""Telemetry export service — fetch readings and render downloadable payloads."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime, timedelta

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import CurrentUser
from app.devices.service import _get_device_for_user
from app.models.telemetry_reading import TelemetryReading
from app.telemetry.export_generator import render_export

ALLOWED_HOURS = frozenset({1, 24})
MAX_EXPORT_SAMPLES = 5000


async def export_telemetry(
    db: AsyncSession,
    user: CurrentUser,
    *,
    device_id: uuid.UUID,
    export_format: str,
    hours: int = 24,
) -> tuple[str, str, str]:
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
        .limit(MAX_EXPORT_SAMPLES)
    )
    if not user.is_super_admin:
        query = query.where(TelemetryReading.tenant_id == user.tenant_id)

    readings = (await db.scalars(query)).all()

    try:
        return render_export(
            readings,
            device_id=device_id,
            hours=hours,
            export_format=export_format,
        )
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)) from exc
