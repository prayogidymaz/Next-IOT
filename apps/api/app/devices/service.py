import uuid
from datetime import UTC, datetime

import redis.asyncio as aioredis
from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.auth.dependencies import CurrentUser
from app.config import settings
from app.devices.dependencies import CurrentDevice
from app.devices.events import emit_device_event
from app.devices.liveness import clear_liveness, touch_liveness
from app.devices.provisioning import consume_provisioning_token, store_provisioning_token
from app.devices.schemas import (
    DeviceCredentialsResponse,
    DeviceMetadataItem,
    DeviceRegisterRequest,
    DeviceRegisterResponse,
    DeviceResponse,
    DeviceStatusPatchRequest,
    HeartbeatRequest,
    HeartbeatResponse,
)
from app.devices.state_machine import ADMIN_STATUS_TARGETS, can_send_heartbeat, should_emit_online
from app.devices.security import (
    generate_client_id,
    generate_client_secret,
    generate_provisioning_token,
    hash_device_secret,
)
from app.models.device import Device, DeviceStatus
from app.models.device_credential import DeviceCredential
from app.models.device_metadata import DeviceMetadata


def _to_device_response(device: Device) -> DeviceResponse:
    metadata = [
        DeviceMetadataItem(key=entry.key, value=entry.value) for entry in device.metadata_entries
    ]
    return DeviceResponse(
        id=device.id,
        tenant_id=device.tenant_id,
        name=device.name,
        device_type=device.device_type,
        status=device.status,
        last_seen_at=device.last_seen_at,
        metadata=metadata,
        created_at=device.created_at,
    )


async def _get_device_for_user(
    db: AsyncSession, device_id: uuid.UUID, user: CurrentUser
) -> Device:
    query = (
        select(Device)
        .options(selectinload(Device.metadata_entries))
        .where(Device.id == device_id)
    )
    if not user.is_super_admin:
        query = query.where(Device.tenant_id == user.tenant_id)

    device = await db.scalar(query)
    if not device:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Device not found")
    return device


async def register_device(
    db: AsyncSession,
    redis: aioredis.Redis,
    user: CurrentUser,
    payload: DeviceRegisterRequest,
) -> DeviceRegisterResponse:
    device = Device(
        tenant_id=user.tenant_id,
        name=payload.name,
        device_type=payload.device_type,
        status=DeviceStatus.PENDING,
    )
    db.add(device)
    await db.flush()

    for key, value in payload.metadata.items():
        db.add(DeviceMetadata(device_id=device.id, key=key, value=value))

    await db.flush()
    await db.refresh(device, ["metadata_entries"])

    token = generate_provisioning_token()
    await store_provisioning_token(redis, token, str(device.id))

    return DeviceRegisterResponse(
        device=_to_device_response(device),
        provisioning_token=token,
        provisioning_expires_in_hours=settings.device_provisioning_token_expire_hours,
    )


async def list_devices(db: AsyncSession, user: CurrentUser) -> list[DeviceResponse]:
    query = select(Device).options(selectinload(Device.metadata_entries))
    if not user.is_super_admin:
        query = query.where(Device.tenant_id == user.tenant_id)

    result = await db.scalars(query.order_by(Device.created_at.desc()))
    return [_to_device_response(d) for d in result.all()]


async def get_device(db: AsyncSession, user: CurrentUser, device_id: uuid.UUID) -> DeviceResponse:
    device = await _get_device_for_user(db, device_id, user)
    return _to_device_response(device)


async def provision_device(
    db: AsyncSession,
    redis: aioredis.Redis,
    device_id: uuid.UUID,
    provisioning_token: str,
) -> DeviceCredentialsResponse:
    device_id_str = await consume_provisioning_token(redis, provisioning_token)
    if device_id_str is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired provisioning token")

    if str(device_id) != device_id_str:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Provisioning token does not match device")

    device = await db.scalar(
        select(Device)
        .options(selectinload(Device.credentials))
        .where(Device.id == device_id)
    )
    if not device:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Device not found")

    if device.status != DeviceStatus.PENDING:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Device already provisioned")

    if device.credentials:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Device credentials already exist")

    client_id = generate_client_id()
    client_secret = generate_client_secret()

    credential = DeviceCredential(
        device_id=device.id,
        client_id=client_id,
        secret_hash=hash_device_secret(client_secret),
    )
    device.status = DeviceStatus.PROVISIONED
    db.add(credential)

    return DeviceCredentialsResponse(
        client_id=client_id,
        client_secret=client_secret,
        device_id=device.id,
        status=device.status,
    )


async def _upsert_metadata(db: AsyncSession, device: Device, key: str, value: str) -> None:
    existing = next((m for m in device.metadata_entries if m.key == key), None)
    if existing:
        existing.value = value
    else:
        entry = DeviceMetadata(device_id=device.id, key=key, value=value)
        db.add(entry)
        device.metadata_entries.append(entry)


async def process_heartbeat(
    db: AsyncSession,
    redis: aioredis.Redis,
    device_auth: CurrentDevice,
    device_id: uuid.UUID,
    payload: HeartbeatRequest,
) -> HeartbeatResponse:
    if device_auth.device_id != device_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Device ID mismatch")

    device = await db.scalar(
        select(Device)
        .options(selectinload(Device.metadata_entries))
        .where(Device.id == device_id)
    )
    if not device:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Device not found")

    if not can_send_heartbeat(device.status):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Device cannot send heartbeat in status '{device.status}'",
        )

    previous_status = device.status
    now = datetime.now(UTC)
    device.last_seen_at = now
    device.status = DeviceStatus.ONLINE

    if payload.firmware_version:
        await _upsert_metadata(db, device, "firmware_version", payload.firmware_version)
    if payload.ip:
        await _upsert_metadata(db, device, "ip", payload.ip)
    if payload.telemetry:
        for key, value in payload.telemetry.items():
            await _upsert_metadata(db, device, f"telemetry.{key}", str(value))

    await touch_liveness(redis, str(device.id))

    if should_emit_online(previous_status, device.status):
        await emit_device_event(
            redis,
            "device.online",
            device_id=str(device.id),
            tenant_id=str(device.tenant_id),
            extra={"previous_status": previous_status},
        )

    return HeartbeatResponse(device_id=device.id, status=device.status, last_seen_at=now)


async def update_device_status(
    db: AsyncSession,
    redis: aioredis.Redis,
    user: CurrentUser,
    device_id: uuid.UUID,
    payload: DeviceStatusPatchRequest,
) -> DeviceResponse:
    if payload.status not in ADMIN_STATUS_TARGETS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid target status. Allowed: {sorted(ADMIN_STATUS_TARGETS)}",
        )

    device = await _get_device_for_user(db, device_id, user)
    previous = device.status

    if payload.status == DeviceStatus.DEACTIVATED:
        device.status = DeviceStatus.DEACTIVATED
        await clear_liveness(redis, str(device.id))
    elif payload.status == DeviceStatus.PROVISIONED:
        if previous != DeviceStatus.DEACTIVATED:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Only deactivated devices can be reactivated to provisioned",
            )
        device.status = DeviceStatus.PROVISIONED

    return _to_device_response(device)
