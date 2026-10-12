"""Background jobs for agriculture vertical."""

from __future__ import annotations

import asyncio
import logging
from datetime import UTC, datetime

from sqlalchemy import select

from app.agriculture.disease_predictor import (
    DiseaseRisk,
    evaluate_coffee_berry_borer,
    evaluate_coffee_rust,
    evaluate_oil_palm_ganoderma,
    evaluate_rice_blast,
)
from app.agriculture.models import AgriDiseaseAlert, AgriFarm, AgriPlot
from app.database import async_session
from app.types.redis_client import RedisClient

logger = logging.getLogger(__name__)

SCAN_INTERVAL_SECONDS = 30 * 60


async def run_disease_scan_once() -> int:
    created = 0
    async with async_session() as db:
        farms = await db.scalars(select(AgriFarm))
        for farm in farms.all():
            plots = await db.scalars(select(AgriPlot).where(AgriPlot.farm_id == farm.id))
            for plot in plots.all():
                for risk in _evaluate_for_crop(farm.crop_type):
                    alert = AgriDiseaseAlert(
                        plot_id=plot.id,
                        disease_name=risk.disease_name,
                        risk_level=risk.risk_level,
                        predicted_at=datetime.now(tz=UTC),
                        factors=risk.factors,
                        action_recommended=risk.action_recommended,
                    )
                    db.add(alert)
                    created += 1
        if created:
            await db.commit()
    return created


def _evaluate_for_crop(crop_type: str) -> list[DiseaseRisk]:
    candidates: list[DiseaseRisk | None]
    if crop_type == "coffee":
        candidates = [
            evaluate_coffee_rust(88, 23, 7, 50),
            evaluate_coffee_berry_borer(25, 80, "fruiting"),
        ]
    elif crop_type == "rice":
        candidates = [evaluate_rice_blast(90, 22, True, True)]
    elif crop_type == "oil_palm":
        candidates = [evaluate_oil_palm_ganoderma(0.25, 5.0)]
    else:
        candidates = []
    return [r for r in candidates if r is not None]


async def agriculture_jobs_loop(redis: RedisClient, stop_event: asyncio.Event) -> None:
    while not stop_event.is_set():
        try:
            count = await run_disease_scan_once()
            if count:
                logger.info("agriculture disease scan created %s alerts", count)
        except Exception:
            logger.exception("agriculture disease scan failed")
        try:
            await asyncio.wait_for(stop_event.wait(), timeout=SCAN_INTERVAL_SECONDS)
        except TimeoutError:
            pass
