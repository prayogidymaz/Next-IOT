"""Redis cache invalidation when rotating device MQTT credentials."""

from __future__ import annotations

import uuid
from unittest.mock import AsyncMock, patch

import pytest
from app.mqtt_auth.cache import get_cached_credential, set_cached_credential
from app.types.redis_client import RedisClient
from httpx import AsyncClient

PASSWORD = "SecurePass123!"


async def _register_token(client: AsyncClient, slug: str, email: str) -> str:
    reg = await client.post(
        "/auth/register",
        json={"tenant_name": f"T {slug}", "tenant_slug": slug, "email": email, "password": PASSWORD},
    )
    assert reg.status_code == 201
    return reg.json()["tokens"]["access_token"]


async def _device_with_credential(client: AsyncClient, token: str) -> tuple[str, str]:
    create = await client.post(
        "/api/v1/devices",
        headers={"Authorization": f"Bearer {token}"},
        json={"name": "CacheRotateDev", "device_type": "sensor"},
    )
    device_id = create.json()["device"]["id"]
    gen = await client.post(
        f"/api/v1/devices/{device_id}/credentials",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert gen.status_code == 201
    return device_id, gen.json()["access_token"]


@pytest.mark.asyncio
async def test_rotate_clears_old_token_cache(
    client: AsyncClient,
    test_redis: RedisClient,
    unique_slug: str,
    unique_email: str,
) -> None:
    _ = test_redis
    token = await _register_token(client, unique_slug, unique_email)
    device_id, first_token = await _device_with_credential(client, token)
    with patch(
        "app.device_credentials.service.invalidate_mqtt_auth_cache_for_tokens",
        new_callable=AsyncMock,
    ) as batch_invalidate_mock:
        rotate = await client.post(
            f"/api/v1/devices/{device_id}/credentials/rotate",
            headers={"Authorization": f"Bearer {token}"},
        )
    assert rotate.status_code == 200
    new_token = rotate.json()["access_token"]
    batch_invalidate_mock.assert_awaited_once()
    call_tokens = list(batch_invalidate_mock.await_args.args[1:])
    assert first_token in call_tokens
    assert new_token in call_tokens


@pytest.mark.asyncio
async def test_rotate_clears_new_token_negative_cache(
    client: AsyncClient,
    test_redis: RedisClient,
    unique_slug: str,
    unique_email: str,
) -> None:
    token = await _register_token(client, unique_slug, unique_email)
    device_id, first_token = await _device_with_credential(client, token)
    tenant_resp = await client.get(
        f"/api/v1/devices/{device_id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    tenant_id = uuid.UUID(tenant_resp.json()["tenant_id"])

    rotate = await client.post(
        f"/api/v1/devices/{device_id}/credentials/rotate",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert rotate.status_code == 200
    new_token = rotate.json()["access_token"]

    await set_cached_credential(
        test_redis,
        new_token,
        device_id=uuid.UUID(device_id),
        tenant_id=tenant_id,
    )
    assert await get_cached_credential(test_redis, new_token) is not None

    rotate_again = await client.post(
        f"/api/v1/devices/{device_id}/credentials/rotate",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert rotate_again.status_code == 200
    assert await get_cached_credential(test_redis, new_token) is None
