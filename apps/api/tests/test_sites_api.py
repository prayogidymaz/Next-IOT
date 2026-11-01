"""Sites API — run manually after migration 048."""

import pytest
from httpx import AsyncClient

pytestmark = pytest.mark.skip(reason="Scaffold: enable after alembic upgrade head")


@pytest.mark.asyncio
async def test_list_sites_requires_auth(client: AsyncClient) -> None:
    resp = await client.get("/api/v1/sites")
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_create_site_happy_path(client: AsyncClient) -> None:
    """TODO: register tenant, POST /api/v1/sites, assert 201."""
    assert True


@pytest.mark.asyncio
async def test_site_tenant_isolation(client: AsyncClient) -> None:
    """TODO: tenant B cannot GET tenant A site."""
    assert True
