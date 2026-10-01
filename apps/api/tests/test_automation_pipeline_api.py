import pytest
from httpx import AsyncClient

from tests.test_commands import _register_and_create_device

SAMPLE_PIPELINE = {
    "name": "Weather Safe SAR Dispatch",
    "description": "Dispatch SAR grid when weather is safe",
    "is_active": True,
    "nodes_json": [
        {"id": "t1", "type": "TRIGGER", "subtype": "WEATHER_HAZARD", "config": {}},
        {"id": "c1", "type": "CONDITION", "subtype": "WIND_SPEED_LESS_THAN", "config": {"threshold": 15}},
        {"id": "a1", "type": "ACTION", "subtype": "DISPATCH_SAR_GRID", "config": {}},
    ],
    "edges_json": [
        {"from": "t1", "to": "c1"},
        {"from": "c1", "to": "a1"},
    ],
}


@pytest.mark.asyncio
async def test_automation_pipeline_crud(client: AsyncClient, unique_slug: str, unique_email: str):
    ctx = await _register_and_create_device(client, unique_slug, unique_email)
    headers = {"Authorization": f"Bearer {ctx['token']}"}

    create_resp = await client.post(
        "/api/v1/automation/pipelines",
        headers=headers,
        json=SAMPLE_PIPELINE,
    )
    assert create_resp.status_code == 201
    created = create_resp.json()
    pipeline_id = created["id"]
    assert created["name"] == "Weather Safe SAR Dispatch"
    assert len(created["nodes_json"]) == 3

    list_resp = await client.get("/api/v1/automation/pipelines", headers=headers)
    assert list_resp.status_code == 200
    assert list_resp.json()["count"] == 1

    get_resp = await client.get(f"/api/v1/automation/pipelines/{pipeline_id}", headers=headers)
    assert get_resp.status_code == 200

    update_resp = await client.put(
        f"/api/v1/automation/pipelines/{pipeline_id}",
        headers=headers,
        json={"name": "Updated Pipeline", "is_active": False},
    )
    assert update_resp.status_code == 200
    assert update_resp.json()["name"] == "Updated Pipeline"
    assert update_resp.json()["is_active"] is False

    delete_resp = await client.delete(f"/api/v1/automation/pipelines/{pipeline_id}", headers=headers)
    assert delete_resp.status_code == 204


@pytest.mark.asyncio
async def test_automation_pipeline_test_run(client: AsyncClient, unique_slug: str, unique_email: str):
    ctx = await _register_and_create_device(client, unique_slug, unique_email)
    headers = {"Authorization": f"Bearer {ctx['token']}"}

    create_resp = await client.post(
        "/api/v1/automation/pipelines",
        headers=headers,
        json=SAMPLE_PIPELINE,
    )
    pipeline_id = create_resp.json()["id"]

    test_resp = await client.post(
        f"/api/v1/automation/pipelines/{pipeline_id}/test-run",
        headers=headers,
        json={
            "event_type": "WEATHER_HAZARD",
            "context": {
                "flight_safety_status": "CAUTION",
                "wind_speed_m_s": 10,
                "lat": -6.2088,
                "lon": 106.8456,
            },
        },
    )
    assert test_resp.status_code == 200
    body = test_resp.json()
    assert body["executed"] is True
    assert body["event_type"] == "WEATHER_HAZARD"
    assert len(body["steps"]) >= 3
    action_steps = [s for s in body["steps"] if s["node_type"] == "ACTION"]
    assert action_steps[0]["subtype"] == "DISPATCH_SAR_GRID"


@pytest.mark.asyncio
async def test_automation_pipeline_validation_error(client: AsyncClient, unique_slug: str, unique_email: str):
    ctx = await _register_and_create_device(client, unique_slug, unique_email)
    headers = {"Authorization": f"Bearer {ctx['token']}"}

    resp = await client.post(
        "/api/v1/automation/pipelines",
        headers=headers,
        json={
            "name": "Invalid",
            "nodes_json": [{"id": "t1", "type": "TRIGGER", "subtype": "AI_DETECTION"}],
            "edges_json": [{"from": "t1", "to": "missing"}],
        },
    )
    assert resp.status_code == 422
