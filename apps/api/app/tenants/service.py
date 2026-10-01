import uuid

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.context import CurrentUser
from app.auth.rbac import UserRole, is_super_admin
from app.auth.security import hash_password
from app.models.tenant import Tenant
from app.models.tenant_membership import TenantMembership
from app.models.user import User
from app.tenants.schemas import (
    TenantCreateRequest,
    TenantMemberInviteRequest,
    TenantMemberResponse,
    TenantSummary,
)


def _normalize_role(role: str) -> str:
    value = role.lower().replace("-", "_")
    allowed = {UserRole.TENANT_ADMIN, UserRole.OPERATOR, UserRole.VIEWER}
    if value not in allowed:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Invalid role. Allowed: {sorted(allowed)}",
        )
    return value


async def list_accessible_tenants(db: AsyncSession, user: CurrentUser) -> list[TenantSummary]:
    if user.is_super_admin:
        tenants = (await db.scalars(select(Tenant).order_by(Tenant.name))).all()
        return [
            TenantSummary(
                id=t.id,
                name=t.name,
                slug=t.slug,
                security_tier=t.security_tier,
                is_active=t.is_active,
                membership_role=UserRole.SUPER_ADMIN,
            )
            for t in tenants
        ]

    rows = await db.scalars(
        select(TenantMembership).where(TenantMembership.user_id == user.user_id)
    )
    memberships = rows.all()
    if not memberships:
        tenant = await db.scalar(select(Tenant).where(Tenant.id == user.tenant_id))
        if tenant:
            return [
                TenantSummary(
                    id=tenant.id,
                    name=tenant.name,
                    slug=tenant.slug,
                    security_tier=tenant.security_tier,
                    is_active=tenant.is_active,
                    membership_role=user.role,
                )
            ]
        return []

    tenant_ids = [m.tenant_id for m in memberships]
    tenants = (await db.scalars(select(Tenant).where(Tenant.id.in_(tenant_ids)))).all()
    role_by_tenant = {m.tenant_id: m.role for m in memberships}
    return [
        TenantSummary(
            id=t.id,
            name=t.name,
            slug=t.slug,
            security_tier=t.security_tier,
            is_active=t.is_active,
            membership_role=role_by_tenant.get(t.id),
        )
        for t in sorted(tenants, key=lambda x: x.name.lower())
    ]


async def create_tenant(
    db: AsyncSession,
    user: CurrentUser,
    payload: TenantCreateRequest,
) -> TenantSummary:
    if not user.is_super_admin and user.role != UserRole.TENANT_ADMIN:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to create tenants")

    existing = await db.scalar(select(Tenant).where(Tenant.slug == payload.slug))
    if existing:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Tenant slug already exists")

    tenant = Tenant(name=payload.name, slug=payload.slug)
    db.add(tenant)
    await db.flush()

    db.add(
        TenantMembership(
            user_id=user.user_id,
            tenant_id=tenant.id,
            role=UserRole.TENANT_ADMIN,
        )
    )
    await db.commit()
    await db.refresh(tenant)

    return TenantSummary(
        id=tenant.id,
        name=tenant.name,
        slug=tenant.slug,
        security_tier=tenant.security_tier,
        is_active=tenant.is_active,
        membership_role=UserRole.TENANT_ADMIN,
    )


async def user_can_access_tenant(db: AsyncSession, user: User, tenant_id: uuid.UUID) -> bool:
    if is_super_admin(user.role):
        return True
    if user.tenant_id == tenant_id:
        return True
    membership = await db.scalar(
        select(TenantMembership).where(
            TenantMembership.user_id == user.id,
            TenantMembership.tenant_id == tenant_id,
        )
    )
    return membership is not None


async def list_tenant_members(
    db: AsyncSession,
    user: CurrentUser,
    tenant_id: uuid.UUID,
) -> list[TenantMemberResponse]:
    await _require_tenant_admin(db, user, tenant_id)

    memberships = (
        await db.scalars(select(TenantMembership).where(TenantMembership.tenant_id == tenant_id))
    ).all()
    if not memberships:
        owner = await db.scalar(select(User).where(User.tenant_id == tenant_id))
        if owner:
            return [
                TenantMemberResponse(
                    user_id=owner.id,
                    email=owner.email,
                    role=owner.role,
                    is_active=owner.is_active,
                    created_at=owner.created_at,
                )
            ]
        return []

    user_ids = [m.user_id for m in memberships]
    users = (await db.scalars(select(User).where(User.id.in_(user_ids)))).all()
    role_by_user = {m.user_id: m.role for m in memberships}
    return [
        TenantMemberResponse(
            user_id=u.id,
            email=u.email,
            role=role_by_user.get(u.id, u.role),
            is_active=u.is_active,
            created_at=u.created_at,
        )
        for u in sorted(users, key=lambda x: x.email.lower())
    ]


async def invite_tenant_member(
    db: AsyncSession,
    user: CurrentUser,
    tenant_id: uuid.UUID,
    payload: TenantMemberInviteRequest,
) -> TenantMemberResponse:
    await _require_tenant_admin(db, user, tenant_id)
    role = _normalize_role(payload.role)

    existing = await db.scalar(select(User).where(User.email == payload.email))
    if existing:
        dup = await db.scalar(
            select(TenantMembership).where(
                TenantMembership.user_id == existing.id,
                TenantMembership.tenant_id == tenant_id,
            )
        )
        if dup:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="User already in tenant")
        db.add(TenantMembership(user_id=existing.id, tenant_id=tenant_id, role=role))
        await db.commit()
        return TenantMemberResponse(
            user_id=existing.id,
            email=existing.email,
            role=role,
            is_active=existing.is_active,
            created_at=existing.created_at,
        )

    new_user = User(
        tenant_id=tenant_id,
        email=payload.email,
        password_hash=hash_password(payload.password),
        role=role,
    )
    db.add(new_user)
    await db.flush()
    db.add(TenantMembership(user_id=new_user.id, tenant_id=tenant_id, role=role))
    await db.commit()
    await db.refresh(new_user)

    return TenantMemberResponse(
        user_id=new_user.id,
        email=new_user.email,
        role=role,
        is_active=new_user.is_active,
        created_at=new_user.created_at,
    )


async def _require_tenant_admin(db: AsyncSession, user: CurrentUser, tenant_id: uuid.UUID) -> None:
    if user.is_super_admin and user.tenant_id == tenant_id:
        return
    if user.is_super_admin:
        tenant = await db.scalar(select(Tenant).where(Tenant.id == tenant_id))
        if tenant:
            return
    if user.tenant_id == tenant_id and user.role in {UserRole.TENANT_ADMIN, UserRole.SUPER_ADMIN}:
        return
    membership = await db.scalar(
        select(TenantMembership).where(
            TenantMembership.user_id == user.user_id,
            TenantMembership.tenant_id == tenant_id,
            TenantMembership.role == UserRole.TENANT_ADMIN,
        )
    )
    if membership is None:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Tenant admin required")
