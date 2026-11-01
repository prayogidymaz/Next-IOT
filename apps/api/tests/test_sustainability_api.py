"""Sustainability API — run manually after migration 049."""

import pytest
from httpx import AsyncClient

pytestmark = pytest.mark.skip(reason="Scaffold: enable after alembic upgrade head")


@pytest.mark.asyncio
async def test_carbon_list_unauthorized(client: AsyncClient) -> None:
    resp = await client.get("/api/v1/sustainability/carbon")
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_esg_generate_happy_path(client: AsyncClient) -> None:
    """TODO: seed carbon/water rows, POST generate?month=2026-01."""
    assert True
