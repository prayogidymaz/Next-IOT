"""CCTV / vision domain mesh simulator."""

from __future__ import annotations

import os
import random
import uuid

from app.mesh.event_bus import MeshDomain
from app.mesh_simulators.base import MeshPublisher, SimulatorEnv
from pydantic import JsonValue


class CctvSimulator:
    def __init__(self, env: SimulatorEnv) -> None:
        self._env = env
        self._motion_probability = float(os.environ.get("CCTV_PROBABILITY_MOTION", "0.05"))

    async def publish_image_captured(self, publisher: MeshPublisher) -> uuid.UUID:
        return await publisher.publish_mesh(
            MeshDomain.VISION,
            "image_captured",
            {"image_url": "https://example.invalid/sim/cctv-placeholder.jpg", "format": "jpeg"},
        )

    async def publish_motion_detected(self, publisher: MeshPublisher, confidence: float) -> uuid.UUID:
        return await publisher.publish_mesh(
            MeshDomain.VISION,
            "motion_detected",
            {"confidence": confidence, "class": "motion"},
            context={"physical_zone": os.environ.get("PHYSICAL_ZONE", "plot_A")},
        )

    async def maybe_publish_motion(self, publisher: MeshPublisher) -> uuid.UUID | None:
        if random.random() > self._motion_probability:
            return None
        return await self.publish_motion_detected(publisher, confidence=round(random.uniform(0.75, 0.98), 2))

    async def publish_anomaly(self, publisher: MeshPublisher, label: str) -> uuid.UUID:
        return await publisher.publish_mesh(
            MeshDomain.VISION,
            "anomaly_detected",
            {"label": label, "confidence": 0.9},
        )

    async def handle_command(self, command_type: str, params: dict[str, JsonValue]) -> dict[str, JsonValue]:
        if command_type in {"SET_ACTUATOR", "capture_image"}:
            return {"image_url": "https://example.invalid/sim/capture.jpg", "params": params}
        return {"ok": True}


async def run_tick(publisher: MeshPublisher, sim: CctvSimulator) -> None:
    await sim.publish_image_captured(publisher)
    await sim.maybe_publish_motion(publisher)
