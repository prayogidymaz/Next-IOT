"""Gate / security domain mesh simulator."""

from __future__ import annotations

from app.mesh.event_bus import MeshDomain
from app.mesh_simulators.base import MeshPublisher
from pydantic import JsonValue


class GateSimulator:
    def __init__(self) -> None:
        self.locked = True
        self.proximity_detected = False

    async def handle_lock(self, publisher: MeshPublisher) -> None:
        self.locked = True
        await publisher.publish_mesh(MeshDomain.SECURITY, "lock_engaged", {"locked": True})

    async def handle_unlock(self, publisher: MeshPublisher) -> None:
        self.locked = False
        await publisher.publish_mesh(MeshDomain.SECURITY, "access_granted", {"locked": False})

    async def simulate_intrusion(self, publisher: MeshPublisher) -> None:
        self.proximity_detected = True
        await publisher.publish_mesh(
            MeshDomain.SECURITY,
            "intrusion_detected",
            {"proximity": True, "zone": "perimeter"},
        )

    async def handle_command(
        self,
        publisher: MeshPublisher,
        command_type: str,
        params: dict[str, JsonValue],
    ) -> dict[str, JsonValue]:
        value = str(params.get("value", ""))
        if command_type == "SET_ACTUATOR" and value == "lock":
            await self.handle_lock(publisher)
            return {"locked": True}
        if command_type == "SET_ACTUATOR" and value == "unlock":
            await self.handle_unlock(publisher)
            return {"locked": False}
        if command_type == "SET_ACTUATOR" and value == "trigger_alarm":
            await self.simulate_intrusion(publisher)
            return {"alarm": True}
        return {"ignored": command_type}
