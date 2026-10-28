"""Background loop for ML anomaly detection (15-minute cadence)."""

from __future__ import annotations

import asyncio
import logging

from app.analytics.ml.service import run_ml_anomaly_tick
from app.config import settings
from app.database import async_session

logger = logging.getLogger(__name__)

_ML_ANOMALY_INTERVAL_SECONDS = 15 * 60


async def ml_anomaly_scheduler_loop(stop_event: asyncio.Event) -> None:
    while not stop_event.is_set():
        if settings.run_background_workers:
            try:
                async with async_session() as db:
                    count = await run_ml_anomaly_tick(db)
                    await db.commit()
                if count:
                    logger.info("ML anomaly tick inserted=%s", count)
            except Exception:
                logger.exception("ML anomaly scheduler tick failed")
        try:
            await asyncio.wait_for(stop_event.wait(), timeout=_ML_ANOMALY_INTERVAL_SECONDS)
        except TimeoutError:
            continue
