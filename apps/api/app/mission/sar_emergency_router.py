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
from app.database import async_session
from app.mission.sar_emergency_events import sar_emergency_channel_for_tenant
from app.models.user import User

VIEWER_ROLES = frozenset(
    {UserRole.VIEWER, UserRole.OPERATOR, UserRole.TENANT_ADMIN, UserRole.SUPER_ADMIN}
)


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


router = APIRouter(prefix="/api/v1/mission", tags=["mission-sar-emergency"])


@router.websocket("/sar-incidents/ws")
async def sar_incidents_websocket(
    websocket: WebSocket,
    token: str | None = Query(default=None),
):
    """Subscribe to SAR emergency alert broadcasts for the authenticated tenant."""
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

    channel = sar_emergency_channel_for_tenant(str(user.tenant_id))
    pubsub = redis.pubsub()
    await pubsub.subscribe(channel)

    async def _forward_messages() -> None:
        while True:
            message = await pubsub.get_message(ignore_subscribe_messages=True, timeout=1.0)
            if message and message.get("type") == "message":
                data = message.get("data")
                if isinstance(data, bytes):
                    data = data.decode()
                await websocket.send_text(data if isinstance(data, str) else json.dumps(data))
            await asyncio.sleep(0.05)

    forward_task = asyncio.create_task(_forward_messages())
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        pass
    finally:
        forward_task.cancel()
        await pubsub.unsubscribe(channel)
        await pubsub.aclose()
