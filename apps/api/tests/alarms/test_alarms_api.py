"""Alarm lifecycle API tests."""

from __future__ import annotations

import uuid

import pytest
from app.alarms.fingerprint import alarm_fingerprint
from app.alarms.service import upsert_alarm
from app.database import async_session
from app.models.alarm import Alarm, AlarmStatus
from app.telemetry.ingest_pipeline import TelemetryRejectedMetric
from httpx import AsyncClient
from sqlalchemy import select

PASSWORD = "SecurePass123!"


async def _token(client: AsyncClient, slug: str, email: str) -> str:
    reg = await client.post(
        "/auth/register",
        json={
            "tenant_name": f"T {slug}",
            "tenant_slug": slug,
            "email": email,
            "password": PASSWORD,
        },
    )
    assert reg.status_code == 201
    return reg.json()["tokens"]["access_token"]


@pytest.mark.asyncio
async def test_alarm_create_dedup_by_fingerprint(
    client: AsyncClient, unique_slug: str, unique_email: str
) -> None:
    token = await _token(client, unique_slug, unique_email)
    body = {
        "alarm_type": "test",
        "severity": "warning",
        "title": "Dup",
        "message": "one",
        "details": {"metric_key": "temp"},
    }
    first = await client.post("/api/v1/alarms", headers={"Authorization": f"Bearer {token}"}, json=body)
    second = await client.post("/api/v1/alarms", headers={"Authorization": f"Bearer {token}"}, json=body)
    assert first.status_code == 201
    assert second.status_code == 201
    assert first.json()["id"] == second.json()["id"]


@pytest.mark.asyncio
async def test_alarm_escalation_count_increments(
    client: AsyncClient, unique_slug: str, unique_email: str
) -> None:
    token = await _token(client, unique_slug, unique_email)
    body = {
        "alarm_type": "test",
        "severity": "minor",
        "title": "Esc",
        "details": {"metric_key": "x"},
    }
    await client.post("/api/v1/alarms", headers={"Authorization": f"Bearer {token}"}, json=body)
    resp = await client.post("/api/v1/alarms", headers={"Authorization": f"Bearer {token}"}, json=body)
    assert resp.json()["escalation_count"] >= 1


@pytest.mark.asyncio
async def test_alarm_state_transitions(client: AsyncClient, unique_slug: str, unique_email: str) -> None:
    token = await _token(client, unique_slug, unique_email)
    create = await client.post(
        "/api/v1/alarms",
        headers={"Authorization": f"Bearer {token}"},
        json={"alarm_type": "test", "severity": "info", "title": "Flow"},
    )
    alarm_id = create.json()["id"]
    ack = await client.post(
        f"/api/v1/alarms/{alarm_id}/acknowledge",
        headers={"Authorization": f"Bearer {token}"},
        json={"note": "seen"},
    )
    assert ack.json()["status"] == "acknowledged"
    resolve = await client.post(
        f"/api/v1/alarms/{alarm_id}/resolve",
        headers={"Authorization": f"Bearer {token}"},
        json={},
    )
    assert resolve.json()["status"] == "resolved"


@pytest.mark.asyncio
async def test_alarm_cannot_resolve_from_active_directly(
    client: AsyncClient, unique_slug: str, unique_email: str
) -> None:
    token = await _token(client, unique_slug, unique_email)
    create = await client.post(
        "/api/v1/alarms",
        headers={"Authorization": f"Bearer {token}"},
        json={"alarm_type": "test", "severity": "warning", "title": "NoSkip"},
    )
    alarm_id = create.json()["id"]
    resp = await client.post(
        f"/api/v1/alarms/{alarm_id}/resolve",
        headers={"Authorization": f"Bearer {token}"},
        json={},
    )
    assert resp.status_code == 409


@pytest.mark.asyncio
async def test_alarm_history_recorded_per_transition(
    client: AsyncClient, unique_slug: str, unique_email: str
) -> None:
    token = await _token(client, unique_slug, unique_email)
    create = await client.post(
        "/api/v1/alarms",
        headers={"Authorization": f"Bearer {token}"},
        json={"alarm_type": "test", "severity": "info", "title": "Hist"},
    )
    alarm_id = create.json()["id"]
    await client.post(
        f"/api/v1/alarms/{alarm_id}/acknowledge",
        headers={"Authorization": f"Bearer {token}"},
        json={},
    )
    hist = await client.get(
        f"/api/v1/alarms/{alarm_id}/history",
        headers={"Authorization": f"Bearer {token}"},
    )
    actions = {item["action"] for item in hist.json()["items"]}
    assert "created" in actions
    assert "acknowledged" in actions


