"""Monthly marketplace payout scheduler."""

from __future__ import annotations

import asyncio
import logging
from datetime import UTC, datetime, timedelta

from app.database import async_session
from app.workflows.marketplace.payout_service import aggregate_monthly_payouts

logger = logging.getLogger(__name__)


async def marketplace_payout_scheduler_loop(stop_event: asyncio.Event) -> None:
    while not stop_event.is_set():
        now = datetime.now(tz=UTC)
        if now.day == 1 and now.hour == 0:
            prev = (now.replace(day=1) - timedelta(days=1)).strftime("%Y-%m")
            try:
                async with async_session() as db:
                    rows = await aggregate_monthly_payouts(db, prev)
                logger.info("Marketplace payout cron created %s rows for %s", len(rows), prev)
            except Exception:
                logger.exception("Marketplace payout cron failed")
        try:
            await asyncio.wait_for(stop_event.wait(), timeout=3600.0)
        except asyncio.TimeoutError:
            continue
