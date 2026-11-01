"""Multi-site enterprise API."""

from __future__ import annotations

import uuid
from typing import Annotated

from fastapi import APIRouter, Query

from app.auth.dependencies import RequireAuth
from app.deps import DbSession
from app.sites import service
from app.sites.schemas import PlotCreate, PlotView, SiteCreate, SiteMemberInvite, SiteReportView, SiteUpdate, SiteView

router = APIRouter(prefix="/api/v1/sites", tags=["sites"])

PeriodDaysQuery = Annotated[int, Query(ge=1, le=365)]


@router.get("", response_model=list[SiteView])
async def list_sites(user: RequireAuth, db: DbSession) -> list[SiteView]:
    rows = await service.list_accessible_sites(db, user)
    return [SiteView.model_validate(r) for r in rows]


@router.post("", response_model=SiteView, status_code=201)
async def create_site(user: RequireAuth, db: DbSession, payload: SiteCreate) -> SiteView:
    row = await service.create_site(db, user, payload)
    return SiteView.model_validate(row)


@router.get("/{site_id}", response_model=SiteView)
async def get_site(user: RequireAuth, db: DbSession, site_id: uuid.UUID) -> SiteView:
    row = await service.get_site(db, user, site_id)
    return SiteView.model_validate(row)


@router.patch("/{site_id}", response_model=SiteView)
async def patch_site(user: RequireAuth, db: DbSession, site_id: uuid.UUID, payload: SiteUpdate) -> SiteView:
    row = await service.update_site(db, user, site_id, payload)
    return SiteView.model_validate(row)


@router.get("/{site_id}/plots", response_model=list[PlotView])
async def get_site_plots(user: RequireAuth, db: DbSession, site_id: uuid.UUID) -> list[PlotView]:
    rows = await service.list_plots(db, user, site_id)
    return [PlotView.model_validate(r) for r in rows]


@router.post("/{site_id}/plots", response_model=PlotView, status_code=201)
async def create_site_plot(user: RequireAuth, db: DbSession, site_id: uuid.UUID, payload: PlotCreate) -> PlotView:
    row = await service.create_plot(db, user, site_id, payload)
    return PlotView.model_validate(row)


@router.get("/{site_id}/report", response_model=SiteReportView)
async def get_site_report(user: RequireAuth, db: DbSession, site_id: uuid.UUID, period: PeriodDaysQuery = 30) -> SiteReportView:
    return await service.consolidated_report(db, user, site_id, period)


@router.post("/{site_id}/members", status_code=201)
async def invite_site_member(user: RequireAuth, db: DbSession, site_id: uuid.UUID, payload: SiteMemberInvite) -> dict[str, str]:
    await service.add_site_member(db, user, site_id, payload)
    return {"status": "ok"}
