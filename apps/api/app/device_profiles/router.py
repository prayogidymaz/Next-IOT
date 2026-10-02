import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, Query, Request, status

from app.auth.context import CurrentUser
from app.auth.dependencies import RequireTenantAdmin, require_roles
from app.auth.rbac import UserRole
from app.deps import DbSession
from app.device_profiles import service
from app.device_profiles.schemas import (
    DeviceProfileCreateRequest,
    DeviceProfileResponse,
    DeviceProfileUpdateRequest,
)
from app.models.device_profile import ProfileDomain, ProfileStatus

router = APIRouter(prefix="/api/v1/device-profiles", tags=["device-profiles"])

RequireProfileReader = Annotated[
    CurrentUser,
    Depends(require_roles(UserRole.VIEWER, UserRole.OPERATOR, UserRole.TENANT_ADMIN, UserRole.SUPER_ADMIN)),
]

OptionalProfileDomain = Annotated[ProfileDomain | None, Query()]
OptionalProfileStatus = Annotated[ProfileStatus | None, Query(alias="status")]


@router.get("", response_model=list[DeviceProfileResponse])
async def list_device_profiles(
    user: RequireProfileReader,
    db: DbSession,
    domain: OptionalProfileDomain = None,
    profile_status: OptionalProfileStatus = None,
) -> list[DeviceProfileResponse]:
    return await service.list_device_profiles(db, user, domain=domain, profile_status=profile_status)


@router.get("/{profile_id}", response_model=DeviceProfileResponse)
async def get_device_profile(
    profile_id: uuid.UUID,
    user: RequireProfileReader,
    db: DbSession,
) -> DeviceProfileResponse:
    return await service.get_device_profile(db, user, profile_id)


@router.post("", response_model=DeviceProfileResponse, status_code=status.HTTP_201_CREATED)
async def create_device_profile(
    payload: DeviceProfileCreateRequest,
    user: RequireTenantAdmin,
    db: DbSession,
    request: Request,
) -> DeviceProfileResponse:
    return await service.create_device_profile(db, user, payload, request)


@router.patch("/{profile_id}", response_model=DeviceProfileResponse)
async def update_device_profile(
    profile_id: uuid.UUID,
    payload: DeviceProfileUpdateRequest,
    user: RequireTenantAdmin,
    db: DbSession,
) -> DeviceProfileResponse:
    return await service.update_device_profile(db, user, profile_id, payload)


@router.post("/{profile_id}/publish", response_model=DeviceProfileResponse)
async def publish_device_profile(
    profile_id: uuid.UUID,
    user: RequireTenantAdmin,
    db: DbSession,
    request: Request,
) -> DeviceProfileResponse:
    return await service.publish_device_profile(db, user, profile_id, request)


@router.post("/{profile_id}/new-version", response_model=DeviceProfileResponse, status_code=status.HTTP_201_CREATED)
async def new_version_device_profile(
    profile_id: uuid.UUID,
    user: RequireTenantAdmin,
    db: DbSession,
) -> DeviceProfileResponse:
    return await service.new_version_device_profile(db, user, profile_id)


@router.post("/{profile_id}/archive", response_model=DeviceProfileResponse)
async def archive_device_profile(
    profile_id: uuid.UUID,
    user: RequireTenantAdmin,
    db: DbSession,
    request: Request,
) -> DeviceProfileResponse:
    return await service.archive_device_profile(db, user, profile_id, request)
