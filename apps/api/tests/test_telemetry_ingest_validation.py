"""Integration tests for thing-model validation at telemetry bulk ingest and commands."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime

import pytest
from app.database import async_session
from app.device_profiles.spec import (
    CommandDef,
    CommandParamBoolean,
    TelemetryKeyBoolean,
    TelemetryKeyEnum,
    TelemetryKeyNumber,
    ThingModelSpec,
)
from app.models.telemetry_reading import TelemetryReading
from httpx import AsyncClient
from sqlalchemy import select

PASSWORD = "SecurePass123!"


def _profile_key(prefix: str, slug: str) -> str:
    safe = slug.replace("-", "_")[:48]
    return f"{prefix}_{safe}"[:64]


async def _register_operator(client: AsyncClient, slug: str, email: str) -> str:
    reg = await client.post(
        "/auth/register",
        json={"tenant_name": f"T {slug}", "tenant_slug": slug, "email": email, "password": PASSWORD},
    )
    assert reg.status_code == 201
    return reg.json()["tokens"]["access_token"]


async def _create_online_device(client: AsyncClient, token: str, name: str = "Sensor") -> str:
    create = await client.post(
        "/api/v1/devices",
        headers={"Authorization": f"Bearer {token}"},
        json={"name": name, "device_type": "multi_sensor"},
    )
    assert create.status_code == 201
    body = create.json()
    device_id = body["device"]["id"]
    prov = await client.post(
        f"/api/v1/devices/{device_id}/provision",
        json={"provisioning_token": body["provisioning_token"]},
    )
    creds = prov.json()
    import base64

    basic = base64.b64encode(f"{creds['client_id']}:{creds['client_secret']}".encode()).decode()
    hb = await client.post(
        f"/api/v1/devices/{device_id}/heartbeat",
        headers={"Authorization": f"Basic {basic}"},
        json={},
    )
    assert hb.status_code == 200
    return device_id


async def _publish_profile(client: AsyncClient, token: str, key: str, spec: ThingModelSpec) -> uuid.UUID:
    created = await client.post(
        "/api/v1/device-profiles",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "key": key,
            "name": key,
            "description": "test",
            "domain": "smart_home",
            "spec": spec.model_dump(mode="json"),
        },
    )
    assert created.status_code == 201
    profile_id = created.json()["id"]
    pub = await client.post(
        f"/api/v1/device-profiles/{profile_id}/publish",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert pub.status_code == 200
    return uuid.UUID(profile_id)


async def _assign_profile(client: AsyncClient, token: str, device_id: str, profile_id: uuid.UUID) -> None:
    resp = await client.patch(
        f"/api/v1/devices/{device_id}/profile",
        headers={"Authorization": f"Bearer {token}"},
        json={"profile_id": str(profile_id)},
    )
    assert resp.status_code == 204


def _smart_switch_spec() -> ThingModelSpec:
    return ThingModelSpec(
        telemetry=[TelemetryKeyBoolean(key="relay_on", label="Relay", data_type="boolean")],
        attributes=[],
        commands=[
            CommandDef(key="turn_on", label="On", params=[]),
            CommandDef(key="turn_off", label="Off", params=[]),
        ],
    )


def _env_sensor_spec() -> ThingModelSpec:
    return ThingModelSpec(
        telemetry=[
            TelemetryKeyNumber(key="temperature", label="Temp", data_type="number", min=-40, max=85),
            TelemetryKeyNumber(key="battery", label="Battery", data_type="number", min=0, max=100),
        ],
        attributes=[],
        commands=[],
    )


def _enum_sensor_spec() -> ThingModelSpec:
    return ThingModelSpec(
        telemetry=[
            TelemetryKeyEnum(
                key="mode",
                label="Mode",
                data_type="enum",
                values=["auto", "manual"],
            ),
        ],
        attributes=[],
        commands=[],
    )


async def _bulk(client: AsyncClient, token: str, device_id: str, metrics: dict[str, object]) -> object:
    ts = datetime.now(UTC).isoformat()
    return await client.post(
        "/api/v1/telemetry/bulk",
        headers={"Authorization": f"Bearer {token}"},
        json={"items": [{"device_id": device_id, "timestamp": ts, "metrics": metrics}]},
    )


@pytest.mark.asyncio
async def test_telemetry_ingest_no_profile_accepts_all(
    client: AsyncClient, unique_slug: str, unique_email: str
) -> None:
    token = await _register_operator(client, unique_slug, unique_email)
    device_id = await _create_online_device(client, token)
    resp = await _bulk(client, token, device_id, {"temperature": 25, "custom_field": 1})
    assert resp.status_code == 200
    body = resp.json()
    assert body["accepted_count"] == 1
    assert body["rejected"] == []


@pytest.mark.asyncio
async def test_telemetry_ingest_with_profile_accepts_valid(
    client: AsyncClient, unique_slug: str, unique_email: str
) -> None:
    token = await _register_operator(client, unique_slug, unique_email)
    device_id = await _create_online_device(client, token)
    profile_id = await _publish_profile(client, token, _profile_key("sw", unique_slug), _smart_switch_spec())
    await _assign_profile(client, token, device_id, profile_id)

    resp = await _bulk(client, token, device_id, {"relay_on": True})
    assert resp.status_code == 200
    assert resp.json()["accepted_count"] == 1
    assert resp.json()["rejected"] == []


@pytest.mark.asyncio
async def test_telemetry_ingest_rejects_wrong_type(
    client: AsyncClient, unique_slug: str, unique_email: str
) -> None:
    token = await _register_operator(client, unique_slug, unique_email)
    device_id = await _create_online_device(client, token)
    profile_id = await _publish_profile(client, token, _profile_key("sw2", unique_slug), _smart_switch_spec())
    await _assign_profile(client, token, device_id, profile_id)

    resp = await _bulk(client, token, device_id, {"relay_on": "salah"})
    assert resp.status_code == 200
    rejected = resp.json()["rejected"]
    assert len(rejected) == 1
    assert rejected[0]["reason"] == "wrong_type"


@pytest.mark.asyncio
async def test_telemetry_ingest_rejects_out_of_range(
    client: AsyncClient, unique_slug: str, unique_email: str
) -> None:
    token = await _register_operator(client, unique_slug, unique_email)
    device_id = await _create_online_device(client, token)
    profile_id = await _publish_profile(client, token, _profile_key("env", unique_slug), _env_sensor_spec())
    await _assign_profile(client, token, device_id, profile_id)

    resp = await _bulk(client, token, device_id, {"temperature": 9999})
    assert resp.status_code == 200
    assert resp.json()["rejected"][0]["reason"] == "out_of_range"


@pytest.mark.asyncio
async def test_telemetry_ingest_rejects_enum_not_allowed(
    client: AsyncClient, unique_slug: str, unique_email: str
) -> None:
    token = await _register_operator(client, unique_slug, unique_email)
    device_id = await _create_online_device(client, token)
    profile_id = await _publish_profile(client, token, _profile_key("en", unique_slug), _enum_sensor_spec())
    await _assign_profile(client, token, device_id, profile_id)

    resp = await _bulk(client, token, device_id, {"mode": "turbo"})
    assert resp.status_code == 200
    assert resp.json()["rejected"][0]["reason"] == "enum_not_allowed"


@pytest.mark.asyncio
async def test_telemetry_ingest_unknown_key_warning_not_reject(
    client: AsyncClient, unique_slug: str, unique_email: str
) -> None:
    token = await _register_operator(client, unique_slug, unique_email)
    device_id = await _create_online_device(client, token)
    profile_id = await _publish_profile(client, token, _profile_key("sw3", unique_slug), _smart_switch_spec())
    await _assign_profile(client, token, device_id, profile_id)

    resp = await _bulk(client, token, device_id, {"relay_on": True, "temperature": 25})
    assert resp.status_code == 200
    body = resp.json()
    assert body["accepted_count"] == 1
    assert body["rejected"] == []
    assert any(entry["key"] == "temperature" for entry in body["unknown_keys"])


@pytest.mark.asyncio
async def test_telemetry_ingest_partial_success_returns_200_with_detail(
    client: AsyncClient, unique_slug: str, unique_email: str
) -> None:
    token = await _register_operator(client, unique_slug, unique_email)
    device_id = await _create_online_device(client, token)
    profile_id = await _publish_profile(client, token, _profile_key("env2", unique_slug), _env_sensor_spec())
    await _assign_profile(client, token, device_id, profile_id)

    resp = await _bulk(
        client,
        token,
        device_id,
        {"temperature": 25.5, "humidity": 40, "battery": "x"},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["accepted_count"] == 1
    assert len(body["rejected"]) == 1
    assert body["rejected"][0]["key"] == "battery"

    async with async_session() as session:
        reading = await session.scalar(
            select(TelemetryReading)
            .where(TelemetryReading.device_id == uuid.UUID(device_id))
            .order_by(TelemetryReading.recorded_at.desc())
        )
        assert reading is not None
        assert reading.metrics["temperature"] == 25.5
        assert reading.metrics["humidity"] == 40
        assert "battery" not in reading.metrics


@pytest.mark.asyncio
async def test_command_ingest_rejects_unknown_command(
    client: AsyncClient, unique_slug: str, unique_email: str
) -> None:
    token = await _register_operator(client, unique_slug, unique_email)
    device_id = await _create_online_device(client, token)
    profile_id = await _publish_profile(client, token, _profile_key("swc", unique_slug), _smart_switch_spec())
    await _assign_profile(client, token, device_id, profile_id)

    resp = await client.post(
        f"/api/v1/devices/{device_id}/commands",
        headers={"Authorization": f"Bearer {token}"},
        json={"command_type": "GO_TO_MISSION", "params": {"waypoints": [{"lat": 1, "lon": 2}]}},
    )
    assert resp.status_code == 400


@pytest.mark.asyncio
async def test_command_ingest_rejects_wrong_param_type(
    client: AsyncClient, unique_slug: str, unique_email: str
) -> None:
    token = await _register_operator(client, unique_slug, unique_email)
    device_id = await _create_online_device(client, token)
    spec = ThingModelSpec(
        telemetry=[],
        attributes=[],
        commands=[
            CommandDef(
                key="set_actuator",
                label="Actuator",
                params=[CommandParamBoolean(key="enabled", data_type="boolean", required=True)],
            ),
        ],
    )
    profile_id = await _publish_profile(client, token, _profile_key("lock", unique_slug), spec)
    await _assign_profile(client, token, device_id, profile_id)

    resp = await client.post(
        f"/api/v1/devices/{device_id}/commands",
        headers={"Authorization": f"Bearer {token}"},
        json={"command_type": "SET_ACTUATOR", "params": {"enabled": "yes"}},
    )
    assert resp.status_code == 400


@pytest.mark.asyncio
async def test_command_ingest_valid_passes(
    client: AsyncClient, unique_slug: str, unique_email: str
) -> None:
    token = await _register_operator(client, unique_slug, unique_email)
    device_id = await _create_online_device(client, token)
    profile_id = await _publish_profile(client, token, _profile_key("swv", unique_slug), _smart_switch_spec())
    await _assign_profile(client, token, device_id, profile_id)

    resp = await client.post(
        f"/api/v1/devices/{device_id}/commands",
        headers={"Authorization": f"Bearer {token}"},
        json={"command_type": "RELAY_ON", "params": {}},
    )
    assert resp.status_code == 201


@pytest.mark.asyncio
async def test_metrics_endpoint_includes_rejection_counters(
    client: AsyncClient, unique_slug: str, unique_email: str
) -> None:
    token = await _register_operator(client, unique_slug, unique_email)
    device_id = await _create_online_device(client, token)
    profile_id = await _publish_profile(client, token, _profile_key("met", unique_slug), _smart_switch_spec())
    await _assign_profile(client, token, device_id, profile_id)
    await _bulk(client, token, device_id, {"relay_on": "bad"})

    metrics_resp = await client.get("/metrics")
    assert metrics_resp.status_code == 200
    text = metrics_resp.text
    assert "telemetry_rejected_total" in text
    assert "telemetry_accepted_total" in text
    assert "command_rejected_total" in text
