import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import (
    CurrentUser,
    RequireAuth,
    RequireOperator,
    RequireSuperAdmin,
    RequireTenantAdmin,
    get_current_user,
)
from app.auth.tiering import TIER_TO_LEVEL, SecurityTier
from app.deps import get_db
from app.models.tenant import Tenant
from app.models.user import User

router = APIRouter(prefix="/api/v1", tags=["protected"])


class MeResponse(BaseModel):
    user_id: uuid.UUID
    email: str
    role: str
    tenant_id: uuid.UUID
    security_tier: SecurityTier
    tier_level: int


class TenantProfileResponse(BaseModel):
    tenant_id: uuid.UUID
    name: str
    slug: str
    security_tier: SecurityTier
    tier_level: int


class UserSummary(BaseModel):
    id: uuid.UUID
    email: str
    role: str


class TenantListItem(BaseModel):
    id: uuid.UUID
    name: str
    slug: str
    security_tier: str


@router.get("/me", response_model=MeResponse)
async def get_me(user: RequireAuth):
    return MeResponse(
        user_id=user.user_id,
        email=user.email,
        role=user.role,
        tenant_id=user.tenant_id,
        security_tier=user.security_tier,
        tier_level=int(TIER_TO_LEVEL[user.security_tier]),
    )


@router.get("/tenants/{tenant_id}", response_model=TenantProfileResponse)
async def get_tenant_profile(
    tenant_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    user: CurrentUser = Depends(get_current_user),
):
    if not user.is_super_admin and user.tenant_id != tenant_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied: tenant isolation violation",
        )

    tenant = await db.scalar(select(Tenant).where(Tenant.id == tenant_id))
    if not tenant:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tenant not found")

    tier = SecurityTier(tenant.security_tier)
    return TenantProfileResponse(
        tenant_id=tenant.id,
        name=tenant.name,
        slug=tenant.slug,
        security_tier=tier,
        tier_level=int(TIER_TO_LEVEL[tier]),
    )


@router.get("/admin/users", response_model=list[UserSummary])
async def list_tenant_users(user: RequireTenantAdmin, db: AsyncSession = Depends(get_db)):
    """List users scoped to the caller's tenant (tenant isolation)."""
    result = await db.scalars(select(User).where(User.tenant_id == user.tenant_id))
    users = result.all()
    return [UserSummary(id=u.id, email=u.email, role=u.role) for u in users]


@router.post("/devices/command", status_code=204)
async def send_device_command(user: RequireOperator):
    """Stub write endpoint — operator+ only; viewer gets 403."""
    return None


@router.get("/super/tenants", response_model=list[TenantListItem])
async def list_all_tenants(user: RequireSuperAdmin, db: AsyncSession = Depends(get_db)):
    result = await db.scalars(select(Tenant))
    tenants = result.all()
    return [
        TenantListItem(id=t.id, name=t.name, slug=t.slug, security_tier=t.security_tier) for t in tenants
    ]
