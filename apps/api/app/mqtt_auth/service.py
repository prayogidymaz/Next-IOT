"""EMQX HTTP authentication and ACL handlers."""

from __future__ import annotations

from datetime import UTC, datetime

from app.device_credentials.service import lookup_active_by_access_token
from app.models.device_credential import DeviceCredential
from app.mqtt_auth.acl import MqttAclDecision, evaluate_device_acl
from app.mqtt_auth.cache import CachedMqttCredential, get_cached_credential, set_cached_credential
from app.mqtt_auth.schemas import (
    MqttAclRequest,
    MqttAclResponse,
    MqttAuthRequest,
    MqttAuthResponse,
    MqttAuthResult,
)
from app.types.redis_client import RedisClient
from sqlalchemy.ext.asyncio import AsyncSession


def _resolve_username(payload: MqttAuthRequest) -> str:
    if payload.username.strip():
        return payload.username.strip()
    return payload.clientid.strip()


async def _resolve_credential(
    db: AsyncSession,
    redis: RedisClient,
    access_token: str,
) -> DeviceCredential | CachedMqttCredential | None:
    cached = await get_cached_credential(redis, access_token)
    if cached is not None:
        return cached

    credential = await lookup_active_by_access_token(db, access_token)
    if credential is None:
        # Never cache denials — avoids stale reject after rotate/generate.
        return None
    await set_cached_credential(
        redis,
        access_token,
        device_id=credential.device_id,
        tenant_id=credential.tenant_id,
    )
    return credential


async def handle_mqtt_auth(
    db: AsyncSession,
    redis: RedisClient,
    payload: MqttAuthRequest,
) -> MqttAuthResponse:
    token = _resolve_username(payload)
    if not token:
        return MqttAuthResponse(result=MqttAuthResult.DENY)

    resolved = await _resolve_credential(db, redis, token)
    if resolved is None:
        return MqttAuthResponse(result=MqttAuthResult.DENY)

    if isinstance(resolved, DeviceCredential):
        resolved.last_connected_at = datetime.now(UTC)
        await db.flush()

    return MqttAuthResponse(result=MqttAuthResult.ALLOW)


async def handle_mqtt_acl(
    db: AsyncSession,
    redis: RedisClient,
    payload: MqttAclRequest,
) -> MqttAclResponse:
    token = payload.username.strip() or payload.clientid.strip()
    if not token or not payload.topic:
        return MqttAclResponse(result=MqttAuthResult.DENY)

    resolved = await _resolve_credential(db, redis, token)
    if resolved is None:
        return MqttAclResponse(result=MqttAuthResult.DENY)

    if isinstance(resolved, CachedMqttCredential):
        tenant_id = resolved.tenant_id
        device_id = resolved.device_id
    else:
        tenant_id = resolved.tenant_id
        device_id = resolved.device_id

    decision = evaluate_device_acl(
        credential_tenant_id=tenant_id,
        credential_device_id=device_id,
        topic=payload.topic,
        action=payload.action,
    )
    if decision == MqttAclDecision.ALLOW:
        return MqttAclResponse(result=MqttAuthResult.ALLOW)
    return MqttAclResponse(result=MqttAuthResult.DENY)
