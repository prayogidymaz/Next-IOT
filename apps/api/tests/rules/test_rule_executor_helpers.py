"""Shared helpers for rule executor DB tests."""

from __future__ import annotations

import uuid

from app.models.device import Device, DeviceStatus
from app.models.tenant import Tenant
from sqlalchemy.ext.asyncio import AsyncSession


async def add_tenant_and_device(
    db: AsyncSession,
    *,
    tenant_id: uuid.UUID | None = None,
    device_id: uuid.UUID | None = None,
    device_name: str = "Sensor",
) -> tuple[uuid.UUID, uuid.UUID, Device]:
    tenant_id = tenant_id or uuid.uuid4()
    device_id = device_id or uuid.uuid4()
    db.add(
        Tenant(
            id=tenant_id,
            name="Test tenant",
            slug=f"t-{tenant_id.hex[:10]}",
            is_active=True,
        )
    )
    device = Device(
        id=device_id,
        tenant_id=tenant_id,
        name=device_name,
        device_type="temp",
        status=DeviceStatus.ONLINE,
    )
    db.add(device)
    await db.flush()
    return tenant_id, device_id, device
