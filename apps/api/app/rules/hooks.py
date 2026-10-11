"""Post-persist hooks into the rule executor."""

from __future__ import annotations

import logging
import uuid
from datetime import datetime

from pydantic import JsonValue
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.device import Device
from app.rules.executor import RuleExecutor
from app.types.json_types import numeric_metrics

logger = logging.getLogger(__name__)


async def apply_telemetry_rules(
    executor: RuleExecutor,
    db: AsyncSession,
    *,
    tenant_id: uuid.UUID,
    device_id: uuid.UUID,
    metrics: dict[str, JsonValue],
    recorded_at: datetime,
    reading_id: uuid.UUID | None,
) -> None:
    device = await db.scalar(
        select(Device).where(Device.id == device_id, Device.tenant_id == tenant_id)
    )
    if device is None:
        logger.warning("Rule executor skip telemetry: device %s not found", device_id)
        return
    for metric_key, value in numeric_metrics(dict(metrics)).items():
        try:
            await executor.on_telemetry(
                db,
                device=device,
                metric_key=metric_key,
                value=value,
                recorded_at=recorded_at,
                reading_id=reading_id,
            )
        except Exception:
            logger.exception("Rule executor failed on telemetry %s=%s", metric_key, value)


async def apply_attribute_change_rules(
    executor: RuleExecutor,
    db: AsyncSession,
    *,
    tenant_id: uuid.UUID,
    device_id: uuid.UUID,
    scope: str,
    key: str,
    old_value: JsonValue,
    new_value: JsonValue,
) -> None:
    device = await db.scalar(
        select(Device).where(Device.id == device_id, Device.tenant_id == tenant_id)
    )
    if device is None:
        return
    try:
        await executor.on_attribute_change(
            db,
            device=device,
            scope=scope,
            key=key,
            old_value=old_value,
            new_value=new_value,
        )
    except Exception:
        logger.exception(
            "Rule executor failed on attribute change device=%s scope=%s key=%s",
            device_id,
            scope,
            key,
        )
