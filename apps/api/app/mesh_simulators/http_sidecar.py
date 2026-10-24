"""Optional HTTP control plane for mesh simulators (playground triggers)."""

from __future__ import annotations

import uvicorn
from app.mesh_simulators.base import MeshPublisher, SimulatorEnv
from app.mesh_simulators.cctv import CctvSimulator
from pydantic import BaseModel, Field
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.routing import Route


class SimulateMotionBody(BaseModel):
    confidence: float = Field(default=0.9, ge=0.0, le=1.0)


def build_cctv_http_app(
    env: SimulatorEnv,
    sim: CctvSimulator,
    publisher_ref: list[MeshPublisher],
) -> Starlette:
    async def health(_request: Request) -> JSONResponse:
        return JSONResponse({"ok": True, "device_id": str(env.device_id)})

    async def simulate_motion(request: Request) -> JSONResponse:
        publisher = publisher_ref[0] if publisher_ref else None
        if publisher is None:
            return JSONResponse({"detail": "MQTT publisher not ready"}, status_code=503)
        raw = await request.body()
        confidence = 0.9
        if raw:
            try:
                body = SimulateMotionBody.model_validate_json(raw)
            except ValueError as exc:
                return JSONResponse({"detail": str(exc)}, status_code=400)
            confidence = body.confidence
        event_id = await sim.publish_motion_detected(publisher, confidence)
        return JSONResponse({"event_id": str(event_id), "event_type": "motion_detected"})

    return Starlette(
        routes=[
            Route("/health", health, methods=["GET"]),
            Route("/simulate-motion", simulate_motion, methods=["POST"]),
        ],
    )


async def serve_starlette(app: Starlette, host: str, port: int) -> None:
    config = uvicorn.Config(app, host=host, port=port, log_level="info", access_log=False)
    server = uvicorn.Server(config)
    await server.serve()


async def run_http_sidecar(env: SimulatorEnv, app: Starlette) -> None:
    await serve_starlette(app, host="0.0.0.0", port=env.http_port)
