"""Background jobs for agriculture vertical."""

from __future__ import annotations

import asyncio
import logging
import uuid
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
from app.agriculture.notification_dispatcher import AgriNotificationDispatcher
from app.database import async_session
from app.types.redis_client import RedisClient

logger = logging.getLogger(__name__)

SCAN_INTERVAL_SECONDS = 30 * 60


async def run_disease_scan_once(redis: RedisClient) -> int:
    created = 0
    new_alert_ids: list[uuid.UUID] = []
    async with async_session() as db:
        farms = await db.scalars(select(AgriFarm))
        for farm in farms.all():
            plots = await db.scalars(select(AgriPlot).where(AgriPlot.farm_id == farm.id))
            for plot in plots.all():
                for risk in _evaluate_for_crop(farm.crop_type):
                    existing = await db.scalar(
                        select(AgriDiseaseAlert).where(
                            AgriDiseaseAlert.plot_id == plot.id,
                            AgriDiseaseAlert.disease_name == risk.disease_name,
                            AgriDiseaseAlert.resolved_at.is_(None),
                        )
                    )
                    if existing is not None:
                        continue
                    alert = AgriDiseaseAlert(
                        plot_id=plot.id,
                        disease_name=risk.disease_name,
                        risk_level=risk.risk_level,
                        predicted_at=datetime.now(tz=UTC),
                        factors=risk.factors,
                        action_recommended=risk.action_recommended,
                    )
                    db.add(alert)
                    await db.flush()
                    new_alert_ids.append(alert.id)
                    created += 1
        if created:
            await db.commit()
        dispatcher = AgriNotificationDispatcher(db, redis)
        for alert_id in new_alert_ids:
            alert_row = await db.scalar(select(AgriDiseaseAlert).where(AgriDiseaseAlert.id == alert_id))
            if alert_row is None:
                continue
            if alert_row.risk_level in ("high", "critical"):
                await dispatcher.send_disease_alert(alert_row.id)
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
    tick = 0
    while not stop_event.is_set():
        try:
            from app.scheduler.jobs import (
                battery_check_job,
                disease_prediction_job,
                harvest_reminder_job,
                weather_check_job,
            )

            await disease_prediction_job(redis)
        except Exception:
            logger.exception("agriculture disease job failed")
        if tick % 6 == 0:
            try:
                await weather_check_job(redis)
            except Exception:
                logger.exception("agriculture weather job failed")
        if tick % 12 == 0:
            try:
                await battery_check_job(redis)
            except Exception:
                logger.exception("agriculture battery job failed")
        hour_wib = (datetime.now(tz=UTC).hour + 7) % 24
        if hour_wib == 6 and tick % 2 == 0:
            try:
                await harvest_reminder_job(redis)
            except Exception:
                logger.exception("agriculture harvest job failed")
        tick += 1
        try:
            await asyncio.wait_for(stop_event.wait(), timeout=SCAN_INTERVAL_SECONDS)
        except TimeoutError:
            pass
