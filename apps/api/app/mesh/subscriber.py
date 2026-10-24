"""Mesh event subscriber helper (Redis fan-out from publisher)."""

from __future__ import annotations

import asyncio
import fnmatch
import json
import logging
from collections.abc import Awaitable, Callable

from app.mesh.event_bus import MeshDomain
from app.mesh.schemas import MeshContext, MeshEvent
from app.types.redis_client import RedisClient, close_pubsub

logger = logging.getLogger(__name__)

MeshEventHandler = Callable[[MeshEvent], Awaitable[None]]


class MeshEventSubscriber:
    def __init__(self, redis: RedisClient) -> None:
        self._redis = redis
        self._handlers: list[tuple[str, str, MeshEventHandler]] = []
        self._task: asyncio.Task[None] | None = None
        self._stopping = False

    def subscribe(self, domain_pattern: str, event_type_pattern: str, callback: MeshEventHandler) -> None:
        self._handlers.append((domain_pattern, event_type_pattern, callback))

    def _matches(self, domain: str, event_type: str, domain_pattern: str, event_type_pattern: str) -> bool:
        return fnmatch.fnmatch(domain, domain_pattern) and fnmatch.fnmatch(event_type, event_type_pattern)

    async def _dispatch(self, raw: str) -> None:
        try:
            data = json.loads(raw)
        except json.JSONDecodeError:
            return
        try:
            event = MeshEvent(
                event_id=data["event_id"],
                tenant_id=data["tenant_id"],
                device_id=data["device_id"],
                domain=MeshDomain(data["domain"]),
                event_type=str(data["event_type"]),
                timestamp=data["timestamp"],
                payload=data.get("payload", {}),
                context=MeshContext.model_validate(data.get("context", {})),
                correlation_id=data.get("correlation_id"),
                parent_event_id=data.get("parent_event_id"),
            )
        except (KeyError, ValueError):
            logger.debug("Skipping unparsable mesh event payload")
            return
        for domain_pattern, event_type_pattern, callback in self._handlers:
            if self._matches(event.domain.value, event.event_type, domain_pattern, event_type_pattern):
                await callback(event)

    async def listen_tenant(self, tenant_id: str) -> None:
        pubsub = self._redis.pubsub()
        channel = f"mesh:tenant:{tenant_id}"
        await pubsub.subscribe(channel)
        try:
            while not self._stopping:
                message = await pubsub.get_message(ignore_subscribe_messages=True, timeout=1.0)
                if message is None:
                    continue
                data_raw = message.get("data")
                if isinstance(data_raw, bytes):
                    await self._dispatch(data_raw.decode())
                elif isinstance(data_raw, str):
                    await self._dispatch(data_raw)
        finally:
            await close_pubsub(pubsub)

    def request_stop(self) -> None:
        self._stopping = True
