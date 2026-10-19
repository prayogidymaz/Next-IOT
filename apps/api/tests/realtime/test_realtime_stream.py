"""Realtime SSE endpoint tests."""

from __future__ import annotations

import asyncio
import uuid
from collections.abc import AsyncIterator, Callable
from unittest.mock import AsyncMock, MagicMock

import pytest
from app.auth.service import decode_access_token
from app.config import settings
from app.main import app
from app.realtime.router import _sse_generator
from app.telemetry.ws_events import publish_control_center_event
from app.types.json_types import as_json_str
from app.types.redis_client import close_redis, redis_from_url
from httpx import AsyncClient

PASSWORD = "SecurePass123!"
SSE_READ_TIMEOUT = 5.0


async def _login_token(client: AsyncClient, slug: str, email: str) -> str:
    resp = await client.post(
        "/auth/register",
        json={"email": email, "password": PASSWORD, "tenant_name": "Rt Tenant", "tenant_slug": slug},
    )
    assert resp.status_code == 201
    login = await client.post("/auth/login", json={"email": email, "password": PASSWORD})
    assert login.status_code == 200
    return str(login.json()["access_token"])


def _tenant_id_from_token(token: str) -> str:
    payload = decode_access_token(token)
    tenant_id = as_json_str(payload.get("tenant_id"))
    assert tenant_id is not None
    return tenant_id


def _sse_request() -> MagicMock:
    request = MagicMock()
    request.app = app
    request.is_disconnected = AsyncMock(return_value=False)
    return request


async def _read_sse_until(
    iterator: AsyncIterator[bytes],
    *,
    timeout: float,
    predicate: Callable[[bytes], bool],
    initial: bytes = b"",
) -> bytes:
    buffer = initial

    async def _consume() -> bytes:
        nonlocal buffer
        while True:
            chunk = await iterator.__anext__()
            buffer += chunk
            if predicate(buffer):
                return buffer

    return await asyncio.wait_for(_consume(), timeout=timeout)


async def _publish_event(tenant_id: str, marker: str) -> None:
    publisher = redis_from_url(settings.redis_url_for_tests())
    try:
        await publish_control_center_event(
            publisher,
            tenant_id=tenant_id,
            event_type="telemetry",
            payload={"secret": marker},
        )
    finally:
        await close_redis(publisher)


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
async def test_realtime_stream_tenant_isolation(
    client: AsyncClient,
    unique_slug: str,
    unique_email: str,
) -> None:
    token_a = await _login_token(client, unique_slug, unique_email)
    slug_b = f"tenant-{uuid.uuid4().hex[:8]}"
    email_b = f"admin-{uuid.uuid4().hex[:8]}@example.com"
    token_b = await _login_token(client, slug_b, email_b)
    tenant_a_id = _tenant_id_from_token(token_a)
    tenant_b_id = _tenant_id_from_token(token_b)
    assert tenant_a_id != tenant_b_id

    request = _sse_request()
    stream = _sse_generator(request, tenant_id=tenant_a_id, channels=frozenset({"telemetry"}))
    iterator = stream.__aiter__()

    buffer = await asyncio.wait_for(iterator.__anext__(), timeout=SSE_READ_TIMEOUT)
    assert b"connected" in buffer
    buffer += await asyncio.wait_for(iterator.__anext__(), timeout=SSE_READ_TIMEOUT)

    marker_b = f"cross-tenant-{uuid.uuid4().hex}"
    await _publish_event(tenant_b_id, marker_b)
    for _ in range(3):
        buffer += await asyncio.wait_for(iterator.__anext__(), timeout=SSE_READ_TIMEOUT)
    assert marker_b not in buffer.decode(errors="replace")

    marker_a = f"own-tenant-{uuid.uuid4().hex}"
    await _publish_event(tenant_a_id, marker_a)
    owned = await asyncio.wait_for(
        _read_sse_until(
            iterator,
            timeout=SSE_READ_TIMEOUT,
            predicate=lambda data: marker_a.encode() in data,
            initial=buffer,
        ),
        timeout=SSE_READ_TIMEOUT + 2.0,
    )
    assert marker_a.encode() in owned
    await stream.aclose()
