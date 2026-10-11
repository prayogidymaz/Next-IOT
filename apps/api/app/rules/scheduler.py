"""Background scheduler for cron-based rules."""

from __future__ import annotations

import asyncio
import logging
from datetime import UTC, datetime

from app.database import async_session
from app.rules.executor import get_rule_executor

logger = logging.getLogger(__name__)


async def rule_schedule_loop(stop_event: asyncio.Event) -> None:
    while not stop_event.is_set():
        executor = get_rule_executor()
        if executor is not None:
            try:
                async with async_session() as db:
                    checked, fired = await executor.run_schedule_tick(db, datetime.now(UTC))
                    await db.commit()
                logger.info("Schedule scan: %s schedule rules checked, %s fired", checked, fired)
            except Exception:
                logger.exception("Rule schedule tick failed")
        try:
            await asyncio.wait_for(stop_event.wait(), timeout=60.0)
        except TimeoutError:
            continue
