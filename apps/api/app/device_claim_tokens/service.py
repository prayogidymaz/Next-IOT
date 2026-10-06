"""QR claim token lifecycle."""

from __future__ import annotations

import secrets
import uuid
from datetime import UTC, datetime, timedelta

from app.auth.dependencies import CurrentUser
from app.config import settings
from app.device_claim_tokens.schemas import (
    DeviceClaimResultResponse,
    DeviceClaimTokenCreateRequest,
    DeviceClaimTokenResponse,
)
from app.device_credentials.service import create_access_token_credential
from app.models.device import Device, DeviceStatus
from app.models.device_claim_token import DeviceClaimToken
from app.models.device_profile import DeviceProfile, ProfileStatus
from app.models.tenant import Tenant
from app.types.redis_client import RedisClient
from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession


def _qr_url(tenant_slug: str, claim_token: str) -> str:
    return f"nextiot://claim?token={claim_token}&tenant={tenant_slug}"


def _generate_claim_token() -> str:
    return secrets.token_urlsafe(16)[:32]


async def _tenant_for_user(db: AsyncSession, user: CurrentUser) -> Tenant:
    tenant = await db.scalar(select(Tenant).where(Tenant.id == user.tenant_id))
    if tenant is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tenant not found")
    return tenant


async def create_claim_token(
    db: AsyncSession,
    user: CurrentUser,
    payload: DeviceClaimTokenCreateRequest,
) -> DeviceClaimTokenResponse:
    max_hours = settings.device_claim_token_max_ttl_hours
    ttl_hours = min(payload.ttl_hours, max_hours)
    tenant = await _tenant_for_user(db, user)

    if payload.profile_id is not None:
        profile = await db.scalar(
            select(DeviceProfile).where(
                DeviceProfile.id == payload.profile_id,
                DeviceProfile.tenant_id == tenant.id,
                DeviceProfile.status == ProfileStatus.PUBLISHED,
            )
        )
        if profile is None:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Invalid profile_id")

    row = DeviceClaimToken(
        tenant_id=tenant.id,
        claim_token=_generate_claim_token(),
        device_name=payload.device_name,
        device_type=payload.device_type,
        device_category=payload.device_category,
        profile_id=payload.profile_id,
        expires_at=datetime.now(UTC) + timedelta(hours=ttl_hours),
        created_by_user_id=user.user_id,
    )
    db.add(row)
    await db.flush()
    return DeviceClaimTokenResponse.from_model(row, qr_code_url=_qr_url(tenant.slug, row.claim_token))


async def list_claim_tokens(db: AsyncSession, user: CurrentUser) -> list[DeviceClaimTokenResponse]:
    tenant = await _tenant_for_user(db, user)
    rows = await db.scalars(
        select(DeviceClaimToken)
        .where(DeviceClaimToken.tenant_id == tenant.id)
        .order_by(DeviceClaimToken.created_at.desc())
    )
    return [
        DeviceClaimTokenResponse.from_model(row, qr_code_url=_qr_url(tenant.slug, row.claim_token))
        for row in rows.all()
    ]


async def revoke_claim_token(db: AsyncSession, user: CurrentUser, token_id: uuid.UUID) -> None:
    row = await db.scalar(
        select(DeviceClaimToken).where(
            DeviceClaimToken.id == token_id,
            DeviceClaimToken.tenant_id == user.tenant_id,
        )
    )
    if row is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Claim token not found")
    if row.is_claimed():
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Claim token already used")
    await db.delete(row)


async def claim_device(
    db: AsyncSession,
    redis: RedisClient,
    claim_token: str,
) -> DeviceClaimResultResponse:
    row = await db.scalar(select(DeviceClaimToken).where(DeviceClaimToken.claim_token == claim_token))
    if row is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Claim token not found")
    if row.is_claimed():
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Claim token already used")
    if row.is_expired():
        raise HTTPException(status_code=status.HTTP_410_GONE, detail="Claim token expired")

    device = Device(
        tenant_id=row.tenant_id,
        name=row.device_name,
        device_type=row.device_type,
        device_category=row.device_category,
        profile_id=row.profile_id,
        status=DeviceStatus.ONLINE,
    )
    db.add(device)
    await db.flush()

    created = await create_access_token_credential(db, redis, device, include_basic_secret=False)
    row.claimed_at = datetime.now(UTC)
    row.claimed_device_id = device.id

    topic_prefix = f"tenants/{device.tenant_id}/devices/{device.id}"
    return DeviceClaimResultResponse(
        device_id=device.id,
        access_token=created.access_token,
        mqtt_broker_url=settings.mqtt_broker_url_external,
        client_id=created.client_id,
        topic_prefix=topic_prefix,
    )
