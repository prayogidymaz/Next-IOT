import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_system_health_reports_components(client: AsyncClient):
    resp = await client.get("/api/v1/system/health")
    assert resp.status_code == 200
    body = resp.json()
    assert body["status"] in {"ready", "degraded"}
    assert "components" in body
    assert body["components"]["database"] == "ok"
    assert body["components"]["redis_cache"] == "ok"
    assert body["components"]["mqtt_broker"] in {"ok", "standby", "fail"}
    assert "system_metrics" in body
