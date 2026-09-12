import uuid
from datetime import UTC, datetime, timedelta

import redis.asyncio as aioredis
from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import CurrentUser
from app.config import settings
from app.devices.dependencies import CurrentDevice
from app.devices.service import _get_device_for_user
from app.models.device import DeviceStatus
from app.models.telemetry_reading import TelemetryReading
from app.rules.evaluator import evaluate_rules_for_telemetry
from app.commands.fail_safe import fail_safe_protocol
from app.mission.sar_emergency_service import sar_emergency_service
from app.telemetry.anomaly_detector import detect_and_persist_anomalies
from app.telemetry.cache import cache_latest_telemetry, get_latest_telemetry
from app.telemetry.schemas import (
    TelemetryHistoryItem,
    TelemetryHistoryResponse,
    TelemetryIngestRequest,
    TelemetryIngestResponse,
    TelemetryLatestResponse,
)

INGEST_ALLOWED_STATUSES = frozenset({DeviceStatus.ONLINE})


def _validate_timestamp(ts: datetime) -> datetime:
    if ts.tzinfo is None:
        ts = ts.replace(tzinfo=UTC)
    else:
        ts = ts.astimezone(UTC)

    now = datetime.now(UTC)
    max_future = timedelta(minutes=settings.telemetry_timestamp_max_future_minutes)
    max_past = timedelta(hours=settings.telemetry_timestamp_max_past_hours)

    if ts > now + max_future:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Timestamp is too far in the future",
        )
    if ts < now - max_past:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Timestamp is too far in the past",
        )
    return ts


async def ingest_telemetry(
    db: AsyncSession,
    redis: aioredis.Redis,
    device: CurrentDevice,
    payload: TelemetryIngestRequest,
) -> TelemetryIngestResponse:
    if device.status not in INGEST_ALLOWED_STATUSES:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Device cannot ingest telemetry in status '{device.status}'. Device must be online.",
        )

    recorded_at = _validate_timestamp(payload.timestamp)
    metrics = {k: float(v) if isinstance(v, int) else v for k, v in payload.metrics.items()}

    reading = TelemetryReading(
        device_id=device.device_id,
        tenant_id=device.tenant_id,
        recorded_at=recorded_at,
        metrics=metrics,
    )
    db.add(reading)
    await db.flush()

    await cache_latest_telemetry(
        redis,
        device_id=str(device.device_id),
        tenant_id=str(device.tenant_id),
        recorded_at=recorded_at,
        metrics=metrics,
        reading_id=str(reading.id),
    )

    rules_triggered = await evaluate_rules_for_telemetry(
        db,
        redis,
        device_id=device.device_id,
        tenant_id=device.tenant_id,
        metrics=metrics,
        reading_id=reading.id,
    )

    anomaly_rows = await detect_and_persist_anomalies(
        db,
        device_id=device.device_id,
        tenant_id=device.tenant_id,
        metrics=metrics,
        recorded_at=recorded_at,
        reading_id=reading.id,
    )
    if anomaly_rows:
        for row in anomaly_rows:
            await sar_emergency_service.trigger_from_anomaly(
                db,
                redis,
                tenant_id=device.tenant_id,
                device_id=device.device_id,
                anomaly_type=row.anomaly_type,
                severity=row.severity,
                message=row.message,
                metadata=row.metadata_ or {},
            )
        await fail_safe_protocol.handle_critical_anomalies(
            db,
            redis,
            device_id=device.device_id,
            tenant_id=device.tenant_id,
            anomalies=anomaly_rows,
        )

    return TelemetryIngestResponse(
        reading_id=reading.id,
        device_id=device.device_id,
        tenant_id=device.tenant_id,
        recorded_at=recorded_at,
        metrics=metrics,
        rules_triggered=rules_triggered,
    )


async def get_latest_for_device(
    db: AsyncSession,
    redis: aioredis.Redis,
    user: CurrentUser,
    device_id: uuid.UUID,
) -> TelemetryLatestResponse:
    await _get_device_for_user(db, device_id, user)

    cached = await get_latest_telemetry(redis, str(device_id))
    if cached is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No telemetry data found for device")

    return TelemetryLatestResponse(
        device_id=device_id,
        reading_id=cached.get("reading_id"),
        recorded_at=cached.get("recorded_at"),
        metrics=cached.get("metrics", {}),
        cached_at=cached.get("cached_at"),
    )


async def get_history_for_device(
    db: AsyncSession,
    user: CurrentUser,
    device_id: uuid.UUID,
    *,
    start_time: datetime | None = None,
    end_time: datetime | None = None,
    limit: int = 100,
) -> TelemetryHistoryResponse:
    await _get_device_for_user(db, device_id, user)

    if limit < 1 or limit > 1000:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Limit must be between 1 and 1000")

    query = select(TelemetryReading).where(TelemetryReading.device_id == device_id)
    if not user.is_super_admin:
        query = query.where(TelemetryReading.tenant_id == user.tenant_id)

    if start_time:
        st = start_time.astimezone(UTC) if start_time.tzinfo else start_time.replace(tzinfo=UTC)
        query = query.where(TelemetryReading.recorded_at >= st)
    if end_time:
        et = end_time.astimezone(UTC) if end_time.tzinfo else end_time.replace(tzinfo=UTC)
        query = query.where(TelemetryReading.recorded_at <= et)

    query = query.order_by(TelemetryReading.recorded_at.desc()).limit(limit)
    result = await db.scalars(query)
    readings = result.all()

    items = [
        TelemetryHistoryItem(
            reading_id=r.id,
            recorded_at=r.recorded_at,
            metrics=r.metrics,
            ingested_at=r.ingested_at,
        )
        for r in readings
    ]

    return TelemetryHistoryResponse(device_id=device_id, count=len(items), items=items)
