"""Create/clear alarms from telemetry validation."""

from __future__ import annotations

import uuid

from pydantic import JsonValue
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.alarms.fingerprint import alarm_fingerprint, dedup_key_from_details
from app.alarms.service import clear_alarm, upsert_alarm
from app.models.alarm import Alarm, AlarmStatus
from app.telemetry.ingest_pipeline import TelemetryRejectedMetric


async def handle_rejected_metrics_alarms(
    db: AsyncSession,
    *,
    tenant_id: uuid.UUID,
    device_id: uuid.UUID,
    rejected: tuple[TelemetryRejectedMetric, ...],
) -> None:
    for entry in rejected:
        details: dict[str, JsonValue] = {
            "metric_key": entry.key,
            "metric_value": entry.value,
            "reason": entry.reason,
        }
        await upsert_alarm(
            db,
            tenant_id=tenant_id,
            device_id=device_id,
            alarm_type="validation_failed",
            severity="minor",
            title=f"Validation failed: {entry.key}",
            message=f"Metric {entry.key} rejected ({entry.reason})",
            details=details,
            source="validator",
        )


async def clear_validation_alarms_for_metrics(
    db: AsyncSession,
    *,
    tenant_id: uuid.UUID,
    device_id: uuid.UUID,
    metric_keys: set[str],
) -> None:
    for key in metric_keys:
        fp = alarm_fingerprint(
            tenant_id=tenant_id,
            device_id=device_id,
            alarm_type="validation_failed",
            dedup_key=dedup_key_from_details({"metric_key": key}),
        )
        row = await db.scalar(
            select(Alarm).where(
                Alarm.fingerprint == fp,
                Alarm.status.in_([AlarmStatus.ACTIVE, AlarmStatus.ACKNOWLEDGED]),
            )
        )
        if row is not None:
            await clear_alarm(db, row)
