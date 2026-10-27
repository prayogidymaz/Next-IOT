"""Analytics advanced tests."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime, timedelta

import pytest
from app.analytics.energy_service import calculate_energy, cost_estimate
from app.database import async_session
from app.models.device import Device, DeviceStatus
from app.models.telemetry_reading import TelemetryReading
from app.models.tenant import Tenant
from httpx import AsyncClient

PASSWORD = "SecurePass123!"


@pytest.mark.asyncio
async def test_telemetry_csv_export_format(client: AsyncClient, unique_slug: str, unique_email: str) -> None:
    reg = await client.post(
        "/auth/register",
        json={"tenant_name": "CSV", "tenant_slug": unique_slug, "email": unique_email, "password": PASSWORD},
    )
    token = reg.json()["tokens"]["access_token"]
    tenant_id = uuid.UUID(reg.json()["tenant_id"])
    async with async_session() as db:
        device = Device(
            tenant_id=tenant_id,
            name="Power Meter",
            device_type="meter",
            status=DeviceStatus.ONLINE,
        )
        db.add(device)
        await db.flush()
        now = datetime.now(tz=UTC)
        db.add(
            TelemetryReading(
                tenant_id=tenant_id,
                device_id=device.id,
                recorded_at=now - timedelta(hours=1),
                metrics={"power_w": 1000},
            )
        )
        db.add(
            TelemetryReading(
                tenant_id=tenant_id,
                device_id=device.id,
                recorded_at=now,
                metrics={"power_w": 2000},
            )
        )
        await db.commit()
        device_id = device.id

    start = (datetime.now(tz=UTC) - timedelta(days=1)).isoformat()
    end = datetime.now(tz=UTC).isoformat()
    resp = await client.get(
        "/api/v1/analytics/export/telemetry.csv",
        headers={"Authorization": f"Bearer {token}"},
        params={"device_id": str(device_id), "metric": "power_w", "start": start, "end": end},
    )
    assert resp.status_code == 200
    text = resp.text
    assert "recorded_at,device_id,metric,value" in text
    assert "power_w" in text


@pytest.mark.asyncio
async def test_scheduled_report_crud(client: AsyncClient, unique_slug: str, unique_email: str) -> None:
    reg = await client.post(
        "/auth/register",
        json={"tenant_name": "Reports", "tenant_slug": unique_slug, "email": unique_email, "password": PASSWORD},
    )
    token = reg.json()["tokens"]["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    create = await client.post(
        "/api/v1/analytics/reports/schedule",
        headers=headers,
        json={
            "name": "Weekly yield",
            "report_type": "yield",
            "schedule_cron": "0 7 * * 1",
            "recipients": ["owner@example.com"],
            "filter_json": {"farm_id": str(uuid.uuid4())},
        },
    )
    assert create.status_code == 201
    report_id = create.json()["id"]
    listed = await client.get("/api/v1/analytics/reports/schedule", headers=headers)
    assert any(row["id"] == report_id for row in listed.json())


@pytest.mark.asyncio
async def test_energy_calculation() -> None:
    async with async_session() as db:
        tenant = Tenant(name="Energy", slug=f"energy-{uuid.uuid4().hex[:8]}")
        db.add(tenant)
        await db.flush()
        device = Device(
            tenant_id=tenant.id,
            name="Pump",
            device_type="pump",
            status=DeviceStatus.ONLINE,
        )
        db.add(device)
        await db.flush()
        start = datetime(2026, 1, 1, tzinfo=UTC)
        mid = datetime(2026, 1, 1, 1, 0, tzinfo=UTC)
        end = datetime(2026, 1, 1, 2, 0, tzinfo=UTC)
        db.add(
            TelemetryReading(
                tenant_id=tenant.id,
                device_id=device.id,
                recorded_at=start,
                metrics={"power_w": 1000},
            )
        )
        db.add(
            TelemetryReading(
                tenant_id=tenant.id,
                device_id=device.id,
                recorded_at=mid,
                metrics={"power_w": 1000},
            )
        )
        db.add(
            TelemetryReading(
                tenant_id=tenant.id,
                device_id=device.id,
                recorded_at=end,
                metrics={"power_w": 1000},
            )
        )
        await db.commit()
        result = await calculate_energy(db, tenant.id, device.id, start, end)
        assert result.kwh_total == pytest.approx(2.0, rel=0.01)
        assert cost_estimate(result.kwh_total) == pytest.approx(3000.0, rel=0.01)
