import uuid
from datetime import datetime
from typing import Annotated

import redis.asyncio as aioredis
from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import CurrentUser, RequireOperator, RequireTenantAdmin, require_roles
from app.auth.rbac import UserRole
from app.commands import service as command_service
from app.commands.schemas import DeviceCommandRequest, DeviceCommandResponse
from app.deps import get_db, get_redis
from app.devices import service
from app.devices.bulk_import import BulkImportRequest, parse_bulk_import_payload
from app.devices.dependencies import CurrentDevice, get_current_device
from app.devices.schemas import (
    BulkImportResponse,
    DeviceCredentialsResponse,
    DeviceProvisionRequest,
    DeviceRegisterRequest,
    DeviceRegisterResponse,
    DeviceResponse,
    DeviceStatusPatchRequest,
    HeartbeatRequest,
    HeartbeatResponse,
)
from app.rules import service as rules_service
from app.rules.schemas import RuleResponse
from app.telemetry import service as telemetry_service
from app.telemetry.schemas import TelemetryHistoryResponse, TelemetryLatestResponse

router = APIRouter(prefix="/api/v1/devices", tags=["devices"])

RequireDeviceReader = Annotated[
    CurrentUser,
    Depends(require_roles(UserRole.VIEWER, UserRole.OPERATOR, UserRole.TENANT_ADMIN, UserRole.SUPER_ADMIN)),
]


@router.post("", response_model=DeviceRegisterResponse, status_code=201)
async def register_device(
    payload: DeviceRegisterRequest,
    user: RequireTenantAdmin,
    db: AsyncSession = Depends(get_db),
    redis: aioredis.Redis = Depends(get_redis),
):
    return await service.register_device(db, redis, user, payload)


@router.get("", response_model=list[DeviceResponse])
async def list_devices(
    user: RequireDeviceReader,
    db: AsyncSession = Depends(get_db),
):
    return await service.list_devices(db, user)


@router.post("/bulk-import", response_model=BulkImportResponse, status_code=201)
async def bulk_import_devices(
    request: Request,
    user: RequireTenantAdmin,
    db: AsyncSession = Depends(get_db),
    redis: aioredis.Redis = Depends(get_redis),
):
    """Register many devices from JSON body or CSV/JSON file upload (multipart field `file`)."""
    content_type = request.headers.get("content-type", "")
    if "multipart/form-data" in content_type:
        form = await request.form()
        upload = form.get("file")
        if upload is None:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Missing file")
        raw = await upload.read()
        parsed = parse_bulk_import_payload(raw, upload.content_type or "", upload.filename)
    else:
        body = BulkImportRequest.model_validate(await request.json())
        parsed = body
    return await service.bulk_import_devices(db, redis, user, parsed)


@router.get("/{device_id}", response_model=DeviceResponse)
async def get_device(
    device_id: uuid.UUID,
    user: RequireDeviceReader,
    db: AsyncSession = Depends(get_db),
):
    return await service.get_device(db, user, device_id)


@router.post("/{device_id}/provision", response_model=DeviceCredentialsResponse)
async def provision_device(
    device_id: uuid.UUID,
    payload: DeviceProvisionRequest,
    db: AsyncSession = Depends(get_db),
    redis: aioredis.Redis = Depends(get_redis),
):
    """Exchange one-time provisioning token for device credentials (hardware auth)."""
    return await service.provision_device(db, redis, device_id, payload.provisioning_token)


@router.get("/{device_id}/auth-check", response_model=dict)
async def device_auth_check(device: CurrentDevice = Depends(get_current_device)):
    """Verify device credentials — uses HTTP Basic auth (client_id / client_secret)."""
    return {
        "authenticated": True,
        "device_id": str(device.device_id),
        "tenant_id": str(device.tenant_id),
        "status": device.status,
    }


@router.post("/{device_id}/heartbeat", response_model=HeartbeatResponse)
async def device_heartbeat(
    device_id: uuid.UUID,
    payload: HeartbeatRequest,
    device: CurrentDevice = Depends(get_current_device),
    db: AsyncSession = Depends(get_db),
    redis: aioredis.Redis = Depends(get_redis),
):
    return await service.process_heartbeat(db, redis, device, device_id, payload)


@router.get("/{device_id}/rules", response_model=list[RuleResponse])
async def list_device_rules(
    device_id: uuid.UUID,
    user: RequireOperator,
    db: AsyncSession = Depends(get_db),
):
    return await rules_service.list_rules_for_device(db, user, device_id)


@router.get("/{device_id}/telemetry/latest", response_model=TelemetryLatestResponse)
async def get_device_telemetry_latest(
    device_id: uuid.UUID,
    user: RequireDeviceReader,
    db: AsyncSession = Depends(get_db),
    redis: aioredis.Redis = Depends(get_redis),
):
    return await telemetry_service.get_latest_for_device(db, redis, user, device_id)


@router.get("/{device_id}/telemetry/history", response_model=TelemetryHistoryResponse)
async def get_device_telemetry_history(
    device_id: uuid.UUID,
    user: RequireDeviceReader,
    db: AsyncSession = Depends(get_db),
    start_time: datetime | None = Query(default=None),
    end_time: datetime | None = Query(default=None),
    limit: int = Query(default=100, ge=1, le=1000),
):
    return await telemetry_service.get_history_for_device(
        db, user, device_id, start_time=start_time, end_time=end_time, limit=limit
    )


@router.post("/{device_id}/commands", response_model=DeviceCommandResponse, status_code=201)
async def dispatch_device_command(
    device_id: uuid.UUID,
    payload: DeviceCommandRequest,
    user: RequireOperator,
    db: AsyncSession = Depends(get_db),
    redis: aioredis.Redis = Depends(get_redis),
):
    """Dispatch autonomous command to device (operator+). Published via Redis pub/sub."""
    return await command_service.dispatch_device_command(db, redis, user, device_id, payload)


@router.patch("/{device_id}/status", response_model=DeviceResponse)
async def patch_device_status(
    device_id: uuid.UUID,
    payload: DeviceStatusPatchRequest,
    user: RequireTenantAdmin,
    db: AsyncSession = Depends(get_db),
    redis: aioredis.Redis = Depends(get_redis),
):
    return await service.update_device_status(db, redis, user, device_id, payload)
