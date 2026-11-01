"""Marketplace checkout (Midtrans-first, Stripe optional)."""

from __future__ import annotations

import hashlib
import os
import uuid

import httpx
from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.context import CurrentUser
from app.workflows.marketplace.models import MarketplaceTemplatePurchase, WorkflowTemplate


def _midtrans_enabled() -> bool:
    return bool(os.environ.get("MIDTRANS_SERVER_KEY", "").strip())


async def tenant_has_purchase(db: AsyncSession, template_id: uuid.UUID, tenant_id: uuid.UUID) -> bool:
    row = await db.scalar(
        select(MarketplaceTemplatePurchase).where(
            MarketplaceTemplatePurchase.template_id == template_id,
            MarketplaceTemplatePurchase.buyer_tenant_id == tenant_id,
            MarketplaceTemplatePurchase.status == "paid",
        )
    )
    return row is not None


async def create_checkout(
    db: AsyncSession,
    user: CurrentUser,
    template_id: uuid.UUID,
) -> dict[str, str | int]:
    template = await db.get(WorkflowTemplate, template_id)
    if template is None or not template.published:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Template not found")
    price = template.price_idr or 0
    if price <= 0:
        return {"provider": "free", "amount_idr": 0, "checkout_url": ""}
    if await tenant_has_purchase(db, template_id, user.tenant_id):
        return {"provider": "owned", "amount_idr": price, "checkout_url": ""}
    provider = "midtrans" if _midtrans_enabled() else "stub"
    payment_ref = f"NIOT-{uuid.uuid4().hex[:12]}"
    purchase = MarketplaceTemplatePurchase(
        template_id=template_id,
        buyer_tenant_id=user.tenant_id,
        amount_idr=price,
        payment_provider=provider,
        payment_ref=payment_ref,
        status="pending" if provider == "midtrans" else "paid",
    )
    db.add(purchase)
    await db.commit()
    checkout_url = ""
    if provider == "midtrans":
        checkout_url = await _midtrans_snap_redirect(price, payment_ref, user.email)
    return {"provider": provider, "amount_idr": price, "checkout_url": checkout_url, "payment_ref": payment_ref}


async def _midtrans_snap_redirect(amount_idr: int, order_id: str, customer_email: str) -> str:
    server_key = os.environ.get("MIDTRANS_SERVER_KEY", "").strip()
    if not server_key:
        return f"https://app.midtrans.com/snap/v2/vtweb/{order_id}"
    payload = {
        "transaction_details": {"order_id": order_id, "gross_amount": amount_idr},
        "customer_details": {"email": customer_email},
    }
    auth = httpx.BasicAuth(username=server_key, password="")
    async with httpx.AsyncClient(timeout=15.0) as client:
        resp = await client.post("https://app.midtrans.com/snap/v1/transactions", json=payload, auth=auth)
    if resp.status_code >= 400:
        return f"https://app.midtrans.com/snap/v2/vtweb/{order_id}"
    body = resp.json()
    token = body.get("token") if isinstance(body, dict) else None
    if isinstance(token, str) and token:
        return f"https://app.midtrans.com/snap/v2/vtweb/{token}"
    return f"https://app.midtrans.com/snap/v2/vtweb/{order_id}"


def verify_midtrans_signature(order_id: str, status_code: str, gross_amount: str, signature_key: str) -> bool:
    server_key = os.environ.get("MIDTRANS_SERVER_KEY", "").strip()
    if not server_key:
        return False
    raw = f"{order_id}{status_code}{gross_amount}{server_key}"
    expected = hashlib.sha512(raw.encode("utf-8")).hexdigest()
    return expected == signature_key


async def apply_midtrans_callback(db: AsyncSession, order_id: str, transaction_status: str, signature_key: str, gross_amount: str) -> None:
    if not verify_midtrans_signature(order_id, "200", gross_amount, signature_key):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid Midtrans signature")
    row = await db.scalar(
        select(MarketplaceTemplatePurchase).where(MarketplaceTemplatePurchase.payment_ref == order_id)
    )
    if row is None:
        return
    if transaction_status in {"capture", "settlement"}:
        row.status = "paid"
    elif transaction_status in {"deny", "cancel", "expire"}:
        row.status = "failed"
    await db.commit()


async def assert_download_allowed(db: AsyncSession, template: WorkflowTemplate, user: CurrentUser) -> None:
    if (template.price_idr or 0) <= 0:
        return
    if not await tenant_has_purchase(db, template.id, user.tenant_id):
        raise HTTPException(status_code=status.HTTP_402_PAYMENT_REQUIRED, detail="Purchase required before download")
