"""Sprayer / actuator domain mesh simulator."""

from __future__ import annotations

from app.mesh.event_bus import MeshDomain
from app.mesh_simulators.base import MeshPublisher
from pydantic import JsonValue


class SprayerSimulator:
    def __init__(self) -> None:
        self.valve_open = False
        self.tank_percent = 85.0

    async def handle_command(
        self,
        publisher: MeshPublisher,
        command_type: str,
        params: dict[str, JsonValue],
    ) -> dict[str, JsonValue]:
        value = str(params.get("value", ""))
        if command_type == "SET_ACTUATOR" and value in {"open_valve", "spray", "control_valve"}:
            open_valve = params.get("open", True) is not False
            if str(params.get("action", "")).lower() == "close":
                open_valve = False
            await self._set_valve(publisher, open_valve)
            duration = params.get("duration_s") or params.get("duration_seconds")
            if open_valve and isinstance(duration, int | float):
                self._drain_tank(float(duration) / 60.0 * 2.0)
            return {"valve_open": self.valve_open, "tank_percent": self.tank_percent}
        if command_type in {"RELAY_ON", "RELAY_OFF"}:
            await self._set_valve(publisher, command_type == "RELAY_ON")
            return {"valve_open": self.valve_open}
        return {"ignored": command_type}

    async def _set_valve(self, publisher: MeshPublisher, open_valve: bool) -> None:
        self.valve_open = open_valve
        await publisher.publish_mesh(
            MeshDomain.ACTUATOR,
            "state_changed",
            {"valve_open": open_valve, "tank_level_percent": self.tank_percent},
        )
        if self.tank_percent < 20.0:
            await publisher.publish_mesh(
                MeshDomain.ACTUATOR,
                "tank_level_low",
                {"tank_level_percent": self.tank_percent},
            )

    def _drain_tank(self, liters: float) -> None:
        self.tank_percent = max(0.0, self.tank_percent - liters * 0.5)
