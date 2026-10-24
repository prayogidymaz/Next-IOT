"""Cyberdeck / UI domain mesh simulator."""

from __future__ import annotations

from app.mesh.event_bus import MeshDomain
from app.mesh_simulators.base import MeshPublisher
from pydantic import JsonValue


class CyberdeckSimulator:
    def __init__(self) -> None:
        self.current_screen = "dashboard"
        self.battery_percent = 92.0
        self.signal_strength = -67

    async def publish_alert_shown(self, publisher: MeshPublisher, message: str) -> None:
        await publisher.publish_mesh(
            MeshDomain.UI,
            "alert_shown",
            {"message": message, "screen": self.current_screen},
        )

    async def simulate_user_action(self, publisher: MeshPublisher, action: str) -> None:
        await publisher.publish_mesh(
            MeshDomain.UI,
            "user_action_triggered",
            {"action": action, "screen": self.current_screen},
        )

    async def simulate_acknowledge(self, publisher: MeshPublisher, alert_id: str) -> None:
        await publisher.publish_mesh(
            MeshDomain.UI,
            "user_acknowledged",
            {"alert_id": alert_id},
        )

    async def handle_command(
        self,
        publisher: MeshPublisher,
        command_type: str,
        params: dict[str, JsonValue],
    ) -> dict[str, JsonValue]:
        value = str(params.get("value", ""))
        if command_type == "SET_ACTUATOR" and value == "display_message":
            message = str(params.get("message", "alert"))
            await self.publish_alert_shown(publisher, message)
            return {"displayed": message}
        if command_type == "SET_ACTUATOR" and value == "update_dashboard":
            self.current_screen = str(params.get("screen", "dashboard"))
            return {"screen": self.current_screen}
        return {"ignored": command_type}
