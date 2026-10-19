"""Server-Sent Events stream for tenant live updates."""

from __future__ import annotations

import json
import time
import uuid
from collections.abc import AsyncIterator
from typing import cast

import redis.asyncio as aioredis
from fastapi import APIRouter, HTTPException, Query, Request, status
from fastapi.responses import StreamingResponse
from pydantic import TypeAdapter
from sqlalchemy import select

from app.auth.rbac import UserRole, has_role
from app.auth.service import decode_access_token
from app.database import async_session
from app.models.user import User
from app.telemetry.ws_events import telemetry_channel_for_tenant
from app.types.json_types import JsonObject, as_json_str
from app.types.redis_client import RedisClient, close_pubsub

router = APIRouter(prefix="/api/v1/realtime", tags=["realtime"])

_ALLOWED_CHANNELS = frozenset({"telemetry", "alarms", "device_status", "rule_executions"})
_VIEWER_ROLES = frozenset(
    {UserRole.VIEWER, UserRole.OPERATOR, UserRole.TENANT_ADMIN, UserRole.SUPER_ADMIN}
)
_MAX_EVENTS_PER_SECOND = 100
_JSON_OBJECT = TypeAdapter(JsonObject)


def _parse_channels(raw: str | None) -> frozenset[str]:
    if not raw or not raw.strip():
        return frozenset({"telemetry", "alarms", "device_status", "rule_executions"})
    parts = {p.strip() for p in raw.split(",") if p.strip()}
    invalid = parts - _ALLOWED_CHANNELS
    if invalid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid channels: {', '.join(sorted(invalid))}",
        )
    return frozenset(parts)


async def _authenticate_token(token: str | None) -> tuple[uuid.UUID, str]:
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing token")
    payload = decode_access_token(token)
    user_id = as_json_str(payload.get("sub"))
    tenant_id = as_json_str(payload.get("tenant_id"))
    role = as_json_str(payload.get("role"))
    if user_id is None or tenant_id is None or role is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    if not has_role(role, set(_VIEWER_ROLES)):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")

    async with async_session() as db:
        user = await db.scalar(select(User).where(User.id == uuid.UUID(user_id)))
        if user is None or not user.is_active:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid user")
        if str(user.tenant_id) != tenant_id and role != UserRole.SUPER_ADMIN.value:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Tenant mismatch")

    return uuid.UUID(tenant_id), tenant_id


def _map_event_channel(message: JsonObject) -> str:
    event_type = as_json_str(message.get("type")) or ""
    lowered = event_type.lower()
    if "alarm" in lowered:
        return "alarms"
    if "rule" in lowered or "automation" in lowered:
        return "rule_executions"
    if "device" in lowered and "status" in lowered:
        return "device_status"
    if "telemetry" in lowered or event_type in {"telemetry_point", "telemetry"}:
        return "telemetry"
    return "telemetry"


async def _sse_generator(
    request: Request,
    *,
    tenant_id: str,
    channels: frozenset[str],
) -> AsyncIterator[bytes]:
    state_redis: object = request.app.state.redis
    if not isinstance(state_redis, aioredis.Redis):
        yield b"event: error\ndata: {\"detail\":\"redis_unavailable\"}\n\n"
        return
    redis = cast(RedisClient, state_redis)

    pubsub = redis.pubsub()

    window_start = time.monotonic()
    events_in_window = 0

    try:
        yield b"event: connected\ndata: {\"status\":\"ok\"}\n\n"
        await pubsub.subscribe(telemetry_channel_for_tenant(tenant_id))
        while True:
            if await request.is_disconnected():
                break

            now = time.monotonic()
            if now - window_start >= 1.0:
                window_start = now
                events_in_window = 0

            message = await pubsub.get_message(ignore_subscribe_messages=True, timeout=1.0)
            if message is None:
                ping = json.dumps({"ts": time.time(), "channel": "heartbeat"})
                yield f"event: heartbeat\ndata: {ping}\n\n".encode()
                continue

            data_raw = message.get("data")
            if not isinstance(data_raw, bytes | str):
                continue
            text = data_raw.decode() if isinstance(data_raw, bytes) else data_raw
            try:
                parsed = _JSON_OBJECT.validate_json(text)
            except Exception:
                continue

            channel = _map_event_channel(parsed)
            if channel not in channels:
                continue

            events_in_window += 1
            if events_in_window > _MAX_EVENTS_PER_SECOND:
                continue

            envelope = json.dumps({"channel": channel, "payload": parsed}, default=str)
            yield f"event: {channel}\ndata: {envelope}\n\n".encode()
    finally:
        await close_pubsub(pubsub)


@router.get("/stream")
async def realtime_stream(
    request: Request,
    token: str | None = Query(default=None, description="Bearer access token (SSE cannot set Authorization header)"),
    channels: str | None = Query(default=None, description="Comma-separated channel filter"),
) -> StreamingResponse:
    """SSE stream filtered by tenant_id from JWT."""
    selected = _parse_channels(channels)
    _, tenant_id = await _authenticate_token(token)

    return StreamingResponse(
        _sse_generator(request, tenant_id=tenant_id, channels=selected),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )
