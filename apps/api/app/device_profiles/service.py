from __future__ import annotations

import uuid

from fastapi import HTTPException, Request, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.audit.actions import AuditAction
from app.audit.service import client_ip, record_audit_event
from app.auth.dependencies import CurrentUser
from app.device_profiles.schemas import (
    DeviceProfileCreateRequest,
    DeviceProfileResponse,
    DeviceProfileUpdateRequest,
)
from app.device_profiles.spec import parse_thing_model_spec, spec_to_storage
from app.models.device import Device, DeviceStatus
from app.models.device_profile import DeviceProfile, ProfileDomain, ProfileStatus


def _to_response(profile: DeviceProfile) -> DeviceProfileResponse:
    spec = parse_thing_model_spec(profile.spec)
    return DeviceProfileResponse(
        id=profile.id,
        tenant_id=profile.tenant_id,
        key=profile.key,
        name=profile.name,
        description=profile.description,
        domain=ProfileDomain(profile.domain),
        version=profile.version,
        status=ProfileStatus(profile.status),
        spec=spec,
        created_at=profile.created_at,
        updated_at=profile.updated_at,
    )


async def _get_profile_for_user(
    db: AsyncSession,
    profile_id: uuid.UUID,
    user: CurrentUser,
) -> DeviceProfile:
    query = select(DeviceProfile).where(DeviceProfile.id == profile_id)
    if not user.is_super_admin:
        query = query.where(DeviceProfile.tenant_id == user.tenant_id)
    profile = await db.scalar(query)
    if profile is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Device profile not found")
    return profile


def _ensure_draft(profile: DeviceProfile) -> None:
    if profile.status != ProfileStatus.DRAFT:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Only draft profiles can be modified",
        )


async def list_device_profiles(
    db: AsyncSession,
    user: CurrentUser,
    *,
    domain: ProfileDomain | None = None,
    profile_status: ProfileStatus | None = None,
) -> list[DeviceProfileResponse]:
    query = select(DeviceProfile)
    if not user.is_super_admin:
        query = query.where(DeviceProfile.tenant_id == user.tenant_id)
    if domain is not None:
        query = query.where(DeviceProfile.domain == domain.value)
    if profile_status is not None:
        query = query.where(DeviceProfile.status == profile_status.value)
    query = query.order_by(DeviceProfile.key, DeviceProfile.version.desc())
    rows = await db.scalars(query)
    return [_to_response(row) for row in rows.all()]


async def get_device_profile(
    db: AsyncSession,
    user: CurrentUser,
    profile_id: uuid.UUID,
) -> DeviceProfileResponse:
    profile = await _get_profile_for_user(db, profile_id, user)
    return _to_response(profile)


async def create_device_profile(
    db: AsyncSession,
    user: CurrentUser,
    payload: DeviceProfileCreateRequest,
    request: Request | None = None,
) -> DeviceProfileResponse:
    existing = await db.scalar(
        select(DeviceProfile.id).where(
            DeviceProfile.tenant_id == user.tenant_id,
            DeviceProfile.key == payload.key,
            DeviceProfile.version == 1,
        )
    )
    if existing is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Profile key '{payload.key}' version 1 already exists",
        )

    profile = DeviceProfile(
        tenant_id=user.tenant_id,
        key=payload.key,
        name=payload.name,
        description=payload.description,
        domain=payload.domain.value,
        version=1,
        status=ProfileStatus.DRAFT,
        spec=spec_to_storage(payload.spec),
    )
    db.add(profile)
    await db.flush()
    await db.refresh(profile)
    response = _to_response(profile)
    await record_audit_event(
        db,
        action=AuditAction.DEVICE_PROFILE_CREATE,
        actor_email=user.email,
        actor_id=user.user_id,
        tenant_id=user.tenant_id,
        resource_target=f"device_profile:{profile.id}",
        ip_address=client_ip(request),
    )
    return response


