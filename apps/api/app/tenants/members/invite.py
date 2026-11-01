"""Tenant member email invitations (SMTP stub)."""

from __future__ import annotations

import hashlib
import logging
import secrets
import uuid
from datetime import UTC, datetime, timedelta

from fastapi import HTTPException, status
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.context import CurrentUser
from app.tenants import service as tenant_service
from app.tenants.models import TenantMemberInvitation

logger = logging.getLogger(__name__)


class InviteEmailRequest(BaseModel):
    email: EmailStr
    role: str = Field(description="tenant_admin | operator | viewer")


class InvitationView(BaseModel):
    id: uuid.UUID
    email: str
    role: str
    status: str
    expires_at: datetime
    created_at: datetime

    model_config = {"from_attributes": True}


async def create_email_invite(
    db: AsyncSession,
    user: CurrentUser,
    tenant_id: uuid.UUID,
    payload: InviteEmailRequest,
) -> InvitationView:
    await tenant_service.assert_tenant_admin(db, user, tenant_id)
    role = tenant_service.normalize_member_role(payload.role)
    token = secrets.token_urlsafe(32)
    token_hash = hashlib.sha256(token.encode("utf-8")).hexdigest()
    row = TenantMemberInvitation(
        tenant_id=tenant_id,
        email=payload.email.lower(),
        role=role,
        status="sent",
        token_hash=token_hash,
        expires_at=datetime.now(tz=UTC) + timedelta(days=7),
    )
    db.add(row)
    await db.commit()
    await db.refresh(row)
    logger.info("Invite email stub tenant=%s email=%s token=%s", tenant_id, payload.email, token[:8])
    return InvitationView.model_validate(row)


async def list_invitations(db: AsyncSession, user: CurrentUser, tenant_id: uuid.UUID) -> list[InvitationView]:
    await tenant_service.assert_tenant_admin(db, user, tenant_id)
    rows = await db.scalars(
        select(TenantMemberInvitation)
        .where(TenantMemberInvitation.tenant_id == tenant_id)
        .order_by(TenantMemberInvitation.created_at.desc())
    )
    return [InvitationView.model_validate(r) for r in rows.all()]


async def cancel_invitation(db: AsyncSession, user: CurrentUser, tenant_id: uuid.UUID, invite_id: uuid.UUID) -> None:
    await tenant_service.assert_tenant_admin(db, user, tenant_id)
    row = await db.get(TenantMemberInvitation, invite_id)
    if row is None or row.tenant_id != tenant_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invitation not found")
    row.status = "expired"
    await db.commit()


async def resend_invitation(db: AsyncSession, user: CurrentUser, tenant_id: uuid.UUID, invite_id: uuid.UUID) -> InvitationView:
    await tenant_service.assert_tenant_admin(db, user, tenant_id)
    row = await db.get(TenantMemberInvitation, invite_id)
    if row is None or row.tenant_id != tenant_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invitation not found")
    row.status = "sent"
    row.expires_at = datetime.now(tz=UTC) + timedelta(days=7)
    await db.commit()
    await db.refresh(row)
    logger.info("Resend invite stub email=%s invite=%s", row.email, row.id)
    return InvitationView.model_validate(row)
