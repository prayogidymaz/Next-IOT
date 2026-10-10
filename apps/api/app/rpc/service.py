"""Device RPC command dispatch and history."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime

from fastapi import HTTPException, status
from pydantic import JsonValue
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.context import CurrentUser
from app.config import settings
from app.devices.service import _get_device_for_user
from app.models.device import DeviceStatus
from app.models.device_rpc_request import DeviceRpcRequest, DeviceRpcStatus
from app.mqtt_publisher.protocol import MqttPublisherProtocol
from app.rpc.event_registry import rpc_event_registry
from app.rpc.mqtt_topics import rpc_request_topic
from app.rpc.rate_limit import enforce_rpc_rate_limit
from app.rpc.schemas import (
    DeviceRpcCreateRequest,
    DeviceRpcCreateResponse,
    DeviceRpcItem,
    DeviceRpcListResponse,
)
from app.types.json_types import JsonObject
from app.types.redis_client import RedisClient


def _clamp_timeout(seconds: int) -> int:
    return min(max(seconds, 1), settings.rpc_max_timeout_seconds)


def _json_value_from_object(value: object) -> JsonValue | None:
    if isinstance(value, dict | list | str | int | float | bool) or value is None:
        return value
    return None


def _json_object_from_mapping(raw: dict[str, object]) -> JsonObject:
    out: JsonObject = {}
    for key, value in raw.items():
        if not isinstance(key, str):
            continue
        parsed = _json_value_from_object(value)
        if parsed is not None or value is None:
            out[key] = parsed
    return out


def _to_item(row: DeviceRpcRequest) -> DeviceRpcItem:
    params = _json_object_from_mapping(row.params)
    response: JsonValue | None = None
    if isinstance(row.response_json, dict):
        response = _json_object_from_mapping(row.response_json)
    return DeviceRpcItem(
        id=row.id,
        method=row.method,
        params=params,
        status=row.status,
        response_json=response,
        error_message=row.error_message,
        timeout_seconds=row.timeout_seconds,
        requested_at=row.requested_at,
        delivered_at=row.delivered_at,
        completed_at=row.completed_at,
    )


async def create_device_rpc(
    db: AsyncSession,
    redis: RedisClient,
    user: CurrentUser,
    device_id: uuid.UUID,
    body: DeviceRpcCreateRequest,
    publisher: MqttPublisherProtocol,
) -> tuple[DeviceRpcCreateResponse, int]:
    device = await _get_device_for_user(db, device_id, user)
    if device.status != DeviceStatus.ONLINE:
        return (
            DeviceRpcCreateResponse(status="failed", reason="device_offline"),
            status.HTTP_503_SERVICE_UNAVAILABLE,
        )

    await enforce_rpc_rate_limit(redis, device_id)

    timeout_seconds = _clamp_timeout(body.timeout_seconds)
    row = DeviceRpcRequest(
        device_id=device.id,
        tenant_id=device.tenant_id,
        method=body.method,
        params=body.params,
        status=DeviceRpcStatus.PENDING,
        timeout_seconds=timeout_seconds,
        requested_by_user_id=user.user_id,
    )
    db.add(row)
    await db.flush()

    topic = rpc_request_topic(device.tenant_id, device.id, row.id)
    await publisher.publish_json(
        topic,
        {"method": body.method, "params": body.params, "request_id": str(row.id)},
        qos=1,
    )
    row.status = DeviceRpcStatus.DELIVERED
    row.delivered_at = datetime.now(UTC)
    await db.flush()
    await db.commit()

    wait_result = await rpc_event_registry.register_wait(row.id, float(timeout_seconds))
    if wait_result is None:
        refreshed = await db.scalar(select(DeviceRpcRequest).where(DeviceRpcRequest.id == row.id))
        if refreshed is not None and refreshed.status == DeviceRpcStatus.DELIVERED:
            refreshed.status = DeviceRpcStatus.TIMEOUT
            refreshed.completed_at = datetime.now(UTC)
            await db.commit()
        return (
            DeviceRpcCreateResponse(status="timeout", request_id=row.id),
            status.HTTP_408_REQUEST_TIMEOUT,
        )

    refreshed = await db.scalar(select(DeviceRpcRequest).where(DeviceRpcRequest.id == row.id))
    if refreshed is None:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="RPC row missing")

    if refreshed.status == DeviceRpcStatus.FAILED:
        return (
            DeviceRpcCreateResponse(
                status="failed",
                reason=refreshed.error_message,
                request_id=row.id,
            ),
            status.HTTP_200_OK,
        )

    return (
        DeviceRpcCreateResponse(
            status="completed",
            response=wait_result.response,
            request_id=row.id,
        ),
        status.HTTP_200_OK,
    )


async def list_device_rpc(
    db: AsyncSession,
    user: CurrentUser,
    device_id: uuid.UUID,
    status_filter: str | None,
) -> DeviceRpcListResponse:
    await _get_device_for_user(db, device_id, user)
    query = select(DeviceRpcRequest).where(DeviceRpcRequest.device_id == device_id)
    if status_filter:
        query = query.where(DeviceRpcRequest.status == status_filter)
    rows = list(
        await db.scalars(query.order_by(DeviceRpcRequest.requested_at.desc()).limit(50))
    )
    return DeviceRpcListResponse(items=[_to_item(row) for row in rows])


async def get_device_rpc(
    db: AsyncSession,
    user: CurrentUser,
    device_id: uuid.UUID,
    request_id: uuid.UUID,
) -> DeviceRpcItem:
    await _get_device_for_user(db, device_id, user)
    row = await db.scalar(
        select(DeviceRpcRequest).where(
            DeviceRpcRequest.id == request_id,
            DeviceRpcRequest.device_id == device_id,
        )
    )
    if row is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="RPC request not found")
    return _to_item(row)
