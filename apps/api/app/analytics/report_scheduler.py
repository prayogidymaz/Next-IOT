"""Background loop for scheduled analytics reports."""

from __future__ import annotations

import asyncio
import logging

from app.analytics.scheduled_reports import run_scheduled_reports_tick
from app.config import settings
from app.database import async_session

logger = logging.getLogger(__name__)


async def analytics_report_scheduler_loop(stop_event: asyncio.Event) -> None:
    while not stop_event.is_set():
        if settings.analytics_reports_scheduler_enabled:
            try:
                async with async_session() as db:
                    fired = await run_scheduled_reports_tick(db)
                    await db.commit()
                if fired:
                    logger.info("Analytics scheduled reports fired=%s", fired)
            except Exception:
                logger.exception("Analytics report scheduler tick failed")
        try:
            await asyncio.wait_for(stop_event.wait(), timeout=settings.analytics_reports_tick_seconds)
        except TimeoutError:
            continue
