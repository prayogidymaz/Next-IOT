import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_cors_preflight_allows_ephemeral_flutter_web_port(client: AsyncClient):
    response = await client.options(
        "/auth/login",
        headers={
            "Origin": "http://localhost:55921",
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "content-type,authorization",
        },
    )
    assert response.status_code == 200
    assert response.headers.get("access-control-allow-origin") == "http://localhost:55921"


@pytest.mark.asyncio
async def test_cors_preflight_allows_flutter_web_origin(client: AsyncClient):
    response = await client.options(
        "/auth/login",
        headers={
            "Origin": "http://localhost:54321",
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "content-type,authorization",
        },
    )
    assert response.status_code == 200
    allow_origin = response.headers.get("access-control-allow-origin")
    assert allow_origin in {"*", "http://localhost:54321"}
    assert "POST" in (response.headers.get("access-control-allow-methods") or "")


@pytest.mark.asyncio
async def test_cors_allows_json_login_from_browser_origin(client: AsyncClient, unique_email: str, unique_slug: str):
    await client.post(
        "/auth/register",
        json={
            "tenant_name": "CORS Tenant",
            "tenant_slug": unique_slug,
            "email": unique_email,
            "password": "SecurePass123!",
        },
    )

    response = await client.post(
        "/auth/login",
        json={"email": unique_email, "password": "SecurePass123!"},
        headers={"Origin": "http://localhost:54321"},
    )
    assert response.status_code == 200
    allow_origin = response.headers.get("access-control-allow-origin")
    assert allow_origin in {"*", "http://localhost:54321"}
    assert "access_token" in response.json()
