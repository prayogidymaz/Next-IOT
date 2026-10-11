"""Daily usage snapshots."""

from __future__ import annotations

import uuid
from datetime import UTC, date, datetime

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.billing.quota import get_message_count
from app.models.device import Device
from app.models.tenant_usage_daily import TenantUsageDaily
from app.models.user import User
from app.types.redis_client import RedisClient


async def snapshot_tenant_usage(
    db: AsyncSession,
    redis: RedisClient,
    tenant_id: uuid.UUID,
    usage_date: date | None = None,
) -> TenantUsageDaily:
    day = usage_date or datetime.now(tz=UTC).date()
    existing = await db.scalar(
        select(TenantUsageDaily).where(
            TenantUsageDaily.tenant_id == tenant_id,
            TenantUsageDaily.usage_date == day,
        )
    )
    device_count = int(
        await db.scalar(select(func.count()).select_from(Device).where(Device.tenant_id == tenant_id)) or 0
    )
    user_count = int(
        await db.scalar(select(func.count()).select_from(User).where(User.tenant_id == tenant_id)) or 0
    )
    messages = await get_message_count(redis, tenant_id)
    if existing is None:
        row = TenantUsageDaily(
            tenant_id=tenant_id,
            usage_date=day,
            device_count=device_count,
            active_user_count=user_count,
            messages_count=messages,
            api_calls_count=0,
            storage_bytes=0,
        )
        db.add(row)
        await db.flush()
        return row
    existing.device_count = device_count
    existing.active_user_count = user_count
    existing.messages_count = messages
    await db.flush()
    return existing
