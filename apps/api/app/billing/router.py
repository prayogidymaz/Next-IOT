"""Billing and payment webhooks."""

from __future__ import annotations

import uuid

from fastapi import APIRouter, HTTPException, Request, status
from fastapi.responses import PlainTextResponse, Response

from app.auth.dependencies import RequireOperator, RequireTenantAdmin
from app.billing import service as billing_service
from app.billing.cycle import mark_invoice_paid
from app.billing.providers import midtrans, xendit
from app.billing.schemas import (
    ChangePlanRequest,
    InvoiceResponse,
    PaymentMethodCreateRequest,
    SubscriptionPlanResponse,
    TenantSubscriptionResponse,
    UsageSummaryResponse,
)
from app.deps import DbSession, RedisDep

router = APIRouter(tags=["billing"])


@router.get("/api/v1/subscription-plans")
async def list_subscription_plans(db: DbSession) -> list[SubscriptionPlanResponse]:
    return await billing_service.list_public_plans(db)


@router.get("/api/v1/billing/subscription")
async def get_my_subscription(user: RequireOperator, db: DbSession) -> TenantSubscriptionResponse:
    return await billing_service.get_subscription_summary(db, user)


@router.get("/api/v1/billing/usage")
async def get_my_usage(user: RequireOperator, db: DbSession, redis: RedisDep) -> UsageSummaryResponse:
    return await billing_service.get_usage_summary(db, redis, user)


@router.get("/api/v1/billing/invoices")
async def list_my_invoices(user: RequireTenantAdmin, db: DbSession) -> list[InvoiceResponse]:
    return await billing_service.list_tenant_invoices(db, user)


@router.post("/api/v1/billing/change-plan")
async def change_my_plan(
    payload: ChangePlanRequest,
    user: RequireTenantAdmin,
    db: DbSession,
) -> TenantSubscriptionResponse:
    return await billing_service.upgrade_plan(db, user, payload.plan_code, payload.billing_cycle)


@router.post("/api/v1/billing/payment-methods", status_code=201)
async def create_payment_method(
    payload: PaymentMethodCreateRequest,
    user: RequireTenantAdmin,
    db: DbSession,
) -> dict[str, str]:
    pm_id = await billing_service.add_payment_method(
        db,
        user,
        provider=payload.provider,
        pm_type=payload.type,
        details=payload.details,
        is_default=payload.is_default,
    )
    return {"id": str(pm_id)}


@router.get("/api/v1/billing/invoices/{invoice_id}/pdf")
async def download_invoice_pdf(invoice_id: uuid.UUID, user: RequireTenantAdmin, db: DbSession) -> Response:
    from sqlalchemy import select

    from app.models.invoice import Invoice

    inv = await db.scalar(select(Invoice).where(Invoice.id == invoice_id, Invoice.tenant_id == user.tenant_id))
    if inv is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invoice not found")
    body = f"Invoice {inv.invoice_number}\nTotal IDR {inv.total_idr}\n"
    return PlainTextResponse(content=body, media_type="text/plain")


@router.post("/api/v1/billing/webhooks/midtrans")
async def midtrans_webhook(request: Request, db: DbSession) -> dict[str, str]:
    raw = await request.body()
    sig = request.headers.get("X-Midtrans-Signature")
    if not midtrans.verify_webhook_signature(raw, sig):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid signature")
    payload = midtrans.payload_dict(raw)
    invoice_id, reference = midtrans.parse_paid_invoice_id(payload)
    if invoice_id is None:
        return {"status": "ignored"}
    await mark_invoice_paid(db, invoice_id, provider="midtrans", reference=reference)
    return {"status": "ok"}


@router.post("/api/v1/billing/webhooks/xendit")
async def xendit_webhook(request: Request, db: DbSession) -> dict[str, str]:
    token = request.headers.get("x-callback-token")
    if not xendit.verify_callback_token(token):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid callback token")
    raw = await request.body()
    payload = xendit.payload_dict(raw)
    invoice_id, reference = xendit.parse_paid_invoice_id(payload)
    if invoice_id is None:
        return {"status": "ignored"}
    await mark_invoice_paid(db, invoice_id, provider="xendit", reference=reference)
    return {"status": "ok"}
