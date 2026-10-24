"""Mesh event query service."""

from __future__ import annotations

import uuid
from datetime import datetime

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import CurrentUser
from app.mesh.event_bus import MeshDomain
from app.mesh.schemas import MeshEventResponse
from app.models.device import Device
from app.models.mesh_event import MeshEventRecord
from app.types.json_types import JsonObject


async def _ensure_device_access(db: AsyncSession, user: CurrentUser, device_id: uuid.UUID) -> None:
    device = await db.scalar(select(Device).where(Device.id == device_id))
    if device is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Device not found")
    if not user.is_super_admin and device.tenant_id != user.tenant_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")


async def publish_mesh_event_for_user(
    db: AsyncSession,
    user: CurrentUser,
    *,
    device_id: uuid.UUID,
    domain: MeshDomain,
    event_type: str,
    payload: JsonObject,
    correlation_id: uuid.UUID | None,
    parent_event_id: uuid.UUID | None,
    context: object | None,
) -> MeshEventResponse:
    from app.mesh.publisher import get_mesh_publisher
    from app.mesh.schemas import MeshContext

    await _ensure_device_access(db, user, device_id)
    publisher = get_mesh_publisher()
    if publisher is None:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Mesh publisher unavailable")
    device = await db.scalar(select(Device).where(Device.id == device_id))
    if device is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Device not found")
    tenant_id = device.tenant_id
    if not user.is_super_admin and tenant_id != user.tenant_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
    mesh_context = context if isinstance(context, MeshContext) else None
    event_id = await publisher.publish_event(
        db,
        tenant_id=tenant_id,
        domain=domain,
        event_type=event_type,
        device_id=device_id,
        payload=payload,
        context=mesh_context,
        correlation_id=correlation_id,
        parent_event_id=parent_event_id,
    )
    row = await db.scalar(select(MeshEventRecord).where(MeshEventRecord.id == event_id))
    if row is None:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Event persist failed")
    return MeshEventResponse.from_record(row)


async def list_mesh_events(
    db: AsyncSession,
    user: CurrentUser,
    *,
    domain: MeshDomain | None,
    event_type: str | None,
    device_id: uuid.UUID | None,
    since: datetime | None,
    until: datetime | None,
    limit: int,
) -> list[MeshEventResponse]:
    query = select(MeshEventRecord).order_by(MeshEventRecord.timestamp.desc()).limit(limit)
    if not user.is_super_admin:
        query = query.where(MeshEventRecord.tenant_id == user.tenant_id)
    if domain is not None:
        query = query.where(MeshEventRecord.domain == domain.value)
    if event_type is not None:
        query = query.where(MeshEventRecord.event_type == event_type)
    if device_id is not None:
        await _ensure_device_access(db, user, device_id)
        query = query.where(MeshEventRecord.device_id == device_id)
    if since is not None:
        query = query.where(MeshEventRecord.timestamp >= since)
    if until is not None:
        query = query.where(MeshEventRecord.timestamp <= until)
    rows = await db.scalars(query)
    return [MeshEventResponse.from_record(row) for row in rows.all()]


async def get_mesh_event(db: AsyncSession, user: CurrentUser, event_id: uuid.UUID) -> MeshEventResponse:
    row = await db.scalar(select(MeshEventRecord).where(MeshEventRecord.id == event_id))
    if row is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Event not found")
    if not user.is_super_admin and row.tenant_id != user.tenant_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
    return MeshEventResponse.from_record(row)


async def mesh_event_chain(db: AsyncSession, user: CurrentUser, event_id: uuid.UUID) -> list[MeshEventResponse]:
    root = await get_mesh_event(db, user, event_id)
    chain: list[MeshEventResponse] = [root]
    current_parent = root.parent_event_id
    while current_parent is not None:
        parent = await get_mesh_event(db, user, current_parent)
        chain.append(parent)
        current_parent = parent.parent_event_id
    if root.correlation_id is not None:
        related = await db.scalars(
            select(MeshEventRecord)
            .where(MeshEventRecord.correlation_id == root.correlation_id)
            .order_by(MeshEventRecord.timestamp.asc())
        )
        for row in related.all():
            item = MeshEventResponse.from_record(row)
            if item.event_id not in {c.event_id for c in chain}:
                chain.append(item)
    return chain
