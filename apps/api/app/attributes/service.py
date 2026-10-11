"""Device attributes CRUD (server / shared / client scopes)."""

from __future__ import annotations

import uuid

from fastapi import HTTPException, status
from pydantic import JsonValue
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.attributes.broadcast import broadcast_shared_attribute_update
from app.attributes.schemas import (
    AttributeScopeParam,
    DeviceAttributeItem,
    DeviceAttributeListResponse,
    DeviceAttributePutResponse,
    validate_attribute_key,
)
from app.auth.context import CurrentUser
from app.config import settings
from app.devices.service import _get_device_for_user
from app.models.device_attribute import DeviceAttribute, DeviceAttributeScope
from app.mqtt_publisher.protocol import MqttPublisherProtocol


def _validate_key_http(key: str) -> None:
    try:
        validate_attribute_key(key)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        ) from exc


def _scope_from_param(scope: AttributeScopeParam) -> DeviceAttributeScope:
    return DeviceAttributeScope(scope.value)


def _attribute_value(row: DeviceAttribute) -> JsonValue:
    stored = row.value_json
    if isinstance(stored, dict):
        return stored
    if isinstance(stored, list):
        return stored
    if isinstance(stored, str | int | float | bool) or stored is None:
        return stored
    return str(stored)


def _to_item(row: DeviceAttribute) -> DeviceAttributeItem:
    return DeviceAttributeItem(
        key=row.key,
        scope=row.scope,
        value=_attribute_value(row),
        updated_at=row.updated_at,
        updated_by_user_id=row.updated_by_user_id,
        updated_source=row.updated_source,
    )


async def list_device_attributes(
    db: AsyncSession,
    user: CurrentUser,
    device_id: uuid.UUID,
    scope: AttributeScopeParam | None,
) -> DeviceAttributeListResponse:
    await _get_device_for_user(db, device_id, user)
    query = select(DeviceAttribute).where(DeviceAttribute.device_id == device_id)
    if scope is not None:
        query = query.where(DeviceAttribute.scope == _scope_from_param(scope))
    rows = list(await db.scalars(query.order_by(DeviceAttribute.scope, DeviceAttribute.key)))
    return DeviceAttributeListResponse(items=[_to_item(row) for row in rows])


async def get_device_attribute(
    db: AsyncSession,
    user: CurrentUser,
    device_id: uuid.UUID,
    scope: AttributeScopeParam,
    key: str,
) -> DeviceAttributeItem:
    _validate_key_http(key)
    await _get_device_for_user(db, device_id, user)
    row = await db.scalar(
        select(DeviceAttribute).where(
            DeviceAttribute.device_id == device_id,
            DeviceAttribute.scope == _scope_from_param(scope),
            DeviceAttribute.key == key,
        )
    )
    if row is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Attribute not found")
    return _to_item(row)


async def put_device_attribute(
    db: AsyncSession,
    user: CurrentUser,
    device_id: uuid.UUID,
    scope: AttributeScopeParam,
    key: str,
    value: JsonValue,
    publisher: MqttPublisherProtocol,
) -> DeviceAttributePutResponse:
    _validate_key_http(key)
    if scope == AttributeScopeParam.CLIENT:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="client attributes must be set via device publish",
        )

    device = await _get_device_for_user(db, device_id, user)
    scope_enum = _scope_from_param(scope)
    row = await db.scalar(
        select(DeviceAttribute).where(
            DeviceAttribute.device_id == device_id,
            DeviceAttribute.scope == scope_enum,
            DeviceAttribute.key == key,
        )
    )
    old_value: JsonValue = _attribute_value(row) if row is not None else None
    if row is None:
        row = DeviceAttribute(
            device_id=device_id,
            tenant_id=device.tenant_id,
            scope=scope_enum,
            key=key,
            value_json=value,
            updated_by_user_id=user.user_id,
            updated_source="api",
        )
        db.add(row)
    else:
        row.value_json = value
        row.updated_by_user_id = user.user_id
        row.updated_source = "api"
    await db.flush()

    if scope == AttributeScopeParam.SHARED:
        await broadcast_shared_attribute_update(
            publisher,
            tenant_id=device.tenant_id,
            device_id=device_id,
            key=key,
            value=value,
            qos=settings.attribute_shared_broadcast_qos,
        )

    if old_value != value:
        from app.rules.executor import get_rule_executor
        from app.rules.hooks import apply_attribute_change_rules

        executor = get_rule_executor()
        if executor is not None:
            await apply_attribute_change_rules(
                executor,
                db,
                tenant_id=device.tenant_id,
                device_id=device.id,
                scope=scope_enum.value,
                key=key,
                old_value=old_value,
                new_value=value,
            )

    return DeviceAttributePutResponse(
        key=row.key,
        scope=row.scope,
        value=_attribute_value(row),
        updated_at=row.updated_at,
    )


async def delete_device_attribute(
    db: AsyncSession,
    user: CurrentUser,
    device_id: uuid.UUID,
    scope: AttributeScopeParam,
    key: str,
) -> None:
    _validate_key_http(key)
    if scope in {AttributeScopeParam.SERVER, AttributeScopeParam.SHARED}:
        await _get_device_for_user(db, device_id, user)
    else:
        await _get_device_for_user(db, device_id, user)

    scope_enum = _scope_from_param(scope)
    result = await db.execute(
        delete(DeviceAttribute).where(
            DeviceAttribute.device_id == device_id,
            DeviceAttribute.scope == scope_enum,
            DeviceAttribute.key == key,
        )
    )
    if result.rowcount == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Attribute not found")
