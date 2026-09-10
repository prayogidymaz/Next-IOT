import uuid
from dataclasses import dataclass
from typing import Annotated, Callable

import redis.asyncio as aioredis
from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.rate_limit import enforce_rate_limit
from app.auth.rbac import UserRole, has_role, is_super_admin
from app.auth.service import decode_access_token
from app.auth.tiering import SecurityTier, parse_tier
from app.deps import get_db, get_redis
from app.models.tenant import Tenant
from app.models.user import User

bearer_scheme = HTTPBearer(auto_error=False)


@dataclass(frozen=True)
class CurrentUser:
    user_id: uuid.UUID
    tenant_id: uuid.UUID
    email: str
    role: str
    security_tier: SecurityTier

    @property
    def is_super_admin(self) -> bool:
        return is_super_admin(self.role)


async def get_current_user(
    request: Request,
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer_scheme)],
    db: AsyncSession = Depends(get_db),
    redis: aioredis.Redis = Depends(get_redis),
) -> CurrentUser:
    if credentials is None or credentials.scheme.lower() != "bearer":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")

    payload = decode_access_token(credentials.credentials)
    user_id = payload.get("sub")
    tenant_id = payload.get("tenant_id")
    role = payload.get("role")

    if not user_id or not tenant_id or not role:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token claims")

    user = await db.scalar(select(User).where(User.id == uuid.UUID(user_id)))
    if not user or not user.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found or inactive")

    if str(user.tenant_id) != tenant_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Tenant mismatch")

    tenant = await db.scalar(select(Tenant).where(Tenant.id == user.tenant_id))
    if not tenant or not tenant.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Tenant is inactive")

    tier = parse_tier(tenant.security_tier)
    current = CurrentUser(
        user_id=user.id,
        tenant_id=user.tenant_id,
        email=user.email,
        role=user.role,
        security_tier=tier,
    )

    await enforce_rate_limit(
        redis,
        tenant_id=str(current.tenant_id),
        user_id=str(current.user_id),
        security_tier=current.security_tier,
    )

    request.state.current_user = current
    return current


def require_roles(*allowed_roles: UserRole | str) -> Callable:
    allowed = {str(r) for r in allowed_roles}

    async def _checker(user: CurrentUser = Depends(get_current_user)) -> CurrentUser:
        if not has_role(user.role, allowed):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Role '{user.role}' is not authorized. Required: {sorted(allowed)}",
            )
        return user

    return _checker


async def require_tenant_access(
    tenant_id: uuid.UUID,
    user: CurrentUser = Depends(get_current_user),
) -> CurrentUser:
    if user.is_super_admin:
        return user
    if user.tenant_id != tenant_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied: tenant isolation violation",
        )
    return user


# Shortcuts
RequireAuth = Annotated[CurrentUser, Depends(get_current_user)]
RequireTenantAdmin = Annotated[CurrentUser, Depends(require_roles(UserRole.TENANT_ADMIN, UserRole.SUPER_ADMIN))]
RequireOperator = Annotated[
    CurrentUser,
    Depends(require_roles(UserRole.OPERATOR, UserRole.TENANT_ADMIN, UserRole.SUPER_ADMIN)),
]
RequireSuperAdmin = Annotated[CurrentUser, Depends(require_roles(UserRole.SUPER_ADMIN))]
