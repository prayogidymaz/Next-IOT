"""Marketplace HTTP routes."""

from __future__ import annotations

import uuid

from fastapi import APIRouter, Query, Response, status

from app.auth.dependencies import RequireAuth, RequireSuperAdmin
from app.deps import DbSession
from app.mesh.workflow_service import _to_view
from app.mesh.workflow_schema import MeshWorkflowRecordView
from sqlalchemy import func, select

from app.workflows.marketplace.models import MarketplacePayout, MarketplaceSeller
from app.workflows.marketplace.payments import apply_midtrans_callback, create_checkout
from app.workflows.marketplace.payout_service import mark_payout_paid
from app.workflows.marketplace.payout_service import ensure_seller
from app.workflows.marketplace.schemas import (
    CheckoutResponse,
    DownloadTemplateBody,
    PayoutView,
    PublishTemplateBody,
    RateTemplateBody,
    SellerDashboardView,
    WorkflowTemplateView,
)
from app.workflows.marketplace.service import MarketplaceService, _template_view

router = APIRouter(prefix="/api/v1/marketplace", tags=["workflow-marketplace"])


@router.get("/templates", response_model=list[WorkflowTemplateView])
async def list_templates(
    db: DbSession,
    category: str | None = None,
    locale: str | None = Query(default=None),
    sort: str = Query(default="downloads", alias="sort"),
    limit: int = Query(default=20, ge=1, le=100),
    search: str | None = Query(default=None, max_length=120),
) -> list[WorkflowTemplateView]:
    service = MarketplaceService(db)
    if search and search.strip():
        rows_raw = await service.search(search, {"category": category or "", "locale": locale or ""})
        return [_template_view(row) for row in rows_raw[:limit]]
    rows = await service.list_templates(category, locale, sort, limit)
    return [_template_view(row, author_name) for row, author_name in rows]


@router.get("/templates/{template_id}", response_model=WorkflowTemplateView)
async def get_template(db: DbSession, template_id: uuid.UUID) -> WorkflowTemplateView:
    service = MarketplaceService(db)
    row, author_name = await service.get(template_id)
    return _template_view(row, author_name)


@router.post("/publish", response_model=WorkflowTemplateView, status_code=201)
async def publish_template(
    user: RequireAuth,
    db: DbSession,
    body: PublishTemplateBody,
) -> WorkflowTemplateView:
    service = MarketplaceService(db)
    metadata: dict[str, object] = {
        "name": body.name,
        "description": body.description,
        "category": body.category,
        "tags": body.tags,
        "locale": body.locale,
    }
    row = await service.publish(body.workflow_id, metadata, user)
    return _template_view(row)


@router.delete("/templates/{template_id}", status_code=status.HTTP_204_NO_CONTENT, response_class=Response)
async def unpublish_template(
    user: RequireAuth,
    db: DbSession,
    template_id: uuid.UUID,
) -> Response:
    service = MarketplaceService(db)
    await service.unpublish(template_id, user)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post("/templates/{template_id}/download", response_model=MeshWorkflowRecordView)
async def download_template(
    user: RequireAuth,
    db: DbSession,
    template_id: uuid.UUID,
    body: DownloadTemplateBody,
) -> MeshWorkflowRecordView:
    service = MarketplaceService(db)
    mesh = await service.download(template_id, user, body.target_tenant_id)
    return _to_view(mesh)


@router.post("/templates/{template_id}/checkout", response_model=CheckoutResponse)
async def checkout_template(user: RequireAuth, db: DbSession, template_id: uuid.UUID) -> CheckoutResponse:
    payload = await create_checkout(db, user, template_id)
    return CheckoutResponse(
        provider=str(payload["provider"]),
        amount_idr=int(payload["amount_idr"]),
        checkout_url=str(payload.get("checkout_url") or ""),
        payment_ref=str(payload["payment_ref"]) if payload.get("payment_ref") else None,
    )


@router.get("/seller/me")
async def seller_me(user: RequireAuth, db: DbSession) -> dict[str, bool]:
    row = await db.get(MarketplaceSeller, user.user_id)
    return {"is_seller": row is not None}


@router.post("/payments/midtrans/callback")
async def midtrans_callback(
    db: DbSession,
    order_id: str = Query(),
    transaction_status: str = Query(),
    signature_key: str = Query(),
    gross_amount: str = Query(),
) -> dict[str, str]:
    await apply_midtrans_callback(db, order_id, transaction_status, signature_key, gross_amount)
    return {"status": "ok"}


@router.post("/payouts/{payout_id}/trigger", response_model=PayoutView)
async def trigger_payout(payout_id: uuid.UUID, user: RequireSuperAdmin, db: DbSession) -> PayoutView:
    row = await mark_payout_paid(db, payout_id, f"manual-{uuid.uuid4().hex[:8]}")
    return PayoutView.model_validate(row)


@router.get("/seller/dashboard", response_model=SellerDashboardView)
async def seller_dashboard(user: RequireAuth, db: DbSession) -> SellerDashboardView:
    seller = await ensure_seller(db, user.user_id, user.tenant_id)
    pending = await db.scalar(
        select(func.coalesce(func.sum(MarketplacePayout.commission_idr), 0)).where(
            MarketplacePayout.seller_user_id == user.user_id,
            MarketplacePayout.status == "pending",
        )
    )
    return SellerDashboardView(
        tier=seller.tier,
        lifetime_sales_idr=seller.lifetime_sales_idr,
        commission_rate_percent=float(seller.commission_rate_percent),
        verified_badge=seller.verified_badge,
        pending_payout_idr=int(pending or 0),
    )


@router.get("/seller/payouts", response_model=list[PayoutView])
async def seller_payouts(user: RequireAuth, db: DbSession) -> list[PayoutView]:
    await ensure_seller(db, user.user_id, user.tenant_id)
    rows = await db.scalars(
        select(MarketplacePayout)
        .where(MarketplacePayout.seller_user_id == user.user_id)
        .order_by(MarketplacePayout.period_month.desc())
    )
    return [PayoutView.model_validate(r) for r in rows.all()]


@router.post("/templates/{template_id}/rate", status_code=204, response_class=Response)
async def rate_template(
    user: RequireAuth,
    db: DbSession,
    template_id: uuid.UUID,
    body: RateTemplateBody,
) -> Response:
    service = MarketplaceService(db)
    await service.rate(template_id, user, body.rating, body.review)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
