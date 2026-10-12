"""Automatic irrigation decisions."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.agriculture.bmkg_weather import get_cached_forecast, irrigation_window_ok
from app.agriculture.models import AgriFarm, AgriIrrigationLog, AgriIrrigationValve, AgriPlot
from app.agriculture.notification_dispatcher import AgriNotificationDispatcher
from app.types.redis_client import RedisClient


def minutes_for_plot(area_ha: Decimal, flow_lpm: Decimal) -> int:
    if flow_lpm <= 0:
        return 15
    liters = float(area_ha) * 10000 * 2.0
    minutes = int(liters / float(flow_lpm))
    return max(5, min(120, minutes))


async def run_auto_irrigation_for_farm(
    db: AsyncSession,
    redis: RedisClient,
    farm_id: uuid.UUID,
    plot_moisture_pct: dict[uuid.UUID, float],
) -> list[uuid.UUID]:
    """Open valves when moisture below threshold and weather allows."""
    farm = await db.scalar(select(AgriFarm).where(AgriFarm.id == farm_id))
    if farm is None:
        return []
    forecast = await get_cached_forecast(
        redis,
        float(farm.location_lat or 0),
        float(farm.location_lng or 0),
    )
    if forecast.rain_next_hours(6):
        return []
    if not irrigation_window_ok(datetime.now(tz=UTC)):
        return []
    valves = await db.scalars(
        select(AgriIrrigationValve).where(
            AgriIrrigationValve.farm_id == farm_id,
            AgriIrrigationValve.auto_irrigation_enabled.is_(True),
        )
    )
    opened: list[uuid.UUID] = []
    for valve in valves.all():
        moisture = plot_moisture_pct.get(valve.plot_id)
        if moisture is None or moisture >= float(valve.moisture_threshold_pct):
            continue
        plot = await db.scalar(select(AgriPlot).where(AgriPlot.id == valve.plot_id))
        duration = minutes_for_plot(plot.area_hectares if plot else Decimal("1"), valve.flow_rate_lpm)
        valve.current_state = "open"
        valve.last_opened_at = datetime.now(tz=UTC)
        valve.total_opens_count += 1
        db.add(
            AgriIrrigationLog(
                farm_id=farm_id,
                plot_id=valve.plot_id,
                valve_id=valve.id,
                action="open",
                duration_minutes=duration,
                trigger="auto",
                detail={"moisture_pct": moisture},
            )
        )
        opened.append(valve.id)
    if opened:
        await db.commit()
        dispatcher = AgriNotificationDispatcher(db, redis)
        for valve_id in opened:
            await dispatcher.send_irrigation_notification("started", valve_id)
    return opened