@pytest.mark.asyncio
async def test_alarm_auto_clear_on_valid_telemetry(
    client: AsyncClient, unique_slug: str, unique_email: str
) -> None:
    token = await _token(client, unique_slug, unique_email)
    create = await client.post(
        "/api/v1/devices",
        headers={"Authorization": f"Bearer {token}"},
        json={"name": "Val", "device_type": "sensor"},
    )
    device_id = create.json()["device"]["id"]
    tenant_id = uuid.UUID(create.json()["device"]["tenant_id"])
    async with async_session() as db:
        await upsert_alarm(
            db,
            tenant_id=tenant_id,
            device_id=uuid.UUID(device_id),
            alarm_type="validation_failed",
            severity="minor",
            title="bad",
            message="m",
            details={"metric_key": "temperature"},
            source="validator",
            notify=False,
        )
        from app.alarms.validator_hooks import clear_validation_alarms_for_metrics

        await clear_validation_alarms_for_metrics(
            db,
            tenant_id=tenant_id,
            device_id=uuid.UUID(device_id),
            metric_keys={"temperature"},
        )
        await db.commit()
        row = await db.scalar(select(Alarm).where(Alarm.device_id == uuid.UUID(device_id)))
    assert row is not None
    assert row.status == AlarmStatus.CLEARED


@pytest.mark.asyncio
async def test_alarm_list_filter_by_severity_status_device(
    client: AsyncClient, unique_slug: str, unique_email: str
) -> None:
    token = await _token(client, unique_slug, unique_email)
    await client.post(
        "/api/v1/alarms",
        headers={"Authorization": f"Bearer {token}"},
        json={"alarm_type": "a", "severity": "critical", "title": "C"},
    )
    listed = await client.get(
        "/api/v1/alarms",
        headers={"Authorization": f"Bearer {token}"},
        params={"severity": "critical", "status": "active"},
    )
    assert listed.status_code == 200
    assert all(i["severity"] == "critical" for i in listed.json()["items"])


@pytest.mark.asyncio
async def test_alarm_tenant_isolation(client: AsyncClient, unique_slug: str, unique_email: str) -> None:
    token_a = await _token(client, unique_slug, unique_email)
    create = await client.post(
        "/api/v1/alarms",
        headers={"Authorization": f"Bearer {token_a}"},
        json={"alarm_type": "iso", "severity": "info", "title": "Iso"},
    )
    alarm_id = create.json()["id"]
    token_b = await _token(client, f"other-{uuid.uuid4().hex[:8]}", f"x-{uuid.uuid4().hex[:8]}@example.com")
    foreign = await client.get(
        f"/api/v1/alarms/{alarm_id}",
        headers={"Authorization": f"Bearer {token_b}"},
    )
    assert foreign.status_code == 404


@pytest.mark.asyncio
async def test_alarm_delete_requires_super_admin(
    client: AsyncClient, unique_slug: str, unique_email: str
) -> None:
    token = await _token(client, unique_slug, unique_email)
    create = await client.post(
        "/api/v1/alarms",
        headers={"Authorization": f"Bearer {token}"},
        json={"alarm_type": "del", "severity": "info", "title": "Del"},
    )
    alarm_id = create.json()["id"]
    denied = await client.delete(
        f"/api/v1/alarms/{alarm_id}",
        headers={"Authorization": f"Bearer {token}"},
        params={"reason": "test"},
    )
    assert denied.status_code == 403


@pytest.mark.asyncio
async def test_alarm_from_validator_rejected_metrics(
    client: AsyncClient, unique_slug: str, unique_email: str
) -> None:
    from app.alarms.validator_hooks import handle_rejected_metrics_alarms

    token = await _token(client, unique_slug, unique_email)
    create = await client.post(
        "/api/v1/devices",
        headers={"Authorization": f"Bearer {token}"},
        json={"name": "ValAlarm", "device_type": "sensor"},
    )
    device_id = uuid.UUID(create.json()["device"]["id"])
    tenant_id = uuid.UUID(create.json()["device"]["tenant_id"])
    async with async_session() as db:
        await handle_rejected_metrics_alarms(
            db,
            tenant_id=tenant_id,
            device_id=device_id,
            rejected=(
                TelemetryRejectedMetric(key="temperature", reason="out_of_range", value=999),
            ),
        )
        await db.commit()
    listed = await client.get(
        "/api/v1/alarms",
        headers={"Authorization": f"Bearer {token}"},
        params={"status": "active"},
    )
    assert any(i["alarm_type"] == "validation_failed" for i in listed.json()["items"])


@pytest.mark.asyncio
async def test_alarm_acknowledge_updates_fields(
    client: AsyncClient, unique_slug: str, unique_email: str
) -> None:
    token = await _token(client, unique_slug, unique_email)
    create = await client.post(
        "/api/v1/alarms",
        headers={"Authorization": f"Bearer {token}"},
        json={"alarm_type": "ack", "severity": "warning", "title": "Ack"},
    )
    alarm_id = create.json()["id"]
    ack = await client.post(
        f"/api/v1/alarms/{alarm_id}/acknowledge",
        headers={"Authorization": f"Bearer {token}"},
        json={"note": "ok"},
    )
    body = ack.json()
    assert body["acknowledged_at"] is not None
    assert body["acknowledged_by_user_id"] is not None


def test_alarm_fingerprint_hash_stable() -> None:
    tid = uuid.uuid4()
    did = uuid.uuid4()
    a = alarm_fingerprint(tenant_id=tid, device_id=did, alarm_type="validation_failed", dedup_key="temp")
    b = alarm_fingerprint(tenant_id=tid, device_id=did, alarm_type="validation_failed", dedup_key="temp")
    assert a == b
    assert len(a) == 64
