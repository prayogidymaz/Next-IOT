"""Orchestrate auto-response chains for mesh events."""

from __future__ import annotations

import uuid
from dataclasses import dataclass

from sqlalchemy.ext.asyncio import AsyncSession

from app.agents.responder.chain_definitions import CHAIN_REGISTRY
from app.agents.responder.chain_executor import ChainExecutor
from app.mesh.schemas import MeshEvent
from app.types.json_types import JsonObject
from app.types.redis_client import RedisClient


@dataclass(frozen=True)
class ChainExecution:
    execution_id: uuid.UUID
    chain_id: str
    tenant_id: uuid.UUID
    status: str


class ResponseChain:
    def __init__(self, db: AsyncSession, redis: RedisClient) -> None:
        self._executor = ChainExecutor(db, redis)

    async def orchestrate(self, trigger_event: MeshEvent) -> ChainExecution:
        chain_id = self._chain_for_event(trigger_event)
        context: JsonObject = {
            "event_id": str(trigger_event.event_id),
            "event_type": trigger_event.event_type,
            "device_id": str(trigger_event.device_id),
            "payload": trigger_event.payload,
        }
        row = await self._executor.start(
            chain_id,
            trigger_event.tenant_id,
            trigger_event.event_id,
            context,
        )
        await self._executor.run_next_step(row.id)
        return ChainExecution(
            execution_id=row.id,
            chain_id=row.chain_id,
            tenant_id=row.tenant_id,
            status=row.status,
        )

    @staticmethod
    def _chain_for_event(event: MeshEvent) -> str:
        if event.domain.value == "vision" and event.event_type in {"detection", "anomaly_detected"}:
            return "pest_response"
        if event.event_type == "threshold_exceeded":
            return "irrigation_smart"
        if event.event_type in {"battery_low", "reading_update"}:
            payload = event.payload
            if isinstance(payload, dict) and payload.get("offline") is True:
                return "device_health"
        return "device_health" if event.event_type == "battery_low" else "irrigation_smart"

    def list_registered_chains(self) -> list[str]:
        return list(CHAIN_REGISTRY.keys())
