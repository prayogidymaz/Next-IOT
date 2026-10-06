import uuid

import pytest
from httpx import AsyncClient

PASSWORD = "SecurePass123!"


async def _register_tenant(client: AsyncClient, slug: str, email: str) -> dict:
    resp = await client.post(
        "/auth/register",
        json={
            "tenant_name": f"Tenant {slug}",
            "tenant_slug": slug,
            "email": email,
            "password": PASSWORD,
        },
    )
    assert resp.status_code == 201
    return resp.json()


def _auth(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


def _device_basic(client_id: str, client_secret: str) -> dict:
    return httpx_basic_auth(client_id, client_secret)


def httpx_basic_auth(username: str, password: str) -> dict:
    import base64

    creds = base64.b64encode(f"{username}:{password}".encode()).decode()
    return {"Authorization": f"Basic {creds}"}


@pytest.mark.asyncio
async def test_register_and_provision_device_happy_path(
    client: AsyncClient, unique_slug: str, unique_email: str
):
    reg = await _register_tenant(client, unique_slug, unique_email)
    token = reg["tokens"]["access_token"]

    create = await client.post(
        "/api/v1/devices",
        headers=_auth(token),
        json={
            "name": "Sensor Node 01",
            "device_type": "temperature_sensor",
            "metadata": {"location": "warehouse-a", "firmware": "1.0.0"},
        },
    )
    assert create.status_code == 201
    body = create.json()
    assert body["device"]["status"] == "pending"
    assert body["device"]["tenant_id"] == reg["tenant_id"]
    assert body["provisioning_token"].startswith("prov_")
    assert len(body["device"]["metadata"]) == 2

    device_id = body["device"]["id"]
    prov_token = body["provisioning_token"]

    provision = await client.post(
        f"/api/v1/devices/{device_id}/provision",
        json={"provisioning_token": prov_token},
    )
    assert provision.status_code == 200
    creds = provision.json()
    assert creds["status"] == "provisioned"
    assert creds["client_id"].startswith("dev_")
    assert len(creds["client_secret"]) > 20

    # Provisioning token is one-time
    replay = await client.post(
        f"/api/v1/devices/{device_id}/provision",
        json={"provisioning_token": prov_token},
    )
    assert replay.status_code == 401

    detail = await client.get(f"/api/v1/devices/{device_id}", headers=_auth(token))
    assert detail.status_code == 200
    assert detail.json()["status"] == "provisioned"

    auth_check = await client.get(
        f"/api/v1/devices/{device_id}/auth-check",
        headers=_device_basic(creds["client_id"], creds["client_secret"]),
    )
    assert auth_check.status_code == 200
    assert auth_check.json()["device_id"] == device_id


@pytest.mark.asyncio
async def test_list_devices_scoped_to_tenant(client: AsyncClient):
    slug_a = f"ta-{uuid.uuid4().hex[:6]}"
    slug_b = f"tb-{uuid.uuid4().hex[:6]}"
    email_a = f"a-{uuid.uuid4().hex[:6]}@example.com"
    email_b = f"b-{uuid.uuid4().hex[:6]}@example.com"

    reg_a = await _register_tenant(client, slug_a, email_a)
    reg_b = await _register_tenant(client, slug_b, email_b)
    token_a = reg_a["tokens"]["access_token"]
    token_b = reg_b["tokens"]["access_token"]

    await client.post(
        "/api/v1/devices",
        headers=_auth(token_a),
        json={"name": "Device A1", "device_type": "gateway"},
    )
    await client.post(
        "/api/v1/devices",
        headers=_auth(token_b),
        json={"name": "Device B1", "device_type": "gateway"},
    )

    list_a = await client.get("/api/v1/devices", headers=_auth(token_a))
    assert list_a.status_code == 200
    assert len(list_a.json()) == 1
    assert list_a.json()[0]["name"] == "Device A1"

    list_b = await client.get("/api/v1/devices", headers=_auth(token_b))
    assert len(list_b.json()) == 1
    assert list_b.json()[0]["name"] == "Device B1"


@pytest.mark.asyncio
async def test_tenant_isolation_get_device_denied(client: AsyncClient):
    slug_a = f"ta-{uuid.uuid4().hex[:6]}"
    slug_b = f"tb-{uuid.uuid4().hex[:6]}"
    email_a = f"a-{uuid.uuid4().hex[:6]}@example.com"
    email_b = f"b-{uuid.uuid4().hex[:6]}@example.com"

    reg_a = await _register_tenant(client, slug_a, email_a)
    reg_b = await _register_tenant(client, slug_b, email_b)
    token_a = reg_a["tokens"]["access_token"]

    create_b = await client.post(
        "/api/v1/devices",
        headers=_auth(reg_b["tokens"]["access_token"]),
        json={"name": "Secret Device", "device_type": "camera"},
    )
    device_b_id = create_b.json()["device"]["id"]

    denied = await client.get(f"/api/v1/devices/{device_b_id}", headers=_auth(token_a))
    assert denied.status_code == 404


@pytest.mark.asyncio
async def test_viewer_can_list_but_not_register(client: AsyncClient, unique_slug: str, unique_email: str):
    from app.auth.security import hash_password
    from app.database import async_session
    from app.models.user import User

    reg = await _register_tenant(client, unique_slug, unique_email)
    tenant_id = uuid.UUID(reg["tenant_id"])
    viewer_email = f"viewer-{uuid.uuid4().hex[:6]}@example.com"

    async with async_session() as session:
        session.add(
            User(
                tenant_id=tenant_id,
                email=viewer_email,
                password_hash=hash_password(PASSWORD),
                role="viewer",
            )
        )
        await session.commit()

    login = await client.post("/auth/login", json={"email": viewer_email, "password": PASSWORD})
    viewer_token = login.json()["access_token"]

    denied = await client.post(
        "/api/v1/devices",
        headers=_auth(viewer_token),
        json={"name": "X", "device_type": "sensor"},
    )
    assert denied.status_code == 403

    allowed = await client.get("/api/v1/devices", headers=_auth(viewer_token))
    assert allowed.status_code == 200


@pytest.mark.asyncio
async def test_invalid_device_credentials_rejected(
    client: AsyncClient, unique_slug: str, unique_email: str
):
    reg = await _register_tenant(client, unique_slug, unique_email)
    token = reg["tokens"]["access_token"]

    create = await client.post(
        "/api/v1/devices",
        headers=_auth(token),
        json={"name": "Node", "device_type": "sensor"},
    )
    device_id = create.json()["device"]["id"]

    resp = await client.get(
        f"/api/v1/devices/{device_id}/auth-check",
        headers=_device_basic("dev_invalid", "wrong-secret"),
    )
    assert resp.status_code == 401
