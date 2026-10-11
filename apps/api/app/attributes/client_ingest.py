"""Persist client-scope attributes from MQTT (flat JSON object)."""

from __future__ import annotations

import uuid

from pydantic import JsonValue
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.attributes.schemas import validate_attribute_key
from app.models.device import Device
from app.models.device_attribute import DeviceAttribute, DeviceAttributeScope
from app.rules.attribute_event import AttributeChangeEvent


async def persist_client_attributes_from_mqtt(
    db: AsyncSession,
    *,
    tenant_id: uuid.UUID,
    device_id: uuid.UUID,
    payload: dict[str, JsonValue],
) -> tuple[int, list[AttributeChangeEvent]]:
    device = await db.scalar(
        select(Device).where(Device.id == device_id, Device.tenant_id == tenant_id)
    )
    if device is None:
        return 0, []

    upserted = 0
    changes: list[AttributeChangeEvent] = []
    for raw_key, value in payload.items():
        if not isinstance(raw_key, str):
            continue
        try:
            key = validate_attribute_key(raw_key)
        except ValueError:
            continue
        existing = await db.scalar(
            select(DeviceAttribute).where(
                DeviceAttribute.device_id == device_id,
                DeviceAttribute.scope == DeviceAttributeScope.CLIENT,
                DeviceAttribute.key == key,
            )
        )
        old_value: JsonValue = existing.value_json if existing is not None else None
        if existing is None:
            db.add(
                DeviceAttribute(
                    device_id=device_id,
                    tenant_id=tenant_id,
                    scope=DeviceAttributeScope.CLIENT,
                    key=key,
                    value_json=value,
                    updated_by_user_id=None,
                    updated_source="mqtt_client_push",
                )
            )
        else:
            existing.value_json = value
            existing.updated_source = "mqtt_client_push"
        if old_value != value:
            changes.append(
                AttributeChangeEvent(
                    scope=DeviceAttributeScope.CLIENT.value,
                    key=key,
                    old_value=old_value,
                    new_value=value,
                )
            )
        upserted += 1
    if upserted:
        await db.flush()
    return upserted, changes