async def update_device_profile(
    db: AsyncSession,
    user: CurrentUser,
    profile_id: uuid.UUID,
    payload: DeviceProfileUpdateRequest,
) -> DeviceProfileResponse:
    profile = await _get_profile_for_user(db, profile_id, user)
    _ensure_draft(profile)

    if payload.name is not None:
        profile.name = payload.name
    if payload.description is not None:
        profile.description = payload.description
    if payload.domain is not None:
        profile.domain = payload.domain.value
    if payload.spec is not None:
        profile.spec = spec_to_storage(payload.spec)

    await db.flush()
    await db.refresh(profile)
    return _to_response(profile)


async def publish_device_profile(
    db: AsyncSession,
    user: CurrentUser,
    profile_id: uuid.UUID,
    request: Request | None = None,
) -> DeviceProfileResponse:
    profile = await _get_profile_for_user(db, profile_id, user)
    if profile.status != ProfileStatus.DRAFT:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Only draft profiles can be published",
        )
    profile.status = ProfileStatus.PUBLISHED
    await db.flush()
    await db.refresh(profile)
    response = _to_response(profile)
    await record_audit_event(
        db,
        action=AuditAction.DEVICE_PROFILE_PUBLISH,
        actor_email=user.email,
        actor_id=user.user_id,
        tenant_id=user.tenant_id,
        resource_target=f"device_profile:{profile.id}",
        ip_address=client_ip(request),
    )
    return response


async def new_version_device_profile(
    db: AsyncSession,
    user: CurrentUser,
    profile_id: uuid.UUID,
) -> DeviceProfileResponse:
    source = await _get_profile_for_user(db, profile_id, user)
    if source.status != ProfileStatus.PUBLISHED:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="New version can only be created from a published profile",
        )

    next_version = source.version + 1
    existing_draft = await db.scalar(
        select(DeviceProfile.id).where(
            DeviceProfile.tenant_id == source.tenant_id,
            DeviceProfile.key == source.key,
            DeviceProfile.version == next_version,
        )
    )
    if existing_draft is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Profile version {next_version} already exists",
        )

    clone = DeviceProfile(
        tenant_id=source.tenant_id,
        key=source.key,
        name=source.name,
        description=source.description,
        domain=source.domain,
        version=next_version,
        status=ProfileStatus.DRAFT,
        spec=dict(source.spec),
    )
    db.add(clone)
    await db.flush()
    await db.refresh(clone)
    return _to_response(clone)


async def _count_active_devices_on_profile(db: AsyncSession, profile_id: uuid.UUID) -> int:
    count = await db.scalar(
        select(func.count())
        .select_from(Device)
        .where(
            Device.profile_id == profile_id,
            Device.status != DeviceStatus.DEACTIVATED,
        )
    )
    return int(count or 0)


async def archive_device_profile(
    db: AsyncSession,
    user: CurrentUser,
    profile_id: uuid.UUID,
    request: Request | None = None,
) -> DeviceProfileResponse:
    profile = await _get_profile_for_user(db, profile_id, user)
    if profile.status == ProfileStatus.ARCHIVED:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Profile is already archived")

    active = await _count_active_devices_on_profile(db, profile.id)
    if active > 0:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Cannot archive: {active} active device(s) still use this profile version",
        )

    profile.status = ProfileStatus.ARCHIVED
    await db.flush()
    await db.refresh(profile)
    response = _to_response(profile)
    await record_audit_event(
        db,
        action=AuditAction.DEVICE_PROFILE_ARCHIVE,
        actor_email=user.email,
        actor_id=user.user_id,
        tenant_id=user.tenant_id,
        resource_target=f"device_profile:{profile.id}",
        ip_address=client_ip(request),
    )
    return response


async def assign_device_profile(
    db: AsyncSession,
    user: CurrentUser,
    device_id: uuid.UUID,
    profile_id: uuid.UUID | None,
) -> None:
    from app.devices.service import _get_device_for_user

    device = await _get_device_for_user(db, device_id, user)
    if profile_id is None:
        device.profile_id = None
        await db.flush()
        return

    profile = await _get_profile_for_user(db, profile_id, user)
    if profile.tenant_id != device.tenant_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Profile tenant mismatch")
    if profile.status != ProfileStatus.PUBLISHED:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Only published profiles can be assigned to devices",
        )
    device.profile_id = profile.id
    await db.flush()
