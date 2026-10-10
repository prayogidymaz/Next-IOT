"""Device RPC HTTP routes."""

from __future__ import annotations

import uuid
from typing import Annotated

from fastapi import APIRouter, Query, Request
from fastapi.responses import JSONResponse

from app.auth.dependencies import RequireOperator
from app.deps import DbSession, RedisDep
from app.devices.rbac import RequireDeviceReader
from app.mqtt_publisher.deps import get_mqtt_publisher
from app.rpc import service
from app.rpc.schemas import DeviceRpcCreateRequest, DeviceRpcCreateResponse, DeviceRpcItem, DeviceRpcListResponse

router = APIRouter()

StatusFilter = Annotated[str | None, Query(alias="status")]


@router.post("", response_model=DeviceRpcCreateResponse)
async def create_rpc(
    device_id: uuid.UUID,
    body: DeviceRpcCreateRequest,
    user: RequireOperator,
    db: DbSession,
    redis: RedisDep,
    request: Request,
) -> DeviceRpcCreateResponse | JSONResponse:
    publisher = get_mqtt_publisher(request)
    result, status_code = await service.create_device_rpc(
        db, redis, user, device_id, body, publisher
    )
    if status_code != 200:
        return JSONResponse(status_code=status_code, content=result.model_dump(mode="json"))
    return result


@router.get("", response_model=DeviceRpcListResponse)
async def list_rpc(
    device_id: uuid.UUID,
    user: RequireDeviceReader,
    db: DbSession,
    status: StatusFilter = None,
) -> DeviceRpcListResponse:
    return await service.list_device_rpc(db, user, device_id, status)


@router.get("/{request_id}", response_model=DeviceRpcItem)
async def get_rpc(
    device_id: uuid.UUID,
    request_id: uuid.UUID,
    user: RequireDeviceReader,
    db: DbSession,
) -> DeviceRpcItem:
    return await service.get_device_rpc(db, user, device_id, request_id)
