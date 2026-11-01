"""Stepwise chain execution with Redis-backed state."""

from __future__ import annotations

import json
import uuid
from datetime import UTC, datetime
from enum import StrEnum

from sqlalchemy.ext.asyncio import AsyncSession

from app.agents.models import AgentChainExecution, ChainExecutionStatus
from app.agents.responder.chain_definitions import CHAIN_REGISTRY, ChainTemplate
from app.mesh.event_bus import mesh_tenant_fanout_channel
from app.types.json_types import JsonObject
from app.types.redis_client import RedisClient


class ChainControl(StrEnum):
    PAUSE = "pause"
    RESUME = "resume"
    CANCEL = "cancel"


class ChainExecutor:
    def __init__(self, db: AsyncSession, redis: RedisClient) -> None:
        self._db = db
        self._redis = redis

    def _redis_key(self, execution_id: uuid.UUID) -> str:
        return f"agent:chain:{execution_id}"

    async def _emit_progress(self, tenant_id: uuid.UUID, payload: JsonObject) -> None:
        channel = mesh_tenant_fanout_channel(str(tenant_id))
        await self._redis.publish(channel, json.dumps({"type": "agent_chain_progress", **payload}))

    async def start(
        self,
        chain_name: str,
        tenant_id: uuid.UUID,
        trigger_event_id: uuid.UUID | None,
        context: JsonObject,
    ) -> AgentChainExecution:
        template = CHAIN_REGISTRY.get(chain_name)
        if template is None:
            raise ValueError(f"Unknown chain: {chain_name}")

        row = AgentChainExecution(
            chain_id=chain_name,
            tenant_id=tenant_id,
            trigger_event_id=trigger_event_id,
            current_step=0,
            context_json=dict(context),
            status=ChainExecutionStatus.RUNNING,
            state=ChainExecutionStatus.RUNNING,
        )
        self._db.add(row)
        await self._db.flush()
        await self._persist_redis(row, template)
        await self._emit_progress(tenant_id, {"execution_id": str(row.id), "step": 0, "chain_id": chain_name})
        return row

    async def run_next_step(self, execution_id: uuid.UUID) -> AgentChainExecution:
        row = await self._db.get(AgentChainExecution, execution_id)
        if row is None:
            raise ValueError("Execution not found")
        if row.status in {ChainExecutionStatus.CANCELLED, ChainExecutionStatus.COMPLETED}:
            return row

        template = CHAIN_REGISTRY[row.chain_id]
        if row.current_step >= len(template.steps):
            row.status = ChainExecutionStatus.COMPLETED
            row.state = ChainExecutionStatus.COMPLETED
            row.completed_at = datetime.now(tz=UTC)
            await self._db.flush()
            return row

        step = template.steps[row.current_step]
        ctx = row.context_json if isinstance(row.context_json, dict) else {}
        ctx[f"last_step_{step.step_id}"] = {"handler": step.handler_key, "at": datetime.now(tz=UTC).isoformat()}
        row.context_json = ctx
        row.current_step += 1

        if row.current_step >= len(template.steps):
            row.status = ChainExecutionStatus.COMPLETED
            row.state = ChainExecutionStatus.COMPLETED
            row.completed_at = datetime.now(tz=UTC)

        await self._db.flush()
        await self._persist_redis(row, template)
        await self._emit_progress(
            row.tenant_id,
            {"execution_id": str(row.id), "step": row.current_step, "chain_id": row.chain_id},
        )
        return row

    async def control(self, execution_id: uuid.UUID, action: ChainControl) -> AgentChainExecution:
        row = await self._db.get(AgentChainExecution, execution_id)
        if row is None:
            raise ValueError("Execution not found")
        if action == ChainControl.PAUSE:
            row.status = ChainExecutionStatus.PAUSED
            row.state = ChainExecutionStatus.PAUSED
        elif action == ChainControl.RESUME:
            row.status = ChainExecutionStatus.RUNNING
            row.state = ChainExecutionStatus.RUNNING
        elif action == ChainControl.CANCEL:
            row.status = ChainExecutionStatus.CANCELLED
            row.state = ChainExecutionStatus.CANCELLED
            row.completed_at = datetime.now(tz=UTC)
        await self._db.flush()
        return row

    async def _persist_redis(self, row: AgentChainExecution, template: ChainTemplate) -> None:
        payload = {
            "execution_id": str(row.id),
            "chain_id": row.chain_id,
            "current_step": row.current_step,
            "total_steps": len(template.steps),
            "status": row.status,
        }
        await self._redis.set(self._redis_key(row.id), json.dumps(payload), ex=86_400)
