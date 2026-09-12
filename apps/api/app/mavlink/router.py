import base64
import uuid

import redis.asyncio as aioredis
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import RequireAuth, RequireOperator
from app.deps import get_db, get_redis
from app.devices.service import _get_device_for_user
from app.mavlink.bridge_service import MavlinkBridgeService
from app.mavlink.schemas import (
    MavlinkDecodeRequest,
    MavlinkDecodeResponse,
    MavlinkEncodeRequest,
    MavlinkEncodeResponse,
    MavlinkStatusResponse,
    MavlinkTelemetrySnapshot,
)
from app.mavlink.status_store import read_mavlink_status, save_mavlink_status

router = APIRouter(prefix="/api/v1/hardware/mavlink", tags=["hardware-mavlink"])


@router.get("/status", response_model=MavlinkStatusResponse)
async def get_mavlink_status(
    user: RequireAuth,
    redis: aioredis.Redis = Depends(get_redis),
    db: AsyncSession = Depends(get_db),
    device_id: uuid.UUID = Query(...),
):
    await _get_device_for_user(db, device_id, user)
    status_data = await read_mavlink_status(redis, str(device_id))
    return MavlinkStatusResponse(
        device_id=str(device_id),
        connected=bool(status_data.get("connected") or status_data.get("mavlink_connected")),
        protocol_version=status_data.get("protocol_version", "2.0"),
        autopilot=status_data.get("autopilot"),
        last_heartbeat_at=status_data.get("updated_at"),
        metrics=status_data.get("metrics") or {},
    )


@router.post("/decode", response_model=MavlinkDecodeResponse)
async def decode_mavlink_packet(
    payload: MavlinkDecodeRequest,
    user: RequireOperator,
    redis: aioredis.Redis = Depends(get_redis),
    db: AsyncSession = Depends(get_db),
):
    try:
        packet = base64.b64decode(payload.data_b64)
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Invalid base64") from exc

    bridge = MavlinkBridgeService()
    message_types, snapshot = bridge.decode_packet(packet)
    if not message_types:
        raise HTTPException(status_code=422, detail="No supported MAVLink messages found in packet")

    if payload.device_id:
        await _get_device_for_user(db, uuid.UUID(payload.device_id), user)
        await save_mavlink_status(
            redis,
            device_id=payload.device_id,
            snapshot={
                "connected": snapshot.mavlink_connected,
                "protocol_version": snapshot.protocol_version,
                "autopilot": snapshot.autopilot,
                "metrics": bridge.to_internal_metrics(),
            },
        )

    return MavlinkDecodeResponse(messages=message_types, snapshot=snapshot)


@router.post("/encode", response_model=MavlinkEncodeResponse)
async def encode_mavlink_command(
    payload: MavlinkEncodeRequest,
    _: RequireOperator,
):
    bridge = MavlinkBridgeService()
    try:
        packet = bridge.encode_command(
            payload.command.value,
            target_system=payload.target_system,
            target_component=payload.target_component,
            params=payload.params,
        )
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

    return MavlinkEncodeResponse(
        command=payload.command.value,
        data_b64=base64.b64encode(packet).decode("ascii"),
        byte_length=len(packet),
    )
