"""Edge agent device registration and firmware routes."""

from __future__ import annotations

import uuid
from typing import Annotated

from fastapi import APIRouter, File, Form, Query, UploadFile

from app.auth.dependencies import RequireTenantAdmin
from app.deps import DbSession, RedisDep
from app.devices.edge_agent.ota_service import OTAService
from app.devices.edge_agent.registration import EdgeAgentRegistration
from app.devices.edge_agent.schemas import EdgeRegisterRequest, EdgeRegisterResponse, FirmwareVersionView

devices_router = APIRouter(prefix="/api/v1/devices", tags=["edge-agent"])
firmware_router = APIRouter(prefix="/api/v1/firmware", tags=["edge-firmware"])


@devices_router.post("/register", response_model=EdgeRegisterResponse)
async def post_edge_register(
    db: DbSession,
    redis: RedisDep,
    payload: EdgeRegisterRequest,
) -> EdgeRegisterResponse:
    device = await EdgeAgentRegistration().auto_register(
        db,
        redis,
        payload.device_token,
        payload.device_type,
        payload.capabilities,
    )
    await db.commit()
    return EdgeRegisterResponse(
        device_id=device.id,
        tenant_id=device.tenant_id,
        mqtt_topic_prefix=f"next-iot/sensor/{device.id}",
    )


@firmware_router.get("/latest", response_model=FirmwareVersionView | None)
async def get_firmware_latest(
    db: DbSession,
    device_type: Annotated[str, Query(min_length=1)],
) -> FirmwareVersionView | None:
    return await OTAService().get_latest_firmware(db, device_type)


@firmware_router.get("/versions", response_model=list[FirmwareVersionView])
async def get_firmware_versions(
    db: DbSession,
    device_type: Annotated[str, Query(min_length=1)],
) -> list[FirmwareVersionView]:
    return await OTAService().list_versions(db, device_type)


@firmware_router.post("/upload", response_model=FirmwareVersionView, status_code=201)
async def post_firmware_upload(
    user: RequireTenantAdmin,
    db: DbSession,
    file: UploadFile = File(...),
    device_type: str = Form(...),
    version: str = Form(...),
) -> FirmwareVersionView:
    data = await file.read()
    view = await OTAService().upload_firmware(db, device_type, version, data)
    await db.commit()
    return view
