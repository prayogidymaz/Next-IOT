"""Auto-register edge devices via provisioning token."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime

from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.devices.edge_agent.models import EdgeDeviceToken
from app.devices.schemas import DeviceRegisterRequest
from app.devices import service as device_service
from app.auth.context import CurrentUser
from app.auth.rbac import UserRole
from app.auth.tiering import SecurityTier
from app.models.device import Device
from app.types.redis_client import RedisClient


class EdgeAgentRegistration:
    async def auto_register(
        self,
        db: AsyncSession,
        redis: RedisClient,
        device_token: str,
        device_type: str,
        capabilities: list[str],
    ) -> Device:
        token_row = await db.scalar(select(EdgeDeviceToken).where(EdgeDeviceToken.token == device_token))
        if token_row is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid device token")
        if token_row.expires_at is not None and token_row.expires_at < datetime.now(tz=UTC):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Device token expired")
        count = await db.scalar(
            select(func.count())
            .select_from(Device)
            .where(Device.tenant_id == token_row.tenant_id, Device.device_type == device_type)
        )
        if count is not None and count >= token_row.max_devices:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Device token limit reached")
        pseudo_user = CurrentUser(
            user_id=uuid.uuid4(),
            tenant_id=token_row.tenant_id,
            email="edge-agent@internal",
            role=UserRole.TENANT_ADMIN,
            security_tier=SecurityTier.FREE,
        )
        metadata = {f"capability_{idx}": cap for idx, cap in enumerate(capabilities)}
        payload = DeviceRegisterRequest(name=f"edge-{device_type}-{uuid.uuid4().hex[:8]}", device_type=device_type, metadata=metadata)
        registered = await device_service.register_device(db, redis, pseudo_user, payload)
        device = await db.get(Device, registered.device.id)
        if device is None:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Registration failed")
        return device
