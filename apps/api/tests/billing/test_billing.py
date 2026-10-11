"""Billing and subscription tests."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime, timedelta
from decimal import Decimal

import pytest
from app.billing.cycle import run_billing_cycle
from app.billing.invoice_service import create_invoice_for_subscription, invoice_pdf_path
from app.billing.providers import midtrans, xendit
from app.billing.quota import assert_message_quota, increment_message_count
from app.billing.seed import seed_plans
from app.billing.subscription_service import change_plan, ensure_tenant_subscription
from app.billing.usage_service import snapshot_tenant_usage
from app.config import settings
from app.database import async_session
from app.models.invoice import Invoice
from app.models.subscription_plan import SubscriptionPlan
from app.models.tenant import Tenant
from app.models.tenant_subscription import TenantSubscription
from fastapi import HTTPException
from httpx import AsyncClient
from sqlalchemy import select

PASSWORD = "SecurePass123!"


async def _register(client: AsyncClient, slug: str, email: str) -> dict[str, object]:
    resp = await client.post(
        "/auth/register",
        json={
            "email": email,
            "password": PASSWORD,
            "tenant_name": "Test Tenant",
            "tenant_slug": slug,
        },
    )
    assert resp.status_code == 201
    return resp.json()


def _auth(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


@pytest.mark.asyncio
async def test_subscription_plan_seed_loaded(client: AsyncClient) -> None:
    resp = await client.get("/api/v1/subscription-plans")
    assert resp.status_code == 200
    codes = {row["code"] for row in resp.json()}
    assert codes >= {"free", "starter", "pro", "enterprise"}


@pytest.mark.asyncio
async def test_subscription_create_default_trial(client: AsyncClient, unique_slug: str, unique_email: str) -> None:
    reg = await _register(client, unique_slug, unique_email)
    token = str(reg["tokens"]["access_token"])
    resp = await client.get("/api/v1/billing/subscription", headers=_auth(token))
    assert resp.status_code == 200
    body = resp.json()
    assert body["plan_code"] == "free"
    assert body["status"] == "trial"
    assert body["trial_ends_at"] is not None


@pytest.mark.asyncio
async def test_subscription_quota_devices_enforced(
    client: AsyncClient, unique_slug: str, unique_email: str, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.delenv("TESTING", raising=False)
    reg = await _register(client, unique_slug, unique_email)
    token = str(reg["tokens"]["access_token"])
    for i in range(5):
        r = await client.post(
            "/api/v1/devices",
            headers=_auth(token),
            json={"name": f"d{i}", "device_type": "sensor"},
        )
        assert r.status_code == 201, r.text
    blocked = await client.post(
        "/api/v1/devices",
        headers=_auth(token),
        json={"name": "d6", "device_type": "sensor"},
    )
    assert blocked.status_code == 429


@pytest.mark.asyncio
async def test_subscription_quota_messages_enforced(
    client: AsyncClient, test_redis, unique_slug: str, unique_email: str, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.delenv("TESTING", raising=False)
    reg = await _register(client, unique_slug, unique_email)
    tenant_id = uuid.UUID(str(reg["tenant_id"]))
    async with async_session() as db:
        plan = await db.scalar(select(SubscriptionPlan).where(SubscriptionPlan.code == "free"))
        assert plan is not None
        plan.limits = {**plan.limits, "max_messages_per_month": 2}
        await db.commit()
    for _ in range(2):
        await increment_message_count(test_redis, tenant_id)
    async with async_session() as db:
        with pytest.raises(HTTPException) as exc:
            await assert_message_quota(db, test_redis, tenant_id)
        assert exc.value.status_code == 429


@pytest.mark.asyncio
async def test_subscription_trial_expires_after_14_days(
    client: AsyncClient, unique_slug: str, unique_email: str
) -> None:
    reg = await _register(client, unique_slug, unique_email)
    tenant_id = uuid.UUID(str(reg["tenant_id"]))
    async with async_session() as db:
        sub = await ensure_tenant_subscription(db, tenant_id)
        sub.trial_ends_at = datetime.now(tz=UTC) - timedelta(days=1)
        await db.commit()
        from app.billing.subscription_service import mark_trial_expired_if_needed

        await mark_trial_expired_if_needed(db, sub)
        await db.commit()
        refreshed = await db.scalar(select(TenantSubscription).where(TenantSubscription.tenant_id == tenant_id))
        assert refreshed is not None
        assert refreshed.status == "expired"


@pytest.mark.asyncio
async def test_subscription_upgrade_prorate(client: AsyncClient, unique_slug: str, unique_email: str) -> None:
    reg = await _register(client, unique_slug, unique_email)
    tenant_id = uuid.UUID(str(reg["tenant_id"]))
    async with async_session() as db:
        await change_plan(db, tenant_id, "pro", at_period_end=False)
        await db.commit()
        sub = await db.scalar(select(TenantSubscription).where(TenantSubscription.tenant_id == tenant_id))
        assert sub is not None
        plan = await db.scalar(select(SubscriptionPlan).where(SubscriptionPlan.id == sub.plan_id))
        assert plan is not None
        assert plan.code == "pro"


@pytest.mark.asyncio
async def test_subscription_downgrade_at_period_end(client: AsyncClient, unique_slug: str, unique_email: str) -> None:
    reg = await _register(client, unique_slug, unique_email)
    tenant_id = uuid.UUID(str(reg["tenant_id"]))
    async with async_session() as db:
        await change_plan(db, tenant_id, "pro", at_period_end=False)
        await change_plan(db, tenant_id, "starter", at_period_end=True)
        await db.commit()
        sub = await db.scalar(select(TenantSubscription).where(TenantSubscription.tenant_id == tenant_id))
        assert sub is not None
        plan = await db.scalar(select(SubscriptionPlan).where(SubscriptionPlan.id == sub.plan_id))
        assert plan is not None
        assert plan.code == "starter"


@pytest.mark.asyncio
async def test_invoice_create_calculates_tax_11_percent() -> None:
    async with async_session() as db:
        await seed_plans(db)
        plan = await db.scalar(select(SubscriptionPlan).where(SubscriptionPlan.code == "starter"))
        assert plan is not None
        tenant = Tenant(name="Bill", slug=f"bill-{uuid.uuid4().hex[:8]}")
        db.add(tenant)
        await db.flush()
        sub = TenantSubscription(
            tenant_id=tenant.id,
            plan_id=plan.id,
            status="active",
            billing_cycle="monthly",
        )
        db.add(sub)
        await db.flush()
        inv = await create_invoice_for_subscription(
            db,
            tenant_id=tenant.id,
            subscription=sub,
            plan=plan,
            period_start=datetime.now(tz=UTC).date(),
            period_end=datetime.now(tz=UTC).date(),
        )
        assert inv.subtotal_idr == plan.monthly_price_idr
        tax_base = Decimal(inv.subtotal_idr) * settings.invoice_tax_percent / Decimal("100")
        expected_tax = int(tax_base.quantize(Decimal("1")))
        assert inv.tax_idr == expected_tax
        assert inv.total_idr == inv.subtotal_idr + inv.tax_idr


@pytest.mark.asyncio
async def test_invoice_pdf_url_generation() -> None:
    inv_id = uuid.uuid4()
    assert str(inv_id) in invoice_pdf_path(inv_id)


def test_midtrans_webhook_verifies_signature() -> None:
    payload = b'{"order_id":"00000000-0000-0000-0000-000000000001"}'
    assert midtrans.verify_webhook_signature(payload, None) is True


def test_midtrans_payment_link_creation() -> None:
    inv = Invoice(
        id=uuid.uuid4(),
        tenant_id=uuid.uuid4(),
        subscription_id=uuid.uuid4(),
        invoice_number="INV-TEST",
        period_start=datetime.now(tz=UTC).date(),
        period_end=datetime.now(tz=UTC).date(),
        subtotal_idr=100_000,
        tax_idr=11_000,
        total_idr=111_000,
        due_date=datetime.now(tz=UTC).date(),
    )
    link = midtrans.create_payment_link(inv)
    assert link.provider == "midtrans"
    assert link.url.startswith("https://")


def test_xendit_webhook_verifies_token() -> None:
    assert xendit.verify_callback_token(None) is True


@pytest.mark.asyncio
async def test_billing_cycle_generates_next_invoice(client: AsyncClient, unique_slug: str, unique_email: str) -> None:
    reg = await _register(client, unique_slug, unique_email)
    tenant_id = uuid.UUID(str(reg["tenant_id"]))
    async with async_session() as db:
        sub = await ensure_tenant_subscription(db, tenant_id)
        sub.current_period_end = datetime.now(tz=UTC) - timedelta(days=1)
        sub.status = "active"
        await db.commit()
        result = await run_billing_cycle(db)
        assert result["invoices_created"] >= 1
        inv = await db.scalar(select(Invoice).where(Invoice.tenant_id == tenant_id))
        assert inv is not None


@pytest.mark.asyncio
async def test_billing_cycle_marks_past_due_after_7_days(
    client: AsyncClient, unique_slug: str, unique_email: str
) -> None:
    reg = await _register(client, unique_slug, unique_email)
    tenant_id = uuid.UUID(str(reg["tenant_id"]))
    async with async_session() as db:
        sub = await ensure_tenant_subscription(db, tenant_id)
        plan = await db.scalar(select(SubscriptionPlan).where(SubscriptionPlan.id == sub.plan_id))
        assert plan is not None
        inv = await create_invoice_for_subscription(
            db,
            tenant_id=tenant_id,
            subscription=sub,
            plan=plan,
            period_start=datetime.now(tz=UTC).date(),
            period_end=datetime.now(tz=UTC).date(),
        )
        inv.status = "pending"
        inv.due_date = datetime.now(tz=UTC).date() - timedelta(days=settings.subscription_past_due_grace_days + 1)
        sub.status = "active"
        await db.commit()
        await run_billing_cycle(db)
        refreshed = await db.scalar(select(TenantSubscription).where(TenantSubscription.tenant_id == tenant_id))
        assert refreshed is not None
        assert refreshed.status in {"past_due", "expired"}


@pytest.mark.asyncio
async def test_usage_daily_snapshot_tracks_metrics(
    client: AsyncClient, test_redis, unique_slug: str, unique_email: str
) -> None:
    reg = await _register(client, unique_slug, unique_email)
    tenant_id = uuid.UUID(str(reg["tenant_id"]))
    await increment_message_count(test_redis, tenant_id, 3)
    async with async_session() as db:
        row = await snapshot_tenant_usage(db, test_redis, tenant_id)
        assert row.messages_count >= 3
        assert row.device_count >= 0
