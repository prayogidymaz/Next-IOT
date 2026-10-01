from app.system.health import collect_system_health
from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

router = APIRouter(prefix="/api/v1/system", tags=["system"])


@router.get("/health")
async def system_health(request: Request):
    redis = getattr(request.app.state, "redis", None)
    from app.database import engine

    payload = await collect_system_health(engine=engine, redis=redis)
    code = 200 if payload["status"] == "ready" else 503
    return JSONResponse(status_code=code, content=payload)
