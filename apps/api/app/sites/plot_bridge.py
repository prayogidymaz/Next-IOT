"""Cross-reference enterprise plots and agriculture plots."""

from __future__ import annotations

import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.agriculture.models import AgriPlot
from app.sites.models import Plot


async def link_agri_plot(db: AsyncSession, agri_plot_id: uuid.UUID, enterprise_plot_id: uuid.UUID) -> AgriPlot:
    agri = await db.get(AgriPlot, agri_plot_id)
    ent = await db.get(Plot, enterprise_plot_id)
    if agri is None or ent is None:
        raise ValueError("plot not found")
    agri.enterprise_plot_id = enterprise_plot_id
    await db.commit()
    await db.refresh(agri)
    return agri
