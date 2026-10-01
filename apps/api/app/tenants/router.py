import uuid

from fastapi import APIRouter

from app.auth import service as auth_service
from app.auth.dependencies import RequireAuth, RequireTenantAdmin
from app.auth.schemas import TokenResponse
from app.deps import DbSession, RedisDep
from app.tenants import service
from app.tenants.schemas import (
    TenantCreateRequest,
    TenantMemberInviteRequest,
    TenantMemberResponse,
    TenantSummary,
    TenantSwitchRequest,
)

router = APIRouter(prefix="/api/v1/tenants", tags=["tenants"])


@router.get("", response_model=list[TenantSummary])
async def list_tenants(user: RequireAuth, db: DbSession) -> list[TenantSummary]:
    return await service.list_accessible_tenants(db, user)


@router.post("", response_model=TenantSummary, status_code=201)
async def create_tenant(
    payload: TenantCreateRequest,
    user: RequireTenantAdmin,
    db: DbSession,
) -> TenantSummary:
    return await service.create_tenant(db, user, payload)


@router.post("/switch", response_model=TokenResponse)
async def switch_active_tenant(
    payload: TenantSwitchRequest,
    user: RequireAuth,
    db: DbSession,
    redis: RedisDep,
) -> TokenResponse:
    return await auth_service.switch_tenant(db, redis, user.user_id, payload.tenant_id)


@router.get("/{tenant_id}/members", response_model=list[TenantMemberResponse])
async def list_members(
    tenant_id: uuid.UUID,
    user: RequireAuth,
    db: DbSession,
) -> list[TenantMemberResponse]:
    return await service.list_tenant_members(db, user, tenant_id)


@router.post("/{tenant_id}/members", response_model=TenantMemberResponse, status_code=201)
async def invite_member(
    tenant_id: uuid.UUID,
    payload: TenantMemberInviteRequest,
    user: RequireTenantAdmin,
    db: DbSession,
) -> TenantMemberResponse:
    return await service.invite_tenant_member(db, user, tenant_id, payload)
