import uuid
from datetime import UTC, datetime
from typing import Any

import redis.asyncio as aioredis
from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import CurrentUser
from app.commands.events import publish_device_command
from app.commands.schemas import DeviceCommandRequest, DeviceCommandResponse
from app.models.device import Device
from app.models.device_command import CommandStatus, CommandType, DeviceCommand


def _validate_params(command_type: str, params: dict[str, Any]) -> None:
    if command_type == CommandType.GO_TO_WAYPOINT:
        lat = params.get("lat") if "lat" in params else params.get("latitude")
        lon = params.get("lon") if "lon" in params else params.get("longitude")
        if lat is None or lon is None:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="GO_TO_WAYPOINT requires params.lat and params.lon (or latitude/longitude)",
            )
        return

    if command_type == CommandType.GO_TO_MISSION:
        waypoints = params.get("waypoints")
        if not isinstance(waypoints, list) or len(waypoints) == 0:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="GO_TO_MISSION requires params.waypoints as a non-empty list",
            )
        for index, wp in enumerate(waypoints, start=1):
            if not isinstance(wp, dict):
                raise HTTPException(status_code=422, detail=f"waypoints[{index - 1}] must be an object")
            lat = wp.get("lat") if "lat" in wp else wp.get("latitude")
            lon = wp.get("lon") if "lon" in wp else wp.get("longitude")
            if lat is None or lon is None:
                raise HTTPException(
                    status_code=422,
                    detail=f"waypoints[{index - 1}] requires lat/lon",
                )
        return

    if command_type in {CommandType.RTL, CommandType.TAKEOFF, CommandType.LAND}:
        return

    raise HTTPException(status_code=422, detail=f"Unsupported command_type: {command_type}")


async def _get_device_for_user(
    db: AsyncSession, device_id: uuid.UUID, user: CurrentUser
) -> Device:
    query = select(Device).where(Device.id == device_id)
    if not user.is_super_admin:
        query = query.where(Device.tenant_id == user.tenant_id)
    device = await db.scalar(query)
    if device is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Device not found")
    return device


async def dispatch_device_command(
    db: AsyncSession,
    redis: aioredis.Redis,
    user: CurrentUser,
    device_id: uuid.UUID,
    payload: DeviceCommandRequest,
) -> DeviceCommandResponse:
    device = await _get_device_for_user(db, device_id, user)
    command_type = payload.command_type.value
    _validate_params(command_type, payload.params)

    now = datetime.now(UTC)
    command = DeviceCommand(
        device_id=device.id,
        tenant_id=device.tenant_id,
        issued_by_user_id=user.user_id,
        command_type=command_type,
        params=payload.params,
        status=CommandStatus.DISPATCHED,
        dispatched_at=now,
    )
    db.add(command)
    await db.flush()

    await publish_device_command(
        redis,
        command_id=str(command.id),
        device_id=str(device.id),
        tenant_id=str(device.tenant_id),
        command_type=command_type,
        params=payload.params,
        issued_by_user_id=str(user.user_id),
    )

    await db.commit()
    await db.refresh(command)
    return DeviceCommandResponse.model_validate(command)
