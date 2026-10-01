import uuid

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.rbac import is_super_admin
from app.models.tenant import Tenant
from app.models.tenant_membership import TenantMembership
from app.models.user import User


async def resolve_active_session(
    db: AsyncSession,
    user: User,
    jwt_tenant_id: uuid.UUID,
    jwt_role: str | None = None,
) -> tuple[uuid.UUID, str]:
    """Resolve active tenant + effective role from JWT context."""
    tenant = await db.scalar(select(Tenant).where(Tenant.id == jwt_tenant_id))
    if not tenant or not tenant.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Tenant is inactive")

    if is_super_admin(user.role):
        return jwt_tenant_id, user.role

    if user.tenant_id == jwt_tenant_id:
        return jwt_tenant_id, user.role

    membership = await db.scalar(
        select(TenantMembership).where(
            TenantMembership.user_id == user.id,
            TenantMembership.tenant_id == jwt_tenant_id,
        )
    )
    if not membership:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Tenant mismatch")

    return jwt_tenant_id, membership.role
