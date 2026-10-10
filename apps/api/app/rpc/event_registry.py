"""In-memory waiters for synchronous RPC (single API instance)."""

from __future__ import annotations

import asyncio
import uuid
from dataclasses import dataclass

from pydantic import JsonValue


@dataclass(frozen=True)
class RpcWaitResult:
    status: str
    response: JsonValue | None
    error: str | None


class RpcEventRegistry:
    def __init__(self) -> None:
        self._events: dict[uuid.UUID, asyncio.Event] = {}
        self._results: dict[uuid.UUID, RpcWaitResult] = {}

    async def register_wait(self, request_id: uuid.UUID, timeout_seconds: float) -> RpcWaitResult | None:
        event = asyncio.Event()
        self._events[request_id] = event
        try:
            await asyncio.wait_for(event.wait(), timeout=timeout_seconds)
        except TimeoutError:
            self._cleanup(request_id)
            return None
        result = self._results.pop(request_id, None)
        self._events.pop(request_id, None)
        return result

    def resolve(self, request_id: uuid.UUID, result: RpcWaitResult) -> None:
        self._results[request_id] = result
        event = self._events.get(request_id)
        if event is not None:
            event.set()

    def _cleanup(self, request_id: uuid.UUID) -> None:
        self._events.pop(request_id, None)
        self._results.pop(request_id, None)


rpc_event_registry = RpcEventRegistry()
