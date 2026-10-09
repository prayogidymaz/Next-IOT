"""Root /health readiness after application lifespan startup."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_root_health_reports_startup_ok_when_ready(client: AsyncClient) -> None:
    resp = await client.get("/health")
    assert resp.status_code == 200
    body = resp.json()
    assert body["status"] == "healthy"
    assert body["checks"]["startup"] == "ok"
    assert body["checks"]["database"] == "ok"
    assert body["checks"]["redis"] == "ok"
