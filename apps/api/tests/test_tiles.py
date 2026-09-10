import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_tile_proxy_returns_png(client: AsyncClient):
    resp = await client.get("/api/v1/tiles/10/512/512.png")
    assert resp.status_code == 200
    assert resp.headers["content-type"] == "image/png"
    assert resp.content.startswith(b"\x89PNG")


@pytest.mark.asyncio
async def test_tile_proxy_sets_cache_header(client: AsyncClient):
    resp = await client.get("/api/v1/tiles/8/200/150.png")
    assert resp.status_code == 200
    assert "cache-control" in resp.headers
