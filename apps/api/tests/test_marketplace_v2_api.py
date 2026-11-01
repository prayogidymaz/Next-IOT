"""Marketplace v2 — run manually after migration 051."""

import pytest
from httpx import AsyncClient

pytestmark = pytest.mark.skip(reason="Scaffold: enable after alembic upgrade head")


@pytest.mark.asyncio
async def test_paid_download_requires_purchase(client: AsyncClient) -> None:
    """TODO: publish paid template, download without checkout → 402."""
    assert True


@pytest.mark.asyncio
async def test_seller_dashboard(client: AsyncClient) -> None:
    """TODO: GET /api/v1/marketplace/seller/dashboard."""
    assert True
