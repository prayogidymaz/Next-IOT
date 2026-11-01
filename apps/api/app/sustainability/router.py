"""Sustainability dashboard API."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Annotated

from fastapi import APIRouter, HTTPException, Query, Response, status
from sqlalchemy import select

from app.auth.dependencies import RequireAuth
from app.deps import DbSession
from app.sustainability import esg_generator
from app.sustainability.models import CarbonEntry, EsgScorecard, WaterUsage
from app.sustainability.schemas import CarbonSeriesPoint, EsgScorecardView, WaterSeriesPoint

router = APIRouter(prefix="/api/v1/sustainability", tags=["sustainability"])

FromQuery = Annotated[datetime | None, Query(alias="from")]
ToQuery = Annotated[datetime | None, Query(alias="to")]
MonthQuery = Annotated[str, Query(pattern=r"^\d{4}-\d{2}$")]


@router.get("/carbon", response_model=list[CarbonSeriesPoint])
async def list_carbon(
    user: RequireAuth,
    db: DbSession,
    from_: FromQuery = None,
    to: ToQuery = None,
) -> list[CarbonSeriesPoint]:
    stmt = select(CarbonEntry).where(CarbonEntry.tenant_id == user.tenant_id)
    if from_ is not None:
        stmt = stmt.where(CarbonEntry.recorded_at >= from_)
    if to is not None:
        stmt = stmt.where(CarbonEntry.recorded_at <= to)
    stmt = stmt.order_by(CarbonEntry.recorded_at.desc()).limit(500)
    rows = await db.scalars(stmt)
    return [
        CarbonSeriesPoint(recorded_at=r.recorded_at, co2_equivalent_kg=r.co2_equivalent_kg, source_type=r.source_type)
        for r in rows.all()
    ]


@router.get("/water", response_model=list[WaterSeriesPoint])
async def list_water(user: RequireAuth, db: DbSession) -> list[WaterSeriesPoint]:
    rows = await db.scalars(
        select(WaterUsage).where(WaterUsage.tenant_id == user.tenant_id).order_by(WaterUsage.recorded_at.desc()).limit(500)
    )
    return [
        WaterSeriesPoint(
            plot_id=r.plot_id,
            liters_used=r.liters_used,
            source=r.source,
            recorded_at=r.recorded_at,
        )
        for r in rows.all()
    ]


@router.get("/esg/current", response_model=EsgScorecardView | None)
async def current_esg(user: RequireAuth, db: DbSession) -> EsgScorecardView | None:
    row = await db.scalar(
        select(EsgScorecard)
        .where(EsgScorecard.tenant_id == user.tenant_id)
        .order_by(EsgScorecard.generated_at.desc())
        .limit(1)
    )
    if row is None:
        return None
    return EsgScorecardView.model_validate(row)


@router.post("/esg/generate", response_model=EsgScorecardView, status_code=201)
async def generate_esg(user: RequireAuth, db: DbSession, month: MonthQuery) -> EsgScorecardView:
    row = await esg_generator.generate_scorecard(db, user.tenant_id, month)
    return EsgScorecardView.model_validate(row)


@router.get("/esg/{scorecard_id}/pdf")
async def esg_pdf(user: RequireAuth, db: DbSession, scorecard_id: uuid.UUID) -> Response:
    row = await db.get(EsgScorecard, scorecard_id)
    if row is None or row.tenant_id != user.tenant_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Scorecard not found")
    from app.sustainability.pdf_generator import render_esg_pdf, store_pdf_local

    carbon_rows = await db.scalars(
        select(CarbonEntry).where(CarbonEntry.tenant_id == user.tenant_id).order_by(CarbonEntry.recorded_at.desc()).limit(12)
    )
    water_rows = await db.scalars(
        select(WaterUsage).where(WaterUsage.tenant_id == user.tenant_id).order_by(WaterUsage.recorded_at.desc()).limit(10)
    )
    carbon_pts = [(r.recorded_at.date().isoformat(), float(r.co2_equivalent_kg)) for r in carbon_rows.all()]
    water_pts = [(str(r.plot_id or "site"), float(r.liters_used)) for r in water_rows.all()]
    pdf_bytes = render_esg_pdf(row, carbon_pts, water_pts)
    store_pdf_local(row.id, pdf_bytes)
    return Response(content=pdf_bytes, media_type="application/pdf")
