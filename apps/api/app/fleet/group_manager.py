"""Device group CRUD."""

from __future__ import annotations

import uuid

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.context import CurrentUser
from app.fleet.models import DeviceGroup


async def list_groups(db: AsyncSession, user: CurrentUser) -> list[DeviceGroup]:
    rows = await db.scalars(select(DeviceGroup).where(DeviceGroup.tenant_id == user.tenant_id))
    return list(rows.all())


async def create_group(db: AsyncSession, user: CurrentUser, name: str, tag_filter_json: dict[str, object]) -> DeviceGroup:
    row = DeviceGroup(tenant_id=user.tenant_id, name=name, tag_filter_json=tag_filter_json)
    db.add(row)
    await db.commit()
    await db.refresh(row)
    return row


async def get_group(db: AsyncSession, user: CurrentUser, group_id: uuid.UUID) -> DeviceGroup:
    row = await db.get(DeviceGroup, group_id)
    if row is None or row.tenant_id != user.tenant_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Group not found")
    return row
