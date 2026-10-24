"""FCM push client and token registration API tests."""

from __future__ import annotations

import uuid
from unittest.mock import patch

import pytest
from httpx import AsyncClient

from app.notifications.fcm_push import FcmPushClient, FcmSendResult

PASSWORD = "SecurePass123!"


@pytest.mark.asyncio
async def test_fcm_send_success_mock_disabled() -> None:
    client = FcmPushClient()
    result = await client.send("token-abc", "Title", "Body", {"k": "v"})
    assert result.success is True
    assert result.unregistered is False


@pytest.mark.asyncio
async def test_fcm_send_404_token_unregistered() -> None:
    client = FcmPushClient()
    with patch("app.notifications.fcm_push.settings") as mock_settings:
        mock_settings.notification_fcm_enabled = True
        with patch.object(client, "_ensure_firebase", return_value=True):
            with patch("firebase_admin.messaging.send", side_effect=Exception("404 Not Found")):
                result = await client.send("bad-token", "T", "B", {})
    assert result.success is False
    assert result.unregistered is True


@pytest.mark.asyncio
async def test_fcm_register_endpoint(client: AsyncClient, unique_slug: str, unique_email: str) -> None:
    reg = await client.post(
        "/auth/register",
        json={"tenant_name": "FCM", "tenant_slug": unique_slug, "email": unique_email, "password": PASSWORD},
    )
    token = reg.json()["tokens"]["access_token"]
    res = await client.post(
        "/api/v1/notifications/fcm/register",
        headers={"Authorization": f"Bearer {token}"},
        json={"token": f"fcm-{uuid.uuid4().hex}", "device_type": "wear"},
    )
    assert res.status_code == 201
    assert res.json()["device_type"] == "wear"


@pytest.mark.asyncio
async def test_fcm_unregister_endpoint(client: AsyncClient, unique_slug: str, unique_email: str) -> None:
    reg = await client.post(
        "/auth/register",
        json={"tenant_name": "FCM2", "tenant_slug": unique_slug, "email": unique_email, "password": PASSWORD},
    )
    access = reg.json()["tokens"]["access_token"]
    fcm_token = f"fcm-{uuid.uuid4().hex}"
    await client.post(
        "/api/v1/notifications/fcm/register",
        headers={"Authorization": f"Bearer {access}"},
        json={"token": fcm_token, "device_type": "wear"},
    )
    del_res = await client.delete(
        f"/api/v1/notifications/fcm/unregister?token={fcm_token}",
        headers={"Authorization": f"Bearer {access}"},
    )
    assert del_res.status_code == 204
    listed = await client.get(
        "/api/v1/notifications/fcm/tokens",
        headers={"Authorization": f"Bearer {access}"},
    )
    assert listed.status_code == 200
    assert all(row["token"] != fcm_token for row in listed.json())
