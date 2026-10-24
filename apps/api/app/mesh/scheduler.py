"""Cron scheduler for mesh workflows with schedule triggers."""

from __future__ import annotations

import asyncio
import logging
from datetime import UTC, datetime

from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.database import async_session
from app.mesh.workflow_executor import get_mesh_workflow_executor
from app.mesh.workflow_registry import reload_workflows, scheduled_workflows
from app.rules.trigger_match import cron_due
from app.types.json_types import as_json_str
from app.types.redis_client import RedisClient

logger = logging.getLogger(__name__)

_SCHEDULE_LAST_KEY = "mesh:schedule:last:{workflow_id}"


async def run_mesh_schedule_tick(db: AsyncSession, redis: RedisClient, now: datetime) -> tuple[int, int]:
    executor = get_mesh_workflow_executor()
    if executor is None:
        return 0, 0
    entries = scheduled_workflows()
    fired = 0
    for tenant_id, workflow_id, definition in entries:
        filt = definition.trigger.filter
        cron_expr = as_json_str(filt.schedule_cron if filt is not None else None)
        if cron_expr is None:
            continue
        last_raw = await redis.get(_SCHEDULE_LAST_KEY.format(workflow_id=str(workflow_id)))
        last_executed: datetime | None = None
        if isinstance(last_raw, str) and last_raw:
            try:
                last_executed = datetime.fromisoformat(last_raw)
            except ValueError:
                last_executed = None
        if not cron_due(cron_expr, now, last_executed_at=last_executed):
            continue
        await executor.execute(
            db,
            workflow_id=workflow_id,
            tenant_id=tenant_id,
            definition=definition,
            trigger_event=None,
            dry_run=False,
        )
        await redis.set(_SCHEDULE_LAST_KEY.format(workflow_id=str(workflow_id)), now.isoformat())
        fired += 1
    return len(entries), fired


async def mesh_schedule_loop(redis: RedisClient, stop_event: asyncio.Event) -> None:
    async with async_session() as db:
        await reload_workflows(db)
    while not stop_event.is_set():
        if settings.mesh_scheduler_enabled:
            try:
                async with async_session() as db:
                    checked, fired = await run_mesh_schedule_tick(db, redis, datetime.now(tz=UTC))
                    await db.commit()
                if fired:
                    logger.info("Mesh schedule tick checked=%s fired=%s", checked, fired)
            except Exception:
                logger.exception("Mesh schedule tick failed")
        try:
            await asyncio.wait_for(stop_event.wait(), timeout=settings.mesh_scheduler_tick_seconds)
        except TimeoutError:
            continue
