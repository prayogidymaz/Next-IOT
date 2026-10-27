"""Analytics export, energy, and scheduled reports API."""

from __future__ import annotations

import re
import uuid
from datetime import UTC, datetime, timedelta
from typing import Annotated

from fastapi import APIRouter, Query, Response, status
from fastapi.responses import StreamingResponse

from app.analytics.energy_service import calculate_energy, energy_summary_for_farm
from app.analytics.export_service import (
    export_alerts_csv,
    export_telemetry_csv,
    export_yield_csv,
    iter_telemetry_csv_chunks,
)
from app.analytics.scheduled_reports import (
    ScheduledReportCreate,
    ScheduledReportUpdate,
    ScheduledReportView,
    create_scheduled_report,
    delete_scheduled_report,
    list_scheduled_reports,
    update_scheduled_report,
)
from app.auth.dependencies import RequireAuth
from app.deps import DbSession

router = APIRouter(prefix="/api/v1/analytics", tags=["analytics"])

DeviceIdQuery = Annotated[uuid.UUID, Query()]
MetricQuery = Annotated[str, Query(min_length=1)]
StartQuery = Annotated[datetime, Query()]
EndQuery = Annotated[datetime, Query()]
FarmIdQuery = Annotated[uuid.UUID | None, Query()]
YearQuery = Annotated[int, Query(ge=2000, le=2100)]
PeriodQuery = Annotated[str, Query(description="e.g. 30d")]


def _parse_period(period: str) -> int:
    match = re.fullmatch(r"(\d+)d", period.strip())
    if match is None:
        return 30
    return int(match.group(1))


@router.get("/export/telemetry.csv")
async def get_export_telemetry_csv(
    user: RequireAuth,
    db: DbSession,
    device_id: DeviceIdQuery,
    metric: MetricQuery,
    start: StartQuery,
    end: EndQuery,
) -> Response:
    data = await export_telemetry_csv(db, user.tenant_id, device_id, metric, start, end)
    if len(data) > 65536:
        generator = iter_telemetry_csv_chunks(db, user.tenant_id, device_id, metric, start, end)
        return StreamingResponse(generator, media_type="text/csv")
    return Response(content=data, media_type="text/csv")


@router.get("/export/alerts.csv")
async def get_export_alerts_csv(
    user: RequireAuth,
    db: DbSession,
    start: StartQuery,
    end: EndQuery,
) -> Response:
    data = await export_alerts_csv(db, user.tenant_id, start, end)
    return Response(content=data, media_type="text/csv")


@router.get("/export/yield.csv")
async def get_export_yield_csv(
    user: RequireAuth,
    db: DbSession,
    farm_id: Annotated[uuid.UUID, Query()],
    year: YearQuery,
) -> Response:
    data = await export_yield_csv(db, user.tenant_id, farm_id, year)
    return Response(content=data, media_type="text/csv")


@router.post("/reports/schedule", response_model=ScheduledReportView, status_code=status.HTTP_201_CREATED)
async def post_scheduled_report(
    user: RequireAuth,
    db: DbSession,
    payload: ScheduledReportCreate,
) -> ScheduledReportView:
    row = await create_scheduled_report(db, user, payload)
    await db.commit()
    return row


@router.get("/reports/schedule", response_model=list[ScheduledReportView])
async def get_scheduled_reports(user: RequireAuth, db: DbSession) -> list[ScheduledReportView]:
    return await list_scheduled_reports(db, user)


@router.patch("/reports/schedule/{report_id}", response_model=ScheduledReportView)
async def patch_scheduled_report(
    user: RequireAuth,
    db: DbSession,
    report_id: uuid.UUID,
    payload: ScheduledReportUpdate,
) -> ScheduledReportView:
    row = await update_scheduled_report(db, user, report_id, payload)
    await db.commit()
    return row


@router.delete("/reports/schedule/{report_id}", status_code=status.HTTP_204_NO_CONTENT, response_class=Response)
async def remove_scheduled_report(user: RequireAuth, db: DbSession, report_id: uuid.UUID) -> Response:
    await delete_scheduled_report(db, user, report_id)
    await db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/energy")
async def get_energy(
    user: RequireAuth,
    db: DbSession,
    device_id: DeviceIdQuery,
    period: PeriodQuery = "30d",
) -> dict[str, object]:
    days = _parse_period(period)
    end = datetime.now(tz=UTC)
    start = end - timedelta(days=days)
    result = await calculate_energy(db, user.tenant_id, device_id, start, end)
    return result.model_dump(mode="json")


@router.get("/energy/summary")
async def get_energy_summary(
    user: RequireAuth,
    db: DbSession,
    farm_id: FarmIdQuery = None,
    period: PeriodQuery = "30d",
) -> dict[str, object]:
    days = _parse_period(period)
    result = await energy_summary_for_farm(db, user.tenant_id, farm_id, days)
    return result.model_dump(mode="json")
