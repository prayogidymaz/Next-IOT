"""Site and plot business logic."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime, timedelta
from decimal import Decimal

from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.context import CurrentUser
from app.models.telemetry_reading import TelemetryReading
from app.sites.models import Plot, Site, SiteMember
from app.sites.schemas import PlotCreate, SiteCreate, SiteMemberInvite, SiteReportView, SiteUpdate


async def _ensure_site_access(db: AsyncSession, user: CurrentUser, site_id: uuid.UUID) -> Site:
    site = await db.get(Site, site_id)
    if site is None or site.tenant_id != user.tenant_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Site not found")
    member = await db.scalar(
        select(SiteMember).where(SiteMember.site_id == site_id, SiteMember.user_id == user.user_id)
    )
    if member is None and user.role not in {"tenant_admin", "super_admin"}:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not a site member")
    return site


async def get_site(db: AsyncSession, user: CurrentUser, site_id: uuid.UUID) -> Site:
    return await _ensure_site_access(db, user, site_id)


async def list_accessible_sites(db: AsyncSession, user: CurrentUser) -> list[Site]:
    if user.role in {"tenant_admin", "super_admin"}:
        rows = await db.scalars(select(Site).where(Site.tenant_id == user.tenant_id, Site.is_active.is_(True)))
        return list(rows.all())
    stmt = (
        select(Site)
        .join(SiteMember, SiteMember.site_id == Site.id)
        .where(SiteMember.user_id == user.user_id, Site.is_active.is_(True))
    )
    rows = await db.scalars(stmt)
    return list(rows.all())


async def create_site(db: AsyncSession, user: CurrentUser, payload: SiteCreate) -> Site:
    row = Site(
        tenant_id=user.tenant_id,
        name=payload.name,
        slug=payload.slug,
        parent_site_id=payload.parent_site_id,
        location_json=payload.location_json,
        timezone=payload.timezone,
    )
    db.add(row)
    await db.flush()
    db.add(SiteMember(site_id=row.id, user_id=user.user_id, role="owner"))
    await db.commit()
    await db.refresh(row)
    return row


async def update_site(db: AsyncSession, user: CurrentUser, site_id: uuid.UUID, payload: SiteUpdate) -> Site:
    site = await _ensure_site_access(db, user, site_id)
    if payload.name is not None:
        site.name = payload.name
    if payload.location_json is not None:
        site.location_json = payload.location_json
    if payload.timezone is not None:
        site.timezone = payload.timezone
    if payload.is_active is not None:
        site.is_active = payload.is_active
    await db.commit()
    await db.refresh(site)
    return site


async def list_plots(db: AsyncSession, user: CurrentUser, site_id: uuid.UUID) -> list[Plot]:
    await _ensure_site_access(db, user, site_id)
    rows = await db.scalars(select(Plot).where(Plot.site_id == site_id, Plot.is_active.is_(True)))
    return list(rows.all())


async def create_plot(db: AsyncSession, user: CurrentUser, site_id: uuid.UUID, payload: PlotCreate) -> Plot:
    await _ensure_site_access(db, user, site_id)
    row = Plot(
        site_id=site_id,
        name=payload.name,
        crop_type=payload.crop_type,
        area_hectares=payload.area_hectares,
        soil_type=payload.soil_type,
        planting_date=payload.planting_date,
        expected_harvest_date=payload.expected_harvest_date,
        metadata_json=payload.metadata_json,
    )
    db.add(row)
    await db.commit()
    await db.refresh(row)
    return row


async def add_site_member(db: AsyncSession, user: CurrentUser, site_id: uuid.UUID, payload: SiteMemberInvite) -> SiteMember:
    await _ensure_site_access(db, user, site_id)
    existing = await db.scalar(
        select(SiteMember).where(SiteMember.site_id == site_id, SiteMember.user_id == payload.user_id)
    )
    if existing is not None:
        existing.role = payload.role
        await db.commit()
        return existing
    row = SiteMember(site_id=site_id, user_id=payload.user_id, role=payload.role)
    db.add(row)
    await db.commit()
    return row


async def consolidated_report(db: AsyncSession, user: CurrentUser, site_id: uuid.UUID, period_days: int) -> SiteReportView:
    site = await _ensure_site_access(db, user, site_id)
    total_area = await db.scalar(
        select(func.coalesce(func.sum(Plot.area_hectares), 0)).where(Plot.site_id == site_id, Plot.is_active.is_(True))
    )
    plot_count = await db.scalar(select(func.count()).select_from(Plot).where(Plot.site_id == site_id, Plot.is_active.is_(True)))
    active = int(plot_count or 0)
    area_f = float(total_area or Decimal("0"))
    cutoff = datetime.now(tz=UTC) - timedelta(days=period_days)
    readings = await db.scalars(
        select(TelemetryReading).where(TelemetryReading.tenant_id == user.tenant_id, TelemetryReading.recorded_at >= cutoff).limit(2000)
    )
    metric_sums: dict[str, float] = {}
    metric_counts: dict[str, int] = {}
    for row in readings.all():
        metrics = row.metrics if isinstance(row.metrics, dict) else {}
        for key, val in metrics.items():
            if not isinstance(key, str):
                continue
            if isinstance(val, (int, float)):
                metric_sums[key] = metric_sums.get(key, 0.0) + float(val)
                metric_counts[key] = metric_counts.get(key, 0) + 1
    telemetry_metrics = {k: round(metric_sums[k] / metric_counts[k], 3) for k in metric_sums if metric_counts.get(k)}
    return SiteReportView(
        site_id=site.id,
        period_days=period_days,
        plot_count=active,
        total_area_hectares=area_f,
        active_plots=active,
        telemetry_metrics=telemetry_metrics,
    )
