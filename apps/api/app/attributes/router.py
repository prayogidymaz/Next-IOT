"""Device attributes HTTP routes."""

from __future__ import annotations

import uuid
from typing import Annotated

from fastapi import APIRouter, Query, Request, Response, status

from app.attributes import service
from app.attributes.schemas import (
    AttributeScopeParam,
    AttributeValueBody,
    DeviceAttributeItem,
    DeviceAttributeListResponse,
    DeviceAttributePutResponse,
)
from app.auth.dependencies import RequireOperator
from app.deps import DbSession
from app.devices.rbac import RequireDeviceReader
from app.mqtt_publisher.deps import get_mqtt_publisher

router = APIRouter()

ScopeQuery = Annotated[AttributeScopeParam | None, Query(alias="scope")]


@router.get("", response_model=DeviceAttributeListResponse)
async def list_attributes(
    device_id: uuid.UUID,
    user: RequireDeviceReader,
    db: DbSession,
    scope: ScopeQuery = None,
) -> DeviceAttributeListResponse:
    return await service.list_device_attributes(db, user, device_id, scope)


@router.get("/{scope}/{key}", response_model=DeviceAttributeItem)
async def get_attribute(
    device_id: uuid.UUID,
    scope: AttributeScopeParam,
    key: str,
    user: RequireDeviceReader,
    db: DbSession,
) -> DeviceAttributeItem:
    return await service.get_device_attribute(db, user, device_id, scope, key)


@router.put("/{scope}/{key}", response_model=DeviceAttributePutResponse)
async def put_attribute(
    device_id: uuid.UUID,
    scope: AttributeScopeParam,
    key: str,
    body: AttributeValueBody,
    user: RequireOperator,
    db: DbSession,
    request: Request,
) -> DeviceAttributePutResponse:
    publisher = get_mqtt_publisher(request)
    return await service.put_device_attribute(
        db, user, device_id, scope, key, body.value, publisher
    )


@router.delete("/{scope}/{key}", status_code=status.HTTP_204_NO_CONTENT, response_class=Response)
async def delete_attribute(
    device_id: uuid.UUID,
    scope: AttributeScopeParam,
    key: str,
    user: RequireOperator,
    db: DbSession,
) -> Response:
    await service.delete_device_attribute(db, user, device_id, scope, key)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
