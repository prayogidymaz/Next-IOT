import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, File, Form, Query, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import CurrentUser, RequireTenantAdmin, require_roles
from app.auth.rbac import UserRole
from app.deps import get_db
from app.devices.dependencies import CurrentDevice, get_current_device
from app.ota import service as ota_service
from app.ota.schemas import (
    FirmwareReleaseResponse,
    OtaPublishResponse,
    OtaRolloutResponse,
    OtaRolloutStatusPatch,
    OtaUpdateCheckResponse,
)

router = APIRouter(prefix="/api/v1/ota", tags=["ota"])

RequireOtaReader = Annotated[
    CurrentUser,
    Depends(require_roles(UserRole.VIEWER, UserRole.OPERATOR, UserRole.TENANT_ADMIN, UserRole.SUPER_ADMIN)),
]


@router.get("/releases", response_model=list[FirmwareReleaseResponse])
async def list_firmware_releases(user: RequireOtaReader, db: AsyncSession = Depends(get_db)):
    return await ota_service.list_releases(db, user)


@router.post("/releases", response_model=FirmwareReleaseResponse, status_code=201)
async def upload_firmware_release(
    user: RequireTenantAdmin,
    db: AsyncSession = Depends(get_db),
    file: UploadFile = File(...),
    version: str = Form(...),
    target_device_category: str = Form(...),
):
    data = await file.read()
    return await ota_service.create_release(
        db,
        user,
        version=version,
        target_device_category=target_device_category,
        filename=file.filename or "firmware.bin",
        file_bytes=data,
    )


@router.post("/releases/{release_id}/publish", response_model=OtaPublishResponse)
async def publish_firmware_release(
    release_id: uuid.UUID,
    user: RequireTenantAdmin,
    db: AsyncSession = Depends(get_db),
):
    return await ota_service.publish_release(db, user, release_id)


@router.get("/releases/{release_id}/rollouts", response_model=list[OtaRolloutResponse])
async def list_release_rollouts(
    release_id: uuid.UUID,
    user: RequireOtaReader,
    db: AsyncSession = Depends(get_db),
):
    return await ota_service.list_rollouts(db, user, release_id)


@router.get("/releases/{release_id}/download")
async def download_release_firmware_user(
    release_id: uuid.UUID,
    user: RequireOtaReader,
    db: AsyncSession = Depends(get_db),
):
    return await ota_service.download_firmware(db, user, None, release_id)


@router.get("/device/releases/{release_id}/download")
async def download_release_firmware_device(
    release_id: uuid.UUID,
    device: CurrentDevice = Depends(get_current_device),
    db: AsyncSession = Depends(get_db),
):
    return await ota_service.download_firmware(db, None, device, release_id)


@router.get("/check", response_model=OtaUpdateCheckResponse)
async def check_ota_update(
    device: CurrentDevice = Depends(get_current_device),
    db: AsyncSession = Depends(get_db),
    current_version: str | None = Query(default=None),
):
    """Device-facing OTA check (HTTP Basic device credentials)."""
    return await ota_service.check_ota_update(db, device, current_version)


@router.post("/releases/{release_id}/rollouts/status", status_code=204)
async def report_device_rollout_status(
    release_id: uuid.UUID,
    payload: OtaRolloutStatusPatch,
    device: CurrentDevice = Depends(get_current_device),
    db: AsyncSession = Depends(get_db),
):
    await ota_service.report_rollout_status(db, device, release_id, payload.status)
