"""Universal Mesh event bus and context protocol tests."""

from __future__ import annotations

import asyncio
import base64
import uuid
from datetime import UTC, datetime

import pytest
from app.agriculture.models import AgriFarm, AgriPlot, AgriSensorDevice
from app.alarms.service import upsert_alarm
from app.database import async_session
from app.mesh.context_resolver import _cache_key, resolve_device_context
from app.mesh.event_bus import MeshDomain, mesh_event_topic
from app.mesh.publisher import init_mesh_publisher
from app.models.device import Device, DeviceStatus
from app.models.mesh_event import MeshEventRecord
from app.models.rule import Rule, RuleActionType, RuleOperator
from app.rules.alerts import pop_alerts
from app.types.json_types import JsonValue
from httpx import AsyncClient
from sqlalchemy import select

PASSWORD = "SecurePass123!"


class RecordingMqttPublisher:
    def __init__(self) -> None:
        self.topics: list[str] = []
        self.payloads: list[dict[str, JsonValue]] = []

    async def publish_json(self, topic: str, payload: dict[str, JsonValue], qos: int = 1) -> None:
        self.topics.append(topic)
        self.payloads.append(payload)


async def _auth_and_device(
    client: AsyncClient, slug: str, email: str
) -> tuple[str, uuid.UUID, uuid.UUID, dict[str, str]]:
    reg = await client.post(
        "/auth/register",
        json={"tenant_name": f"T {slug}", "tenant_slug": slug, "email": email, "password": PASSWORD},
    )
    assert reg.status_code == 201
    token = reg.json()["tokens"]["access_token"]
    tenant_id = uuid.UUID(reg.json()["tenant_id"])
    create = await client.post(
        "/api/v1/devices",
        headers={"Authorization": f"Bearer {token}"},
        json={"name": "Mesh sensor", "device_type": "lora_sensor"},
    )
    assert create.status_code == 201
    body = create.json()
    device_id = uuid.UUID(body["device"]["id"])
    prov = await client.post(
        f"/api/v1/devices/{body['device']['id']}/provision",
        json={"provisioning_token": body["provisioning_token"]},
    )
    creds = prov.json()
    basic = base64.b64encode(f"{creds['client_id']}:{creds['client_secret']}".encode()).decode()
    device_headers = {"Authorization": f"Basic {basic}"}
    await client.post(f"/api/v1/devices/{body['device']['id']}/heartbeat", headers=device_headers, json={})
    return token, tenant_id, device_id, device_headers


async def _wait_mesh_rows(device_id: uuid.UUID, domain: str | None = None) -> list[MeshEventRecord]:
    for _ in range(40):
        async with async_session() as db:
            query = select(MeshEventRecord).where(MeshEventRecord.device_id == device_id)
            if domain is not None:
                query = query.where(MeshEventRecord.domain == domain)
            rows = await db.scalars(query)
            items = rows.all()
            if items:
                return items
        await asyncio.sleep(0.05)
    return []


@pytest.mark.asyncio
async def test_publish_event_persisted_to_db(
    client: AsyncClient, test_redis, unique_slug: str, unique_email: str
) -> None:
    token, tenant_id, device_id, _ = await _auth_and_device(client, unique_slug, unique_email)
    mqtt = RecordingMqttPublisher()
    init_mesh_publisher(test_redis, mqtt)
    resp = await client.post(
        "/api/v1/mesh/events",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "device_id": str(device_id),
            "domain": "sensor",
            "event_type": "reading_update",
            "payload": {"metrics": {"soil_moisture": 42.0}},
        },
    )
    assert resp.status_code == 201
    event_id = uuid.UUID(resp.json()["event_id"])
    async with async_session() as db:
        row = await db.scalar(select(MeshEventRecord).where(MeshEventRecord.id == event_id))
        assert row is not None
        assert row.tenant_id == tenant_id
        assert row.domain == "sensor"
        assert row.event_type == "reading_update"


