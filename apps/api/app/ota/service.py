import uuid
from datetime import UTC, datetime

from fastapi import HTTPException, status
from fastapi.responses import FileResponse
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.auth.dependencies import CurrentUser
from app.devices.dependencies import CurrentDevice
from app.models.device import Device
from app.models.device_category import DeviceCategory
from app.models.firmware_release import (
    FirmwareRelease,
    FirmwareReleaseStatus,
    OtaDeviceRollout,
    OtaRolloutStatus,
)
from app.ota.schemas import (
    FirmwareReleaseResponse,
    OtaPublishResponse,
    OtaRolloutResponse,
    OtaUpdateCheckResponse,
)
from app.ota.storage import resolve_firmware_path, save_firmware_blob, sha256_hex


def _release_response(release: FirmwareRelease) -> FirmwareReleaseResponse:
    return FirmwareReleaseResponse.model_validate(release)


async def list_releases(db: AsyncSession, user: CurrentUser) -> list[FirmwareReleaseResponse]:
    query = select(FirmwareRelease).order_by(FirmwareRelease.created_at.desc())
    if not user.is_super_admin:
        query = query.where(FirmwareRelease.tenant_id == user.tenant_id)
    result = await db.scalars(query)
    return [_release_response(r) for r in result.all()]


async def create_release(
    db: AsyncSession,
    user: CurrentUser,
    *,
    version: str,
    target_device_category: str,
    filename: str,
    file_bytes: bytes,
) -> FirmwareReleaseResponse:
    try:
        DeviceCategory(target_device_category.upper())
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Invalid target_device_category '{target_device_category}'",
        ) from exc

    release = FirmwareRelease(
        tenant_id=user.tenant_id,
        version=version.strip(),
        target_device_category=target_device_category.upper(),
        checksum_sha256=sha256_hex(file_bytes),
        file_url="",
        status=FirmwareReleaseStatus.DRAFT,
    )
    db.add(release)
    await db.flush()

    release.file_url = save_firmware_blob(user.tenant_id, release.id, filename, file_bytes)
    await db.commit()
    await db.refresh(release)
    return _release_response(release)


async def publish_release(
    db: AsyncSession,
    user: CurrentUser,
    release_id: uuid.UUID,
) -> OtaPublishResponse:
    release = await _get_release_for_user(db, user, release_id)

    await db.execute(
        update(FirmwareRelease)
        .where(
            FirmwareRelease.tenant_id == release.tenant_id,
            FirmwareRelease.target_device_category == release.target_device_category,
            FirmwareRelease.status == FirmwareReleaseStatus.ACTIVE,
            FirmwareRelease.id != release.id,
        )
        .values(status=FirmwareReleaseStatus.ARCHIVED)
    )

    release.status = FirmwareReleaseStatus.ACTIVE

    devices = await db.scalars(
        select(Device).where(
            Device.tenant_id == release.tenant_id,
            Device.device_category == release.target_device_category,
        )
    )
    device_list = devices.all()
    created = 0
    for device in device_list:
        existing = await db.scalar(
            select(OtaDeviceRollout).where(
                OtaDeviceRollout.release_id == release.id,
                OtaDeviceRollout.device_id == device.id,
            )
        )
        if existing:
            existing.status = OtaRolloutStatus.PENDING
            existing.reported_at = None
        else:
            db.add(
                OtaDeviceRollout(
                    tenant_id=release.tenant_id,
                    release_id=release.id,
                    device_id=device.id,
                    status=OtaRolloutStatus.PENDING,
                )
            )
            created += 1

    await db.commit()
    await db.refresh(release)
    return OtaPublishResponse(
        release=_release_response(release),
        targeted_devices=len(device_list),
        rollouts_created=created,
    )


async def list_rollouts(
    db: AsyncSession,
    user: CurrentUser,
    release_id: uuid.UUID,
) -> list[OtaRolloutResponse]:
    await _get_release_for_user(db, user, release_id)
    rows = await db.scalars(
        select(OtaDeviceRollout)
        .where(OtaDeviceRollout.release_id == release_id)
        .options(selectinload(OtaDeviceRollout.release))
    )
    rollouts = rows.all()
    if not rollouts:
        return []

    device_ids = [r.device_id for r in rollouts]
    devices = await db.scalars(select(Device).where(Device.id.in_(device_ids)))
    name_by_id = {d.id: d.name for d in devices.all()}

    return [
        OtaRolloutResponse(
            id=r.id,
            device_id=r.device_id,
            device_name=name_by_id.get(r.device_id, str(r.device_id)),
            status=r.status,
            reported_at=r.reported_at,
            created_at=r.created_at,
        )
        for r in rollouts
    ]


async def check_ota_update(
    db: AsyncSession,
    device_auth: CurrentDevice,
    current_version: str | None,
) -> OtaUpdateCheckResponse:
    device = await db.scalar(select(Device).where(Device.id == device_auth.device_id))
    if not device:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Device not found")

    release = await db.scalar(
        select(FirmwareRelease)
        .where(
            FirmwareRelease.tenant_id == device.tenant_id,
            FirmwareRelease.target_device_category == device.device_category,
            FirmwareRelease.status == FirmwareReleaseStatus.ACTIVE,
        )
        .order_by(FirmwareRelease.created_at.desc())
    )
    if not release:
        return OtaUpdateCheckResponse(update_available=False)

    if current_version and current_version.strip() == release.version:
        return OtaUpdateCheckResponse(update_available=False, version=release.version)

    return OtaUpdateCheckResponse(
        update_available=True,
        version=release.version,
        file_url=release.file_url,
        checksum_sha256=release.checksum_sha256,
        release_id=release.id,
    )


async def report_rollout_status(
    db: AsyncSession,
    device_auth: CurrentDevice,
    release_id: uuid.UUID,
    rollout_status: str,
) -> None:
    if rollout_status not in {s.value for s in OtaRolloutStatus}:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Invalid rollout status")

    rollout = await db.scalar(
        select(OtaDeviceRollout).where(
            OtaDeviceRollout.release_id == release_id,
            OtaDeviceRollout.device_id == device_auth.device_id,
        )
    )
    if not rollout:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Rollout not assigned to device")

    rollout.status = rollout_status
    rollout.reported_at = datetime.now(UTC)
    await db.commit()


async def download_firmware(
    db: AsyncSession,
    user: CurrentUser | None,
    device_auth: CurrentDevice | None,
    release_id: uuid.UUID,
) -> FileResponse:
    release = await db.scalar(select(FirmwareRelease).where(FirmwareRelease.id == release_id))
    if not release:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Release not found")

    if user is not None:
        if not user.is_super_admin and release.tenant_id != user.tenant_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
    elif device_auth is not None:
        if device_auth.tenant_id != release.tenant_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
    else:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication required")

    path = resolve_firmware_path(release.tenant_id, release.id)
    if not path:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Firmware binary not found")

    return FileResponse(path, filename=path.name, media_type="application/octet-stream")


async def _get_release_for_user(
    db: AsyncSession, user: CurrentUser, release_id: uuid.UUID
) -> FirmwareRelease:
    query = select(FirmwareRelease).where(FirmwareRelease.id == release_id)
    if not user.is_super_admin:
        query = query.where(FirmwareRelease.tenant_id == user.tenant_id)
    release = await db.scalar(query)
    if not release:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Firmware release not found")
    return release
