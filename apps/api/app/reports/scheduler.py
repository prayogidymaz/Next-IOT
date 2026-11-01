"""Report schedule runner (hourly tick — cron match TODO deep)."""

from __future__ import annotations

import asyncio
import logging

from sqlalchemy import select

from app.database import async_session
from app.reports.generator import generate_report
from app.reports.models import ReportSchedule, ReportTemplate

logger = logging.getLogger(__name__)


async def report_scheduler_loop(stop_event: asyncio.Event) -> None:
    while not stop_event.is_set():
        try:
            async with async_session() as db:
                schedules = await db.scalars(select(ReportSchedule).where(ReportSchedule.enabled.is_(True)))
                for sched in schedules.all():
                    template = await db.get(ReportTemplate, sched.template_id)
                    if template is None:
                        continue
                    # TODO: evaluate sched.cron_expression with croniter
                    await generate_report(db, template, sched.format)
        except Exception:
            logger.exception("report scheduler tick failed")
        try:
            await asyncio.wait_for(stop_event.wait(), timeout=3600.0)
        except asyncio.TimeoutError:
            continue
