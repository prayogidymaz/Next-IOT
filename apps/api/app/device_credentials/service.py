"""Device credential lifecycle (strict typing)."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime

from app.auth.dependencies import CurrentUser
from app.device_credentials.schemas import (
    DeviceCredentialCreateResponse,
    DeviceCredentialPublicResponse,
)
from app.devices.security import generate_client_secret, hash_device_secret
from app.models.device import Device
from app.models.device_credential import (
    CredentialType,
    DeviceCredential,
    device_short_id,
    generate_access_token,
    generate_mqtt_client_id,
)
from app.models.tenant import Tenant
from app.mqtt_auth.cache import invalidate_cached_credential
from app.types.redis_client import RedisClient
from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession


async def _get_device_for_user(
    db: AsyncSession, device_id: uuid.UUID, user: CurrentUser
) -> Device:
    query = select(Device).where(Device.id == device_id)
    if not user.is_super_admin:
        query = query.where(Device.tenant_id == user.tenant_id)
    device = await db.scalar(query)
    if device is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Device not found")
    return device


async def _tenant_slug(db: AsyncSession, tenant_id: uuid.UUID) -> str:
    slug = await db.scalar(select(Tenant.slug).where(Tenant.id == tenant_id))
    if slug is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tenant not found")
    return slug


async def get_active_credential(
    db: AsyncSession, device_id: uuid.UUID, user: CurrentUser
) -> DeviceCredentialPublicResponse:
    await _get_device_for_user(db, device_id, user)
    credential = await db.scalar(
        select(DeviceCredential).where(
            DeviceCredential.device_id == device_id,
            DeviceCredential.is_active.is_(True),
        )
    )
    if credential is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No active credential")
    return DeviceCredentialPublicResponse.from_model(credential)


async def _deactivate_active(
    db: AsyncSession,
    redis: RedisClient,
    device_id: uuid.UUID,
    *,
    mark_rotated: bool,
) -> None:
    active_rows = await db.scalars(
        select(DeviceCredential).where(
            DeviceCredential.device_id == device_id,
            DeviceCredential.is_active.is_(True),
        )
    )
    now = datetime.now(UTC)
    for row in active_rows.all():
        row.is_active = False
        row.updated_at = now
        if mark_rotated:
            row.rotated_at = now
        await invalidate_cached_credential(redis, row.access_token)


async def create_access_token_credential(
    db: AsyncSession,
    redis: RedisClient,
    device: Device,
    *,
    include_basic_secret: bool = False,
) -> DeviceCredentialCreateResponse:
    await _deactivate_active(db, redis, device.id, mark_rotated=False)
    tenant_slug = await _tenant_slug(db, device.tenant_id)
    short = device_short_id(device.id)
    prior = await db.scalar(
        select(DeviceCredential.client_id)
        .where(DeviceCredential.device_id == device.id)
        .order_by(DeviceCredential.created_at.desc())
        .limit(1)
    )
    client_id = prior if prior is not None else generate_mqtt_client_id(tenant_slug, short)
    access_token = generate_access_token()
    secret_plain: str | None = None
    secret_hash: str | None = None
    cred_type = CredentialType.ACCESS_TOKEN
    if include_basic_secret:
        secret_plain = generate_client_secret()
        secret_hash = hash_device_secret(secret_plain)
        cred_type = CredentialType.BASIC_AUTH

    credential = DeviceCredential(
        device_id=device.id,
        tenant_id=device.tenant_id,
        credential_type=cred_type,
        access_token=access_token,
        client_id=client_id,
        secret_hash=secret_hash,
        is_active=True,
    )
    db.add(credential)
    await db.flush()
    return DeviceCredentialCreateResponse.from_created(
        credential,
        access_token=access_token,
        client_secret=secret_plain,
    )


async def generate_credential(
    db: AsyncSession,
    redis: RedisClient,
    user: CurrentUser,
    device_id: uuid.UUID,
) -> DeviceCredentialCreateResponse:
    device = await _get_device_for_user(db, device_id, user)
    return await create_access_token_credential(db, redis, device, include_basic_secret=False)


async def rotate_credential(
    db: AsyncSession,
    redis: RedisClient,
    user: CurrentUser,
    device_id: uuid.UUID,
) -> DeviceCredentialCreateResponse:
    device = await _get_device_for_user(db, device_id, user)
    credential = await db.scalar(
        select(DeviceCredential).where(
            DeviceCredential.device_id == device.id,
            DeviceCredential.is_active.is_(True),
        )
    )
    if credential is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No active credential")

    old_token = credential.access_token
    now = datetime.now(UTC)
    credential.access_token = generate_access_token()
    credential.rotated_at = now
    credential.updated_at = now
    await invalidate_cached_credential(redis, old_token)
    await db.flush()
    return DeviceCredentialCreateResponse.from_created(
        credential,
        access_token=credential.access_token,
        client_secret=None,
    )


async def revoke_credential(
    db: AsyncSession,
    redis: RedisClient,
    user: CurrentUser,
    device_id: uuid.UUID,
) -> None:
    await _get_device_for_user(db, device_id, user)
    await _deactivate_active(db, redis, device_id, mark_rotated=False)


async def lookup_active_by_access_token(
    db: AsyncSession, access_token: str
) -> DeviceCredential | None:
    if not access_token:
        return None
    row: DeviceCredential | None = await db.scalar(
        select(DeviceCredential).where(
            DeviceCredential.access_token == access_token,
            DeviceCredential.is_active.is_(True),
        )
    )
    return row
