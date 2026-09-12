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
from app.devices.service import _get_device_for_user
from app.models.user import User
from app.telemetry.video_feed.events import video_channel_for_device
from app.telemetry.video_feed.generator import MockVideoFrameGenerator
from app.telemetry.video_feed.parser import serialize_stream_info, serialize_video_frame

router = APIRouter(prefix="/api/v1/telemetry", tags=["telemetry-video"])

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


@router.websocket("/video-feed/{device_id}")
async def video_feed_websocket(
    websocket: WebSocket,
    device_id: uuid.UUID,
    token: str | None = Query(default=None),
):
    await websocket.accept()
    redis: aioredis.Redis = websocket.app.state.redis

    try:
        user = await _authenticate_ws(token)
    except WebSocketDisconnect:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return

    async with async_session() as db:
        try:
            await _get_device_for_user(db, device_id, user)
        except Exception:
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
            return

    generator = MockVideoFrameGenerator(device_id=str(device_id))
    await websocket.send_json(serialize_stream_info(generator.stream_info()))

    pubsub = redis.pubsub()
    channel = video_channel_for_device(str(device_id))
    await pubsub.subscribe(channel)
    stop_event = asyncio.Event()
    interval = 1.0 / generator.fps

    async def _stream_loop() -> None:
        try:
            while not stop_event.is_set():
                message = await pubsub.get_message(ignore_subscribe_messages=True, timeout=0.05)
                if message and message.get("type") == "message":
                    raw = message["data"]
                    try:
                        payload = json.loads(raw)
                        if payload.get("type") == "video_frame":
                            await websocket.send_json(payload)
                            await asyncio.sleep(interval)
                            continue
                    except json.JSONDecodeError:
                        pass

                frame = generator.next_frame()
                await websocket.send_json(serialize_video_frame(frame))
                await asyncio.sleep(interval)
        except WebSocketDisconnect:
            stop_event.set()
        except Exception:
            stop_event.set()

    stream_task = asyncio.create_task(_stream_loop())

    try:
        while not stop_event.is_set():
            try:
                await websocket.receive_text()
            except WebSocketDisconnect:
                break
    finally:
        stop_event.set()
        stream_task.cancel()
        await pubsub.unsubscribe(channel)
        await pubsub.aclose()
        try:
            await stream_task
        except asyncio.CancelledError:
            pass