@pytest.mark.asyncio
async def test_publish_event_broadcasts_to_mqtt_topic(
    client: AsyncClient, test_redis, unique_slug: str, unique_email: str
) -> None:
    token, tenant_id, device_id, _ = await _auth_and_device(client, unique_slug, unique_email)
    mqtt = RecordingMqttPublisher()
    init_mesh_publisher(test_redis, mqtt)
    await client.post(
        "/api/v1/mesh/events",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "device_id": str(device_id),
            "domain": "actuator",
            "event_type": "state_changed",
            "payload": {"state": "open"},
        },
    )
    expected = mesh_event_topic(str(tenant_id), MeshDomain.ACTUATOR, "state_changed")
    assert expected in mqtt.topics
    assert mqtt.payloads[-1]["event_type"] == "state_changed"


@pytest.mark.asyncio
async def test_context_resolver_fetches_farm_plot_zone(test_redis) -> None:
    async with async_session() as db:
        from app.models.tenant import Tenant

        tenant = Tenant(name="Mesh ctx", slug=f"mesh-ctx-{uuid.uuid4().hex[:8]}")
        db.add(tenant)
        await db.flush()
        device = Device(
            tenant_id=tenant.id,
            name="Agri node",
            device_type="lora_sensor",
            status=DeviceStatus.ONLINE,
        )
        db.add(device)
        await db.flush()
        farm = AgriFarm(tenant_id=tenant.id, name="Farm", crop_type="coffee", owner_whatsapp="6281")
        db.add(farm)
        await db.flush()
        plot = AgriPlot(farm_id=farm.id, name="Plot A")
        db.add(plot)
        await db.flush()
        db.add(
            AgriSensorDevice(
                tenant_id=tenant.id,
                farm_id=farm.id,
                plot_id=plot.id,
                device_id=device.id,
                name="S1",
                sensor_type="soil",
                lora_dev_eui=uuid.uuid4().hex[:16],
                position_lat=-6.2,
                position_lng=106.8,
            )
        )
        await db.commit()

        ctx = await resolve_device_context(db, test_redis, device.id)
        assert ctx.farm_id == farm.id
        assert ctx.plot_id == plot.id
        assert ctx.geo_location is not None
        assert abs(ctx.geo_location.lat - (-6.2)) < 0.001


@pytest.mark.asyncio
async def test_context_resolver_caches_redis(test_redis) -> None:
    async with async_session() as db:
        from app.models.tenant import Tenant

        tenant = Tenant(name="Cache", slug=f"mesh-cache-{uuid.uuid4().hex[:8]}")
        db.add(tenant)
        await db.flush()
        device = Device(
            tenant_id=tenant.id,
            name="D",
            device_type="temp",
            status=DeviceStatus.ONLINE,
        )
        db.add(device)
        await db.commit()
        await resolve_device_context(db, test_redis, device.id)
        cached = await test_redis.get(_cache_key(device.id))
        assert isinstance(cached, str) and cached


@pytest.mark.asyncio
async def test_telemetry_ingest_auto_publishes_mesh_event(
    client: AsyncClient, unique_slug: str, unique_email: str
) -> None:
    _, _, device_id, device_headers = await _auth_and_device(client, unique_slug, unique_email)
    resp = await client.post(
        "/api/v1/telemetry",
        headers=device_headers,
        json={"timestamp": datetime.now(UTC).isoformat(), "metrics": {"temperature": 22.5}},
    )
    assert resp.status_code == 201
    rows = await _wait_mesh_rows(device_id, domain="sensor")
    assert len(rows) >= 1
    assert rows[0].event_type == "reading_update"


