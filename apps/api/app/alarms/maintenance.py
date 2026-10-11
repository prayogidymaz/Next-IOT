"""Background alarm maintenance (auto-clear resolved, stale validation)."""

from __future__ import annotations

import asyncio
import logging
from datetime import UTC, datetime, timedelta

from sqlalchemy import select

from app.alarms.service import clear_alarm
from app.database import async_session
from app.models.alarm import Alarm, AlarmStatus

logger = logging.getLogger(__name__)

RESOLVED_CLEAR_AFTER = timedelta(hours=24)
STALE_VALIDATION_AFTER = timedelta(minutes=30)


async def run_alarm_maintenance_once() -> None:
    now = datetime.now(UTC)
    async with async_session() as db:
        resolved_cutoff = now - RESOLVED_CLEAR_AFTER
        resolved_rows = list(
            await db.scalars(
                select(Alarm).where(
                    Alarm.status == AlarmStatus.RESOLVED,
                    Alarm.resolved_at.is_not(None),
                    Alarm.resolved_at <= resolved_cutoff,
                )
            )
        )
        for row in resolved_rows:
            await clear_alarm(db, row)

        stale_cutoff = now - STALE_VALIDATION_AFTER
        stale_rows = list(
            await db.scalars(
                select(Alarm).where(
                    Alarm.alarm_type == "validation_failed",
                    Alarm.status == AlarmStatus.ACTIVE,
                    Alarm.occurred_at <= stale_cutoff,
                )
            )
        )
        for row in stale_rows:
            await clear_alarm(db, row)
        await db.commit()


async def alarm_maintenance_loop(stop_event: asyncio.Event) -> None:
    logger.info("Alarm maintenance worker started")
    while not stop_event.is_set():
        try:
            await run_alarm_maintenance_once()
        except Exception:
            logger.exception("Alarm maintenance iteration failed")
        try:
            await asyncio.wait_for(stop_event.wait(), timeout=300.0)
        except TimeoutError:
            continue
    logger.info("Alarm maintenance worker stopped")
