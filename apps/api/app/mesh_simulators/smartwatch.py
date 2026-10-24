"""Smartwatch / wear UI companion simulator."""

from __future__ import annotations

from app.mesh.event_bus import MeshDomain, mesh_tenant_fanout_channel
from app.mesh_simulators.base import MeshPublisher, SimulatorEnv
from pydantic import JsonValue


class SmartwatchSimulator:
    def __init__(self) -> None:
        self.last_alert_id: str | None = None

    async def on_mesh_fanout(self, publisher: MeshPublisher, payload: dict[str, JsonValue]) -> None:
        domain = str(payload.get("domain", ""))
        event_type = str(payload.get("event_type", ""))
        if domain == MeshDomain.UI.value and event_type in {"alert_shown", "user_action_triggered"}:
            self.last_alert_id = str(payload.get("event_id", ""))
            await publisher.publish_mesh(
                MeshDomain.UI,
                "alert_shown",
                {"forwarded_from_mesh": True, "source_event": event_type},
            )

    async def simulate_tap(self, publisher: MeshPublisher, action: str, alert_id: str | None) -> None:
        if action == "acknowledge":
            await publisher.publish_mesh(
                MeshDomain.UI,
                "user_acknowledged",
                {"alert_id": alert_id or self.last_alert_id or "unknown"},
            )
            return
        await publisher.publish_mesh(
            MeshDomain.UI,
            "user_action_triggered",
            {"action": action, "device": "smartwatch"},
        )

    async def handle_command(self, command_type: str, params: dict[str, JsonValue]) -> dict[str, JsonValue]:
        value = str(params.get("value", ""))
        if command_type == "SET_ACTUATOR" and value == "display_alert":
            return {"vibrate": True, "message": str(params.get("message", ""))}
        if value == "vibrate_haptic":
            return {"vibrated": True}
        return {"ok": True}


def mesh_fanout_channel_for(env: SimulatorEnv) -> str:
    return mesh_tenant_fanout_channel(str(env.tenant_id))
