"""Super admin console API."""

from __future__ import annotations

import uuid

from fastapi import APIRouter, Query, Response
from sqlalchemy import select

from app.auth.dependencies import RequireSuperAdmin
from app.billing.cycle import run_billing_cycle
from app.billing.schemas import InvoiceResponse
from app.deps import DbSession, RedisDep
from app.models.invoice import Invoice
from app.super_admin import service
from app.super_admin.schemas import (
    ChangePlanAdminRequest,
    ExtendTrialRequest,
    ImpersonateResponse,
    PlatformStatsResponse,
    RevenueResponse,
    SystemHealthResponse,
    TenantAdminItem,
)

router = APIRouter(prefix="/api/v1/super-admin", tags=["super-admin"])


@router.get("/stats", response_model=PlatformStatsResponse)
async def get_platform_stats(user: RequireSuperAdmin, db: DbSession) -> PlatformStatsResponse:
    return await service.platform_stats(db)


@router.get("/tenants", response_model=list[TenantAdminItem])
async def list_tenants(
    user: RequireSuperAdmin,
    db: DbSession,
    status: str | None = Query(default=None),
    plan: str | None = Query(default=None),
) -> list[TenantAdminItem]:
    return await service.list_tenants_admin(db, status_filter=status, plan_code=plan)


@router.post("/tenants/{tenant_id}/suspend", status_code=204, response_class=Response)
async def suspend_tenant(tenant_id: uuid.UUID, user: RequireSuperAdmin, db: DbSession) -> Response:
    await service.suspend_tenant(db, user, tenant_id)
    return Response(status_code=204)


@router.post("/tenants/{tenant_id}/unsuspend", status_code=204, response_class=Response)
async def unsuspend_tenant(tenant_id: uuid.UUID, user: RequireSuperAdmin, db: DbSession) -> Response:
    await service.unsuspend_tenant(db, user, tenant_id)
    return Response(status_code=204)


@router.post("/tenants/{tenant_id}/extend-trial", status_code=204, response_class=Response)
async def extend_trial(
    tenant_id: uuid.UUID,
    payload: ExtendTrialRequest,
    user: RequireSuperAdmin,
    db: DbSession,
) -> Response:
    await service.extend_trial_admin(db, user, tenant_id, payload.days)
    return Response(status_code=204)


@router.post("/tenants/{tenant_id}/change-plan", status_code=204, response_class=Response)
async def change_plan(
    tenant_id: uuid.UUID,
    payload: ChangePlanAdminRequest,
    user: RequireSuperAdmin,
    db: DbSession,
) -> Response:
    await service.change_plan_admin(db, user, tenant_id, payload.plan_code, prorate=payload.prorate)
    return Response(status_code=204)


@router.post("/tenants/{tenant_id}/impersonate", response_model=ImpersonateResponse)
async def impersonate(tenant_id: uuid.UUID, user: RequireSuperAdmin, db: DbSession) -> ImpersonateResponse:
    token = await service.impersonate_tenant(db, user, tenant_id)
    return ImpersonateResponse(access_token=token, tenant_id=tenant_id)


@router.get("/invoices", response_model=list[InvoiceResponse])
async def list_invoices(
    user: RequireSuperAdmin,
    db: DbSession,
    status: str | None = Query(default=None),
) -> list[InvoiceResponse]:
    query = select(Invoice).order_by(Invoice.created_at.desc())
    if status:
        query = query.where(Invoice.status == status)
    rows = await db.scalars(query)
    return [InvoiceResponse.model_validate(row) for row in rows.all()]


@router.get("/revenue", response_model=RevenueResponse)
async def get_revenue(user: RequireSuperAdmin, db: DbSession) -> RevenueResponse:
    return await service.revenue_report(db)


@router.get("/system-health", response_model=SystemHealthResponse)
async def get_system_health(user: RequireSuperAdmin, db: DbSession, redis: RedisDep) -> SystemHealthResponse:
    return await service.system_health(db, redis)


@router.post("/billing-cycle/run")
async def run_billing_cycle_manual(user: RequireSuperAdmin, db: DbSession) -> dict[str, int]:
    return await run_billing_cycle(db)
