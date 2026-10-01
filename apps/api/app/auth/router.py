import redis.asyncio as aioredis
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.audit.actions import AuditAction
from app.audit.service import client_ip, record_audit_event
from app.auth import service
from app.auth.dependencies import RequireAuth
from app.auth.permissions import permissions_for_role
from app.auth.schemas import (
    AuthMeResponse,
    LoginRequest,
    LogoutRequest,
    MessageResponse,
    RefreshRequest,
    RegisterRequest,
    RegisterResponse,
    TokenResponse,
)
from app.deps import get_db, get_redis
from app.models.user import User

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=RegisterResponse, status_code=201)
async def register(
    payload: RegisterRequest,
    db: AsyncSession = Depends(get_db),
    redis: aioredis.Redis = Depends(get_redis),
):
    return await service.register(db, redis, payload)


@router.post("/login", response_model=TokenResponse)
async def login(
    request: Request,
    payload: LoginRequest,
    db: AsyncSession = Depends(get_db),
    redis: aioredis.Redis = Depends(get_redis),
):
    ip = client_ip(request)
    try:
        tokens = await service.login(db, redis, payload)
    except HTTPException as exc:
        if exc.status_code in {401, 403}:
            await record_audit_event(
                db,
                action=AuditAction.LOGIN,
                actor_email=payload.email,
                resource_target="auth/login",
                ip_address=ip,
                status="failure",
            )
        raise

    user = await db.scalar(select(User).where(User.email == payload.email))
    if user:
        await record_audit_event(
            db,
            action=AuditAction.LOGIN,
            actor_id=user.id,
            actor_email=user.email,
            tenant_id=user.tenant_id,
            resource_target="auth/login",
            ip_address=ip,
            status="success",
        )
    return tokens


@router.post("/refresh", response_model=TokenResponse)
async def refresh(
    payload: RefreshRequest,
    db: AsyncSession = Depends(get_db),
    redis: aioredis.Redis = Depends(get_redis),
):
    return await service.refresh_tokens(db, redis, payload.refresh_token)


@router.post("/logout", response_model=MessageResponse)
async def logout(
    payload: LogoutRequest,
    redis: aioredis.Redis = Depends(get_redis),
):
    await service.logout(redis, payload.refresh_token)
    return MessageResponse(message="Logged out successfully")


@router.get("/me", response_model=AuthMeResponse)
async def get_auth_me(user: RequireAuth):
    return AuthMeResponse(
        user_id=user.user_id,
        email=user.email,
        role=user.role,
        tenant_id=user.tenant_id,
        permissions=permissions_for_role(user.role),
    )
