from datetime import UTC, datetime

from app.audit import export as audit_export
from app.audit import service as audit_service
from app.audit.schemas import AuditLogItem, AuditLogListResponse
from app.auth.dependencies import RequireAuditRead
from app.deps import get_db
from fastapi import APIRouter, Depends, Query
from fastapi.responses import Response
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(prefix="/api/v1/audit-logs", tags=["audit"])


@router.get("", response_model=AuditLogListResponse)
async def list_audit_logs(
    user: RequireAuditRead,
    db: AsyncSession = Depends(get_db),
    action: str | None = Query(default=None),
    actor: str | None = Query(default=None, description="Search actor email or resource target"),
    start_time: datetime | None = Query(default=None),
    end_time: datetime | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=50, ge=1, le=200),
):
    rows, total = await audit_service.list_audit_logs(
        db,
        user,
        action=action,
        actor_query=actor,
        start_time=start_time,
        end_time=end_time,
        page=page,
        page_size=page_size,
    )
    return AuditLogListResponse(
        items=[AuditLogItem.model_validate(r) for r in rows],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get("/export")
async def export_audit_logs_csv(
    user: RequireAuditRead,
    db: AsyncSession = Depends(get_db),
    action: str | None = Query(default=None),
    actor: str | None = Query(default=None),
    start_time: datetime | None = Query(default=None),
    end_time: datetime | None = Query(default=None),
):
    rows, _ = await audit_service.list_audit_logs(
        db,
        user,
        action=action,
        actor_query=actor,
        start_time=start_time,
        end_time=end_time,
        page=1,
        page_size=10_000,
    )
    csv_body = audit_export.render_audit_csv(rows)
    filename = f"audit_logs_{datetime.now(UTC).strftime('%Y%m%d_%H%M%S')}.csv"
    return Response(
        content=csv_body,
        media_type="text/csv",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
