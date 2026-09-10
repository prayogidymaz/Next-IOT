import uuid

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_register_login_refresh_logout_happy_path(
    client: AsyncClient, unique_email: str, unique_slug: str
):
    register_payload = {
        "tenant_name": "Acme IoT",
        "tenant_slug": unique_slug,
        "email": unique_email,
        "password": "SecurePass123!",
    }

    reg = await client.post("/auth/register", json=register_payload)
    assert reg.status_code == 201
    reg_data = reg.json()
    assert reg_data["tenant_slug"] == unique_slug
    assert reg_data["user"]["email"] == unique_email
    assert reg_data["user"]["tenant_id"] == reg_data["tenant_id"]
    assert "access_token" in reg_data["tokens"]
    assert "refresh_token" in reg_data["tokens"]

    login = await client.post(
        "/auth/login",
        json={"email": unique_email, "password": "SecurePass123!"},
    )
    assert login.status_code == 200
    tokens = login.json()
    access_token = tokens["access_token"]
    refresh_token = tokens["refresh_token"]

    refresh = await client.post("/auth/refresh", json={"refresh_token": refresh_token})
    assert refresh.status_code == 200
    new_tokens = refresh.json()
    assert new_tokens["refresh_token"] != refresh_token
    assert new_tokens["access_token"]
    assert new_tokens["token_type"] == "bearer"

    logout = await client.post("/auth/logout", json={"refresh_token": new_tokens["refresh_token"]})
    assert logout.status_code == 200

    refresh_after_logout = await client.post(
        "/auth/refresh", json={"refresh_token": new_tokens["refresh_token"]}
    )
    assert refresh_after_logout.status_code == 401


@pytest.mark.asyncio
async def test_login_invalid_credentials(client: AsyncClient, unique_email: str, unique_slug: str):
    await client.post(
        "/auth/register",
        json={
            "tenant_name": "Test Co",
            "tenant_slug": unique_slug,
            "email": unique_email,
            "password": "SecurePass123!",
        },
    )

    wrong_password = await client.post(
        "/auth/login",
        json={"email": unique_email, "password": "WrongPassword!"},
    )
    assert wrong_password.status_code == 401

    unknown_user = await client.post(
        "/auth/login",
        json={"email": f"unknown-{uuid.uuid4().hex}@example.com", "password": "SecurePass123!"},
    )
    assert unknown_user.status_code == 401


@pytest.mark.asyncio
async def test_register_duplicate_email(client: AsyncClient, unique_email: str, unique_slug: str):
    payload = {
        "tenant_name": "First Tenant",
        "tenant_slug": unique_slug,
        "email": unique_email,
        "password": "SecurePass123!",
    }
    first = await client.post("/auth/register", json=payload)
    assert first.status_code == 201

    second = await client.post(
        "/auth/register",
        json={
            "tenant_name": "Second Tenant",
            "tenant_slug": f"{unique_slug}-2",
            "email": unique_email,
            "password": "SecurePass123!",
        },
    )
    assert second.status_code == 409
