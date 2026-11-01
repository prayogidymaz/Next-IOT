"""Water usage aggregation."""

from __future__ import annotations

from decimal import Decimal

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.sustainability.models import WaterUsage


async def aggregate_water_by_plot(
    db: AsyncSession,
    tenant_id: object,
    *,
    plot_id: object | None = None,
) -> list[tuple[object | None, Decimal]]:
    stmt = (
        select(WaterUsage.plot_id, func.coalesce(func.sum(WaterUsage.liters_used), 0))
        .where(WaterUsage.tenant_id == tenant_id)
        .group_by(WaterUsage.plot_id)
    )
    if plot_id is not None:
        stmt = stmt.where(WaterUsage.plot_id == plot_id)
    rows = await db.execute(stmt)
    out: list[tuple[object | None, Decimal]] = []
    for pid, total in rows.all():
        out.append((pid, Decimal(str(total))))
    return out


def liters_from_valve_open_seconds(seconds: float, flow_lpm: float = 12.0) -> Decimal:
    liters = Decimal(str(seconds)) / Decimal("60") * Decimal(str(flow_lpm))
    return liters.quantize(Decimal("0.001"))
