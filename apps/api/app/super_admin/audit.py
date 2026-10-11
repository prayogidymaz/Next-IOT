"""Persist super-admin audit rows."""

from __future__ import annotations

import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.super_admin_action import SuperAdminAction


async def record_super_admin_action(
    db: AsyncSession,
    *,
    actor_user_id: uuid.UUID,
    action: str,
    target_tenant_id: uuid.UUID | None,
    detail: dict[str, object],
    note: str | None = None,
) -> None:
    db.add(
        SuperAdminAction(
            actor_user_id=actor_user_id,
            action=action,
            target_tenant_id=target_tenant_id,
            detail=detail,
            note=note,
        )
    )
    await db.flush()
