"""Hourly carbon ingest from telemetry metrics."""

from __future__ import annotations

import asyncio
import logging
import uuid
from datetime import UTC, datetime, timedelta
from decimal import Decimal

from sqlalchemy import select

from app.database import async_session
from app.models.telemetry_reading import TelemetryReading
from app.sustainability.carbon_calculator import co2_from_source
from app.sustainability.models import CarbonEntry

logger = logging.getLogger(__name__)


async def ingest_telemetry_carbon_once() -> None:
    since = datetime.now(tz=UTC) - timedelta(hours=1)
    async with async_session() as db:
        rows = await db.scalars(select(TelemetryReading).where(TelemetryReading.recorded_at >= since).limit(500))
        for row in rows.all():
            metrics = row.metrics if isinstance(row.metrics, dict) else {}
            runtime = metrics.get("actuator_runtime_minutes")
            power_kw = metrics.get("pump_power_kw", metrics.get("power_kw"))
            if isinstance(runtime, (int, float)) and isinstance(power_kw, (int, float)):
                kwh = Decimal(str(runtime)) / Decimal("60") * Decimal(str(power_kw))
                co2 = co2_from_source("electricity", kwh)
                db.add(
                    CarbonEntry(
                        tenant_id=row.tenant_id,
                        site_id=None,
                        source_type="electricity",
                        amount=kwh,
                        co2_equivalent_kg=co2,
                        auto_calculated=True,
                    )
                )
        await db.commit()
    logger.info("Carbon ingest completed")


async def carbon_ingest_loop(stop_event: asyncio.Event) -> None:
    while not stop_event.is_set():
        try:
            await ingest_telemetry_carbon_once()
        except Exception:
            logger.exception("carbon ingest failed")
        try:
            await asyncio.wait_for(stop_event.wait(), timeout=3600.0)
        except asyncio.TimeoutError:
            continue
