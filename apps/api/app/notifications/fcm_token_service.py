"""Persist and query tenant user FCM tokens."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import CurrentUser
from app.models.tenant_user_fcm_token import TenantUserFcmToken


async def register_fcm_token(
    db: AsyncSession,
    user: CurrentUser,
    token: str,
    device_type: str,
) -> TenantUserFcmToken:
    existing = await db.scalar(select(TenantUserFcmToken).where(TenantUserFcmToken.token == token))
    now = datetime.now(tz=UTC)
    if existing is not None:
        existing.user_id = user.user_id
        existing.tenant_id = user.tenant_id
        existing.device_type = device_type
        existing.last_seen_at = now
        await db.flush()
        return existing
    row = TenantUserFcmToken(
        tenant_id=user.tenant_id,
        user_id=user.user_id,
        token=token,
        device_type=device_type,
        last_seen_at=now,
    )
    db.add(row)
    await db.flush()
    return row


async def unregister_fcm_token(db: AsyncSession, user: CurrentUser, token: str) -> None:
    await db.execute(
        delete(TenantUserFcmToken).where(
            TenantUserFcmToken.token == token,
            TenantUserFcmToken.user_id == user.user_id,
            TenantUserFcmToken.tenant_id == user.tenant_id,
        )
    )


async def list_user_fcm_tokens(db: AsyncSession, user: CurrentUser) -> list[TenantUserFcmToken]:
    rows = await db.scalars(
        select(TenantUserFcmToken)
        .where(
            TenantUserFcmToken.user_id == user.user_id,
            TenantUserFcmToken.tenant_id == user.tenant_id,
        )
        .order_by(TenantUserFcmToken.last_seen_at.desc())
    )
    return list(rows.all())


async def list_tenant_fcm_tokens(db: AsyncSession, tenant_id: uuid.UUID) -> list[TenantUserFcmToken]:
    rows = await db.scalars(
        select(TenantUserFcmToken).where(TenantUserFcmToken.tenant_id == tenant_id)
    )
    return list(rows.all())


async def delete_fcm_token_by_value(db: AsyncSession, token: str) -> None:
    await db.execute(delete(TenantUserFcmToken).where(TenantUserFcmToken.token == token))
