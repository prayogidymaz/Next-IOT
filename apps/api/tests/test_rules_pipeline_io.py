import pytest
from httpx import AsyncClient

from tests.test_commands import _register_and_create_device

PIPELINE_DOC = {
    "schema_version": "next-iot.automation-pipeline.v1",
    "pipeline": {
        "name": "Heat Relay",
        "description": "Turn relay on when hot",
        "is_active": True,
        "nodes": [
            {
                "id": "t1",
                "type": "TRIGGER",
                "subtype": "TELEMETRY_THRESHOLD",
                "config": {"metric": "temperature", "operator": ">", "threshold": 30},
            },
            {
                "id": "c1",
                "type": "CONDITION",
                "subtype": "TIME_WINDOW",
                "config": {"start_hour": 0, "end_hour": 23},
            },
            {
                "id": "a1",
                "type": "ACTION",
                "subtype": "DEVICE_COMMAND",
                "config": {"device_id": "relay-1", "command": "relay_on"},
            },
        ],
        "edges": [
            {"from": "t1", "to": "c1"},
            {"from": "c1", "to": "a1"},
        ],
    },
}


@pytest.mark.asyncio
async def test_validate_pipeline_json(client: AsyncClient, unique_slug: str, unique_email: str):
    ctx = await _register_and_create_device(client, unique_slug, unique_email)
    headers = {"Authorization": f"Bearer {ctx['token']}"}

    resp = await client.post(
        "/api/v1/rules/validate",
        headers=headers,
        json={"document": PIPELINE_DOC},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["valid"] is True
    assert body["errors"] == []


@pytest.mark.asyncio
async def test_validate_rejects_cycle(client: AsyncClient, unique_slug: str, unique_email: str):
    ctx = await _register_and_create_device(client, unique_slug, unique_email)
    headers = {"Authorization": f"Bearer {ctx['token']}"}
    cyclic = {
        "pipeline": {
            "name": "Bad",
            "nodes": [
                {"id": "a", "type": "TRIGGER", "subtype": "WEATHER_HAZARD", "config": {}},
                {"id": "b", "type": "ACTION", "subtype": "TRIGGER_ALERT", "config": {}},
            ],
            "edges": [
                {"from": "a", "to": "b"},
                {"from": "b", "to": "a"},
            ],
        }
    }
    resp = await client.post(
        "/api/v1/rules/validate",
        headers=headers,
        json={"document": cyclic},
    )
    assert resp.status_code == 200
    assert resp.json()["valid"] is False
    assert any("circular" in e.lower() for e in resp.json()["errors"])


@pytest.mark.asyncio
async def test_import_and_export_pipeline(client: AsyncClient, unique_slug: str, unique_email: str):
    ctx = await _register_and_create_device(client, unique_slug, unique_email)
    headers = {"Authorization": f"Bearer {ctx['token']}"}

    imp = await client.post(
        "/api/v1/rules/import",
        headers=headers,
        json={"document": PIPELINE_DOC},
    )
    assert imp.status_code == 201
    pipeline_id = imp.json()["pipeline"]["id"]

    exp = await client.get(f"/api/v1/rules/{pipeline_id}/export", headers=headers)
    assert exp.status_code == 200
    exported = exp.json()
    assert exported["schema_version"] == "next-iot.automation-pipeline.v1"
    assert exported["pipeline"]["name"] == "Heat Relay"
    assert len(exported["pipeline"]["nodes"]) == 3


@pytest.mark.asyncio
async def test_dry_run_unsaved_pipeline(client: AsyncClient, unique_slug: str, unique_email: str):
    ctx = await _register_and_create_device(client, unique_slug, unique_email)
    headers = {"Authorization": f"Bearer {ctx['token']}"}
    nodes = PIPELINE_DOC["pipeline"]["nodes"]
    edges = PIPELINE_DOC["pipeline"]["edges"]

    resp = await client.post(
        "/api/v1/automation/pipelines/dry-run",
        headers=headers,
        json={
            "event_type": "TELEMETRY_THRESHOLD",
            "context": {"metrics": {"temperature": 35}},
            "nodes": nodes,
            "edges": edges,
        },
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["executed"] is True
    assert len(body["steps"]) >= 3
