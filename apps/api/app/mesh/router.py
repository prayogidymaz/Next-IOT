"""Mesh events HTTP API."""

from __future__ import annotations

import json
import uuid
from collections.abc import AsyncIterator
from datetime import datetime

from fastapi import APIRouter, Query, Request
from fastapi.responses import StreamingResponse
from pydantic import JsonValue

from app.auth.dependencies import RequireAuth
from app.deps import DbSession, RedisDep
from app.mesh.event_bus import MeshDomain, mesh_tenant_fanout_channel
from app.mesh.schemas import MeshEventPublishRequest, MeshEventResponse
from app.mesh.service import get_mesh_event, list_mesh_events, mesh_event_chain, publish_mesh_event_for_user
from app.types.redis_client import RedisClient, close_pubsub

router = APIRouter(prefix="/api/v1/mesh", tags=["mesh"])


@router.post("/events", response_model=MeshEventResponse, status_code=201)
async def publish_mesh_event(
    user: RequireAuth,
    db: DbSession,
    payload: MeshEventPublishRequest,
) -> MeshEventResponse:
    return await publish_mesh_event_for_user(
        db,
        user,
        device_id=payload.device_id,
        domain=payload.domain,
        event_type=payload.event_type,
        payload=payload.payload,
        correlation_id=payload.correlation_id,
        parent_event_id=payload.parent_event_id,
        context=payload.context,
    )


@router.get("/events", response_model=list[MeshEventResponse])
async def query_mesh_events(
    user: RequireAuth,
    db: DbSession,
    domain: MeshDomain | None = None,
    event_type: str | None = None,
    device_id: uuid.UUID | None = None,
    since: datetime | None = None,
    until: datetime | None = None,
    limit: int = Query(default=50, ge=1, le=200),
) -> list[MeshEventResponse]:
    return await list_mesh_events(
        db,
        user,
        domain=domain,
        event_type=event_type,
        device_id=device_id,
        since=since,
        until=until,
        limit=limit,
    )


async def _mesh_sse_generator(
    request: Request,
    redis: RedisClient,
    tenant_id: str,
) -> AsyncIterator[bytes]:
    pubsub = redis.pubsub()
    channel = mesh_tenant_fanout_channel(tenant_id)
    await pubsub.subscribe(channel)
    try:
        yield b"event: connected\ndata: {\"status\":\"ok\"}\n\n"
        while True:
            if await request.is_disconnected():
                break
            message = await pubsub.get_message(ignore_subscribe_messages=True, timeout=1.0)
            if message is None:
                continue
            data_raw = message.get("data")
            text = data_raw.decode() if isinstance(data_raw, bytes) else str(data_raw)
            payload: dict[str, JsonValue] = json.loads(text)
            yield f"event: mesh\ndata: {json.dumps(payload, default=str)}\n\n".encode()
    finally:
        await close_pubsub(pubsub)


@router.get("/events/stream")
async def mesh_events_stream(
    request: Request,
    user: RequireAuth,
    redis: RedisDep,
) -> StreamingResponse:
    tenant_id = str(user.tenant_id)
    return StreamingResponse(
        _mesh_sse_generator(request, redis, tenant_id),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "Connection": "keep-alive", "X-Accel-Buffering": "no"},
    )


@router.get("/events/{event_id}", response_model=MeshEventResponse)
async def get_mesh_event_detail(user: RequireAuth, db: DbSession, event_id: uuid.UUID) -> MeshEventResponse:
    return await get_mesh_event(db, user, event_id)


@router.get("/events/{event_id}/chain", response_model=list[MeshEventResponse])
async def get_mesh_event_chain(user: RequireAuth, db: DbSession, event_id: uuid.UUID) -> list[MeshEventResponse]:
    return await mesh_event_chain(db, user, event_id)
