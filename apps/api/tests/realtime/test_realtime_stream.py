"""Realtime SSE endpoint tests."""

from __future__ import annotations

import pytest
from httpx import AsyncClient

PASSWORD = "SecurePass123!"


async def _login_token(client: AsyncClient, slug: str, email: str) -> str:
    resp = await client.post(
        "/auth/register",
        json={"email": email, "password": PASSWORD, "tenant_name": "Rt Tenant", "tenant_slug": slug},
    )
    assert resp.status_code == 201
    login = await client.post("/auth/login", json={"email": email, "password": PASSWORD})
    assert login.status_code == 200
    return str(login.json()["access_token"])


@pytest.mark.asyncio
async def test_realtime_stream_unauthorized(client: AsyncClient) -> None:
    resp = await client.get("/api/v1/realtime/stream")
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_realtime_stream_invalid_channel(client: AsyncClient, unique_slug: str, unique_email: str) -> None:
    token = await _login_token(client, unique_slug, unique_email)
    resp = await client.get(
        "/api/v1/realtime/stream",
        params={"token": token, "channels": "telemetry,not_a_channel"},
    )
    assert resp.status_code == 400


@pytest.mark.asyncio
async def test_realtime_stream_tenant_isolation(client: AsyncClient, unique_slug: str, unique_email: str) -> None:
    token = await _login_token(client, unique_slug, unique_email)
    async with client.stream("GET", "/api/v1/realtime/stream", params={"token": token}) as resp:
        assert resp.status_code == 200
        assert resp.headers.get("content-type", "").startswith("text/event-stream")
        chunk = b""
        async for part in resp.aiter_bytes():
            chunk += part
            if b"connected" in chunk or len(chunk) > 64:
                break
        assert b"connected" in chunk

