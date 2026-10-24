"""Background listener: mesh events → workflow executor."""

from __future__ import annotations

import asyncio
import json
import logging
import uuid
from datetime import datetime

from app.database import async_session
from app.mesh.event_bus import MeshDomain
from app.mesh.schemas import MeshContext, MeshEvent
from app.mesh.workflow_executor import get_mesh_workflow_executor
from app.mesh.workflow_registry import matching_workflows, reload_workflows
from app.types.redis_client import RedisClient, close_pubsub

logger = logging.getLogger(__name__)


async def _parse_mesh_event(raw: str) -> MeshEvent | None:
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        return None
    try:
        ts_raw = data["timestamp"]
        if isinstance(ts_raw, str):
            timestamp = datetime.fromisoformat(ts_raw.replace("Z", "+00:00"))
        elif isinstance(ts_raw, datetime):
            timestamp = ts_raw
        else:
            return None
        return MeshEvent(
            event_id=uuid.UUID(str(data["event_id"])),
            tenant_id=uuid.UUID(str(data["tenant_id"])),
            device_id=uuid.UUID(str(data["device_id"])),
            domain=MeshDomain(str(data["domain"])),
            event_type=str(data["event_type"]),
            timestamp=timestamp,
            payload=data.get("payload", {}),
            context=MeshContext.model_validate(data.get("context", {})),
            correlation_id=uuid.UUID(str(data["correlation_id"])) if data.get("correlation_id") else None,
            parent_event_id=uuid.UUID(str(data["parent_event_id"])) if data.get("parent_event_id") else None,
        )
    except (KeyError, ValueError):
        return None


async def _handle_mesh_event(redis: RedisClient, event: MeshEvent) -> None:
    executor = get_mesh_workflow_executor()
    if executor is None:
        return
    workflows = matching_workflows(event)
    if not workflows:
        return
    for workflow_id, definition in workflows:
        dedup_key = f"mesh:wf:dedup:{event.event_id}:{workflow_id}"
        claimed = await redis.set(dedup_key, "1", nx=True, ex=3600)
        if not claimed:
            continue
        async with async_session() as db:
            try:
                await executor.execute(
                    db,
                    workflow_id=workflow_id,
                    tenant_id=event.tenant_id,
                    definition=definition,
                    trigger_event=event,
                    dry_run=False,
                )
                await db.commit()
            except Exception:
                await db.rollback()
                logger.exception("Workflow listener execution failed workflow_id=%s", workflow_id)


async def mesh_workflow_listener_loop(redis: RedisClient, stop_event: asyncio.Event) -> None:
    async with async_session() as db:
        await reload_workflows(db)
        await db.commit()
    pubsub = redis.pubsub()
    await pubsub.psubscribe("mesh:tenant:*")
    logger.info("Mesh workflow listener started (psubscribe mesh:tenant:*)")
    try:
        while not stop_event.is_set():
            message = await pubsub.get_message(ignore_subscribe_messages=True, timeout=1.0)
            if message is None:
                continue
            data_raw = message.get("data")
            if data_raw is None:
                continue
            text = data_raw.decode() if isinstance(data_raw, bytes) else str(data_raw)
            event = await _parse_mesh_event(text)
            if event is None:
                continue
            asyncio.create_task(_handle_mesh_event(redis, event))
    finally:
        await close_pubsub(pubsub)
