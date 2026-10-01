from __future__ import annotations

import uuid
from datetime import datetime

from app.auth.context import CurrentUser
from app.models.audit_log import AuditLog
from fastapi import Request
from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession


def client_ip(request: Request | None) -> str | None:
    if request is None:
        return None
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        return forwarded.split(",")[0].strip()
    if request.client:
        return request.client.host
    return None


async def record_audit_event(
    db: AsyncSession,
    *,
    action: str,
    actor_email: str,
    resource_target: str = "",
    status: str = "success",
    actor_id: uuid.UUID | None = None,
    tenant_id: uuid.UUID | None = None,
    ip_address: str | None = None,
) -> None:
    entry = AuditLog(
        actor_id=actor_id,
        actor_email=actor_email,
        tenant_id=tenant_id,
        action=action,
        resource_target=resource_target[:512],
        ip_address=ip_address,
        status=status,
    )
    db.add(entry)
    await db.commit()


async def list_audit_logs(
    db: AsyncSession,
    user: CurrentUser,
    *,
    action: str | None = None,
    actor_query: str | None = None,
    start_time: datetime | None = None,
    end_time: datetime | None = None,
    page: int = 1,
    page_size: int = 50,
) -> tuple[list[AuditLog], int]:
    page_size = min(max(page_size, 1), 200)
    page = max(page, 1)

    stmt = select(AuditLog)
    count_stmt = select(func.count()).select_from(AuditLog)

    if not user.is_super_admin:
        stmt = stmt.where(AuditLog.tenant_id == user.tenant_id)
        count_stmt = count_stmt.where(AuditLog.tenant_id == user.tenant_id)

    if action:
        stmt = stmt.where(AuditLog.action == action.upper())
        count_stmt = count_stmt.where(AuditLog.action == action.upper())
    if actor_query:
        pattern = f"%{actor_query.strip()}%"
        stmt = stmt.where(
            or_(AuditLog.actor_email.ilike(pattern), AuditLog.resource_target.ilike(pattern))
        )
        count_stmt = count_stmt.where(
            or_(AuditLog.actor_email.ilike(pattern), AuditLog.resource_target.ilike(pattern))
        )
    if start_time:
        stmt = stmt.where(AuditLog.timestamp >= start_time)
        count_stmt = count_stmt.where(AuditLog.timestamp >= start_time)
    if end_time:
        stmt = stmt.where(AuditLog.timestamp <= end_time)
        count_stmt = count_stmt.where(AuditLog.timestamp <= end_time)

    total = int(await db.scalar(count_stmt) or 0)
    offset = (page - 1) * page_size
    rows = await db.scalars(
        stmt.order_by(AuditLog.timestamp.desc()).offset(offset).limit(page_size)
    )
    return list(rows.all()), total
