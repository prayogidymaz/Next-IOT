from fastapi import APIRouter, Response

from app.tiles.service import fetch_tile_png

router = APIRouter(prefix="/api/v1", tags=["tiles"])


@router.get("/tiles/{z}/{x}/{y}.png")
async def get_offline_map_tile(z: int, x: int, y: int):
    """Serve map tiles from local MBTiles server with tactical placeholder fallback."""
    content, _source, status_code = await fetch_tile_png(z, x, y)
    return Response(
        content=content,
        media_type="image/png",
        headers={"Cache-Control": "public, max-age=86400"},
        status_code=status_code,
    )
