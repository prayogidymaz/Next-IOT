import pytest
from httpx import AsyncClient

PASSWORD = "SecurePass123!"


@pytest.mark.asyncio
async def test_v1_auth_register_login_me_refresh(client: AsyncClient, unique_email: str):
    reg = await client.post(
        "/api/v1/auth/register",
        json={"email": unique_email, "password": PASSWORD},
    )
    assert reg.status_code == 201
    reg_data = reg.json()
    assert reg_data["tenant_slug"]
    assert reg_data["user"]["role"] == "tenant_admin"

    login = await client.post(
        "/api/v1/auth/login",
        json={"email": unique_email, "password": PASSWORD},
    )
    assert login.status_code == 200
    login_data = login.json()
    assert login_data["role"] == "tenant_admin"
    assert login_data["email"] == unique_email
    access = login_data["access_token"]
    refresh = login_data["refresh_token"]

    me = await client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {access}"},
    )
    assert me.status_code == 200
    me_data = me.json()
    assert me_data["email"] == unique_email
    assert "devices.read" in me_data["permissions"]

    refreshed = await client.post("/api/v1/auth/refresh", json={"refresh_token": refresh})
    assert refreshed.status_code == 200
    assert refreshed.json()["access_token"]
