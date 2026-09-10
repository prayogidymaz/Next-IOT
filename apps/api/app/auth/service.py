import uuid

import jwt
import redis.asyncio as aioredis
from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.schemas import LoginRequest, RegisterRequest, RegisterResponse, TokenResponse, UserResponse
from app.auth.security import (
    TOKEN_TYPE_ACCESS,
    TOKEN_TYPE_REFRESH,
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
)
from app.config import settings
from app.models.tenant import Tenant
from app.models.user import User

REFRESH_KEY_PREFIX = "refresh:"


def _refresh_ttl_seconds() -> int:
    return settings.jwt_refresh_token_expire_days * 86400


async def _store_refresh_token(redis: aioredis.Redis, jti: str, user_id: uuid.UUID, tenant_id: uuid.UUID) -> None:
    key = f"{REFRESH_KEY_PREFIX}{jti}"
    value = f"{user_id}:{tenant_id}"
    await redis.set(key, value, ex=_refresh_ttl_seconds())


async def _is_refresh_token_active(redis: aioredis.Redis, jti: str) -> bool:
    return await redis.exists(f"{REFRESH_KEY_PREFIX}{jti}") == 1


async def _revoke_refresh_token(redis: aioredis.Redis, jti: str) -> None:
    await redis.delete(f"{REFRESH_KEY_PREFIX}{jti}")


async def _issue_tokens(redis: aioredis.Redis, user: User) -> TokenResponse:
    access_token = create_access_token(user_id=user.id, tenant_id=user.tenant_id, role=user.role)
    refresh_token, jti = create_refresh_token(user_id=user.id, tenant_id=user.tenant_id)
    await _store_refresh_token(redis, jti, user.id, user.tenant_id)
    return TokenResponse(access_token=access_token, refresh_token=refresh_token)


async def register(db: AsyncSession, redis: aioredis.Redis, payload: RegisterRequest) -> RegisterResponse:
    existing_slug = await db.scalar(select(Tenant).where(Tenant.slug == payload.tenant_slug))
    if existing_slug:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Tenant slug already exists")

    existing_email = await db.scalar(select(User).where(User.email == payload.email))
    if existing_email:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already registered")

    tenant = Tenant(name=payload.tenant_name, slug=payload.tenant_slug)
    user = User(
        tenant=tenant,
        email=payload.email,
        password_hash=hash_password(payload.password),
        role="tenant_admin",
    )
    db.add(tenant)
    db.add(user)
    await db.flush()

    tokens = await _issue_tokens(redis, user)

    return RegisterResponse(
        tenant_id=tenant.id,
        tenant_slug=tenant.slug,
        user=UserResponse.model_validate(user),
        tokens=tokens,
    )


async def login(db: AsyncSession, redis: aioredis.Redis, payload: LoginRequest) -> TokenResponse:
    user = await db.scalar(select(User).where(User.email == payload.email))
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")

    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User account is inactive")

    tenant = await db.scalar(select(Tenant).where(Tenant.id == user.tenant_id))
    if not tenant or not tenant.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Tenant is inactive")

    return await _issue_tokens(redis, user)


async def refresh_tokens(db: AsyncSession, redis: aioredis.Redis, refresh_token: str) -> TokenResponse:
    try:
        payload = decode_token(refresh_token)
    except jwt.PyJWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")

    if payload.get("type") != TOKEN_TYPE_REFRESH:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token type")

    jti = payload.get("jti")
    user_id = payload.get("sub")
    tenant_id = payload.get("tenant_id")

    if not jti or not user_id or not tenant_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token claims")

    if not await _is_refresh_token_active(redis, jti):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token revoked or expired")

    user = await db.scalar(select(User).where(User.id == uuid.UUID(user_id)))
    if not user or not user.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found or inactive")

    if str(user.tenant_id) != tenant_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Tenant mismatch")

    await _revoke_refresh_token(redis, jti)
    return await _issue_tokens(redis, user)


async def logout(redis: aioredis.Redis, refresh_token: str) -> None:
    try:
        payload = decode_token(refresh_token)
    except jwt.PyJWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")

    if payload.get("type") != TOKEN_TYPE_REFRESH:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token type")

    jti = payload.get("jti")
    if not jti:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token claims")

    await _revoke_refresh_token(redis, jti)


def decode_access_token(access_token: str) -> dict:
    try:
        payload = decode_token(access_token)
    except jwt.PyJWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid access token")

    if payload.get("type") != TOKEN_TYPE_ACCESS:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token type")

    return payload