@pytest.mark.asyncio
async def test_alarm_create_auto_publishes_mesh_event(
    client: AsyncClient, unique_slug: str, unique_email: str
) -> None:
    token, tenant_id, device_id, _ = await _auth_and_device(client, unique_slug, unique_email)
    async with async_session() as db:
        await upsert_alarm(
            db,
            tenant_id=tenant_id,
            device_id=device_id,
            alarm_type="intrusion",
            severity="critical",
            title="Perimeter breach",
            message="motion",
            details={"zone": "north"},
            source="test",
            notify=False,
        )
        await db.commit()
    rows = await _wait_mesh_rows(device_id, domain="security")
    assert any(row.event_type == "intrusion_detected" for row in rows)


@pytest.mark.asyncio
async def test_mesh_events_api_filter_by_domain(
    client: AsyncClient, test_redis, unique_slug: str, unique_email: str
) -> None:
    token, _, device_id, _ = await _auth_and_device(client, unique_slug, unique_email)
    init_mesh_publisher(test_redis, RecordingMqttPublisher())
    headers = {"Authorization": f"Bearer {token}"}
    await client.post(
        "/api/v1/mesh/events",
        headers=headers,
        json={"device_id": str(device_id), "domain": "sensor", "event_type": "battery_low", "payload": {}},
    )
    await client.post(
        "/api/v1/mesh/events",
        headers=headers,
        json={"device_id": str(device_id), "domain": "ui", "event_type": "alert_shown", "payload": {}},
    )
    listed = await client.get("/api/v1/mesh/events", headers=headers, params={"domain": "ui"})
    assert listed.status_code == 200
    body = listed.json()
    assert len(body) >= 1
    assert all(item["domain"] == "ui" for item in body)


@pytest.mark.asyncio
async def test_mesh_events_chain_walk_correlation(
    client: AsyncClient, test_redis, unique_slug: str, unique_email: str
) -> None:
    token, _, device_id, _ = await _auth_and_device(client, unique_slug, unique_email)
    init_mesh_publisher(test_redis, RecordingMqttPublisher())
    headers = {"Authorization": f"Bearer {token}"}
    correlation_id = str(uuid.uuid4())
    parent = await client.post(
        "/api/v1/mesh/events",
        headers=headers,
        json={
            "device_id": str(device_id),
            "domain": "motion",
            "event_type": "dispatch_requested",
            "payload": {},
            "correlation_id": correlation_id,
        },
    )
    parent_id = parent.json()["event_id"]
    child = await client.post(
        "/api/v1/mesh/events",
        headers=headers,
        json={
            "device_id": str(device_id),
            "domain": "motion",
            "event_type": "flight_started",
            "payload": {},
            "correlation_id": correlation_id,
            "parent_event_id": parent_id,
        },
    )
    assert child.status_code == 201
    chain = await client.get(f"/api/v1/mesh/events/{child.json()['event_id']}/chain", headers=headers)
    assert chain.status_code == 200
    ids = {item["event_id"] for item in chain.json()}
    assert parent_id in ids


@pytest.mark.asyncio
async def test_backward_compat_old_rule_engine_still_works(
    client: AsyncClient, test_redis, unique_slug: str, unique_email: str
) -> None:
    token, tenant_id, device_id, device_headers = await _auth_and_device(client, unique_slug, unique_email)
    async with async_session() as session:
        session.add(
            Rule(
                tenant_id=tenant_id,
                device_id=device_id,
                name="High temperature alert",
                metric="temperature",
                operator=RuleOperator.GT,
                threshold=25.0,
                action_type=RuleActionType.ALERT,
                is_active=True,
            )
        )
        await session.commit()

    from app.rules.executor import get_rule_executor

    executor = get_rule_executor()
    if executor is not None:
        async with async_session() as reload_session:
            await executor.reload(reload_session)
            await reload_session.commit()

    resp = await client.post(
        "/api/v1/telemetry",
        headers=device_headers,
        json={"timestamp": datetime.now(UTC).isoformat(), "metrics": {"temperature": 30.0}},
    )
    assert resp.status_code == 201
    assert resp.json()["rules_triggered"] == 1
    alerts = await pop_alerts(test_redis)
    assert len(alerts) == 1
    assert alerts[0]["event"] == "rule.triggered"
