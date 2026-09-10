import httpx

from app.config import settings
from app.tiles.placeholder import TACTICAL_PLACEHOLDER_PNG


async def fetch_tile_png(z: int, x: int, y: int) -> tuple[bytes, str, int]:
    """Proxy tile from MBTiles server; return placeholder PNG on miss."""
    service = settings.tile_server_service
    url = f"{settings.tile_server_url.rstrip('/')}/services/{service}/tiles/{z}/{x}/{y}.png"

    try:
        async with httpx.AsyncClient(timeout=settings.tile_proxy_timeout_seconds) as client:
            response = await client.get(url)
            if response.status_code == 200 and response.content:
                return response.content, "tile-server", response.status_code
    except httpx.HTTPError:
        pass

    return TACTICAL_PLACEHOLDER_PNG, "placeholder", 200
