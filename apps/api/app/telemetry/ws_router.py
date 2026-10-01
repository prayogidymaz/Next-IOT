import asyncio
import json
import uuid

import redis.asyncio as aioredis
from fastapi import APIRouter, Query, WebSocket, WebSocketDisconnect, status
from sqlalchemy import select

from app.auth.dependencies import CurrentUser
from app.auth.rbac import UserRole, has_role
from app.auth.service import decode_access_token
from app.auth.tiering import SecurityTier
from app.commands.events import DEVICE_COMMANDS_CHANNEL
from app.database import async_session
from app.models.user import User
from app.telemetry.ws_events import publish_control_center_event, telemetry_channel_for_tenant

VIEWER_ROLES = frozenset(
    {UserRole.VIEWER, UserRole.OPERATOR, UserRole.TENANT_ADMIN, UserRole.SUPER_ADMIN}
)

router = APIRouter(prefix="/api/v1/ws", tags=["telemetry-ws"])


async def _authenticate_ws(token: str | None) -> CurrentUser:
    if not token:
        raise WebSocketDisconnect(code=status.WS_1008_POLICY_VIOLATION)

    payload = decode_access_token(token)
    user_id = payload.get("sub")
    tenant_id = payload.get("tenant_id")
    role = payload.get("role")
    if not user_id or not tenant_id or not role:
        raise WebSocketDisconnect(code=status.WS_1008_POLICY_VIOLATION)
    if not has_role(role, VIEWER_ROLES):
        raise WebSocketDisconnect(code=status.WS_1008_POLICY_VIOLATION)

    async with async_session() as db:
        user = await db.scalar(select(User).where(User.id == uuid.UUID(user_id)))
        if user is None or not user.is_active:
            raise WebSocketDisconnect(code=status.WS_1008_POLICY_VIOLATION)
        if str(user.tenant_id) != tenant_id:
            raise WebSocketDisconnect(code=status.WS_1008_POLICY_VIOLATION)

    return CurrentUser(
        user_id=uuid.UUID(user_id),
        tenant_id=uuid.UUID(tenant_id),
        email=user.email,
        role=role,
        security_tier=SecurityTier.FREE,
    )


@router.websocket("/telemetry")
async def telemetry_control_websocket(
    websocket: WebSocket,
    token: str | None = Query(default=None),
):
    """Live telemetry + control audit stream for Tactical Control Center."""
    await websocket.accept()
    redis: aioredis.Redis = websocket.app.state.redis
    if redis is None:
        await websocket.close(code=status.WS_1011_INTERNAL_ERROR)
        return

    try:
        user = await _authenticate_ws(token)
    except WebSocketDisconnect:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return

    tenant_id = str(user.tenant_id)
    tenant_channel = telemetry_channel_for_tenant(tenant_id)
    pubsub = redis.pubsub()
    await pubsub.subscribe(tenant_channel, DEVICE_COMMANDS_CHANNEL)

    async def _forward_messages() -> None:
        while True:
            message = await pubsub.get_message(ignore_subscribe_messages=True, timeout=1.0)
            if message and message.get("type") == "message":
                raw = message.get("data")
                if isinstance(raw, bytes):
                    raw = raw.decode()
                if not isinstance(raw, str):
                    raw = json.dumps(raw)
                try:
                    payload = json.loads(raw)
                except json.JSONDecodeError:
                    continue
                if message.get("channel") == DEVICE_COMMANDS_CHANNEL:
                    if str(payload.get("tenant_id")) != tenant_id:
                        continue
                    payload = {
                        "type": "audit.command",
                        "tenant_id": tenant_id,
                        "device_id": payload.get("device_id"),
                        "command_type": payload.get("command_type"),
                        "params": payload.get("params"),
                        "command_id": payload.get("command_id"),
                    }
                await websocket.send_json(payload)
            await asyncio.sleep(0.02)

    forward_task = asyncio.create_task(_forward_messages())
    try:
        while True:
            text = await websocket.receive_text()
            try:
                data = json.loads(text)
            except json.JSONDecodeError:
                continue
            msg_type = data.get("type")
            if msg_type in {"relay.toggle", "emergency.stop", "control.audit"}:
                await publish_control_center_event(
                    redis,
                    tenant_id=tenant_id,
                    event_type="audit.control",
                    payload={
                        "actor": user.email,
                        "action": msg_type,
                        "details": data.get("details") or {},
                        "domain": data.get("domain"),
                    },
                )
    except WebSocketDisconnect:
        pass
    finally:
        forward_task.cancel()
        await pubsub.unsubscribe(tenant_channel, DEVICE_COMMANDS_CHANNEL)
        await pubsub.aclose()
