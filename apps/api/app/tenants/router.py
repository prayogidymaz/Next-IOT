import uuid

from fastapi import APIRouter, Query, Response
from typing import Annotated

from app.auth import service as auth_service
from app.auth.dependencies import RequireAuth, RequireTenantAdmin
from app.auth.schemas import TokenResponse
from app.deps import DbSession, RedisDep
from app.tenants import service
from app.tenants.members.invite import (
    InvitationView,
    InviteEmailRequest,
    cancel_invitation,
    create_email_invite,
    list_invitations,
    resend_invitation,
)
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
    search: Annotated[str | None, Query(max_length=120)] = None,
) -> list[TenantMemberResponse]:
    return await service.list_tenant_members(db, user, tenant_id, search=search)


@router.post("/{tenant_id}/members", response_model=TenantMemberResponse, status_code=201)
async def invite_member(
    tenant_id: uuid.UUID,
    payload: TenantMemberInviteRequest,
    user: RequireTenantAdmin,
    db: DbSession,
) -> TenantMemberResponse:
    return await service.invite_tenant_member(db, user, tenant_id, payload)


@router.post("/{tenant_id}/members/invite", response_model=InvitationView, status_code=201)
async def invite_member_email(
    tenant_id: uuid.UUID,
    payload: InviteEmailRequest,
    user: RequireTenantAdmin,
    db: DbSession,
) -> InvitationView:
    return await create_email_invite(db, user, tenant_id, payload)


@router.get("/{tenant_id}/members/invitations", response_model=list[InvitationView])
async def list_member_invitations(
    tenant_id: uuid.UUID,
    user: RequireTenantAdmin,
    db: DbSession,
) -> list[InvitationView]:
    return await list_invitations(db, user, tenant_id)


@router.delete("/{tenant_id}/members/invitations/{invite_id}", status_code=204, response_class=Response)
async def cancel_member_invitation(
    tenant_id: uuid.UUID,
    invite_id: uuid.UUID,
    user: RequireTenantAdmin,
    db: DbSession,
) -> Response:
    await cancel_invitation(db, user, tenant_id, invite_id)
    return Response(status_code=204)


@router.post("/{tenant_id}/members/invitations/{invite_id}/resend", response_model=InvitationView)
async def resend_member_invitation(
    tenant_id: uuid.UUID,
    invite_id: uuid.UUID,
    user: RequireTenantAdmin,
    db: DbSession,
) -> InvitationView:
    return await resend_invitation(db, user, tenant_id, invite_id)
