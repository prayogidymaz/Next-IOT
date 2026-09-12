"""MAVLink 2.0 protocol bridge — Pixhawk / ArduPilot compatibility layer."""

from __future__ import annotations

import base64
import math
from dataclasses import dataclass, field
from typing import Any

from pymavlink.dialects.v20 import common as mavlink

from app.mavlink.constants import (
    MAVLINK_PROTOCOL_VERSION,
    MavlinkCommandType,
    SUPPORTED_INBOUND_TYPES,
)
from app.mavlink.schemas import MavlinkTelemetrySnapshot

_AUTOPILOT_NAMES = {
    mavlink.MAV_AUTOPILOT_ARDUPILOTMEGA: "ArduPilot",
    mavlink.MAV_AUTOPILOT_PX4: "PX4",
    mavlink.MAV_AUTOPILOT_GENERIC: "Generic",
}

_VEHICLE_NAMES = {
    mavlink.MAV_TYPE_QUADROTOR: "Quadrotor",
    mavlink.MAV_TYPE_FIXED_WING: "FixedWing",
    mavlink.MAV_TYPE_GROUND_ROVER: "GroundRover",
}


@dataclass
class MavlinkBridgeService:
    """Decode MAVLink UDP/serial streams and encode Next-IOT flight commands."""

    src_system: int = 255
    src_component: int = 190
    _buffer: bytearray = field(default_factory=bytearray)
    _snapshot: MavlinkTelemetrySnapshot = field(default_factory=MavlinkTelemetrySnapshot)

    def __post_init__(self) -> None:
        self._mav = mavlink.MAVLink(None, srcSystem=self.src_system, srcComponent=self.src_component)

    @property
    def snapshot(self) -> MavlinkTelemetrySnapshot:
        return self._snapshot

    def reset(self) -> None:
        self._buffer.clear()
        self._snapshot = MavlinkTelemetrySnapshot()

    def feed_bytes(self, chunk: bytes) -> tuple[list[str], MavlinkTelemetrySnapshot]:
        """Append bytes from UDP/serial stream; return parsed message types."""
        self._buffer.extend(chunk)
        parsed_types: list[str] = []

        while self._buffer:
            msg = self._mav.parse_char(bytes([self._buffer[0]]))
            del self._buffer[0]
            if msg is None:
                continue
            msg_type = msg.get_type()
            if msg_type not in SUPPORTED_INBOUND_TYPES:
                continue
            parsed_types.append(msg_type)
            self._apply_message(msg)

        return parsed_types, self._snapshot

    def decode_packet(self, packet: bytes) -> tuple[list[str], MavlinkTelemetrySnapshot]:
        saved_buffer = bytes(self._buffer)
        saved_snapshot = self._snapshot
        self.reset()
        types, snapshot = self.feed_bytes(packet)
        if not types:
            self._buffer = bytearray(saved_buffer)
            self._snapshot = saved_snapshot
        return types, snapshot

    def to_internal_metrics(self) -> dict[str, float | int]:
        metrics = dict(self._snapshot.metrics)
        metrics["mavlink_connected"] = 1 if self._snapshot.mavlink_connected else 0
        metrics["mavlink_protocol"] = MAVLINK_PROTOCOL_VERSION
        return metrics

    def encode_command(
        self,
        command: str | MavlinkCommandType,
        *,
        target_system: int = 1,
        target_component: int = 1,
        params: dict[str, Any] | None = None,
    ) -> bytes:
        params = params or {}
        command_value = MavlinkCommandType(str(command).upper())

        if command_value == MavlinkCommandType.ARM:
            msg = self._encode_arm(target_system, target_component, arm=True)
        elif command_value == MavlinkCommandType.DISARM:
            msg = self._encode_arm(target_system, target_component, arm=False)
        elif command_value == MavlinkCommandType.RTL:
            msg = self._encode_command_long(
                target_system,
                target_component,
                mavlink.MAV_CMD_NAV_RETURN_TO_LAUNCH,
            )
        elif command_value == MavlinkCommandType.LAND:
            msg = self._encode_command_long(
                target_system,
                target_component,
                mavlink.MAV_CMD_NAV_LAND,
            )
        elif command_value == MavlinkCommandType.WAYPOINT:
            lat = float(params.get("lat", params.get("latitude", 0.0)))
            lon = float(params.get("lon", params.get("longitude", 0.0)))
            alt = float(params.get("alt", params.get("altitude_m", 10.0)))
            msg = self._encode_set_position_target(target_system, target_component, lat, lon, alt)
        else:
            raise ValueError(f"Unsupported MAVLink command: {command}")

        return msg.pack(self._mav)

    def _encode_arm(self, target_system: int, target_component: int, *, arm: bool) -> mavlink.MAVLink_message:
        return self._encode_command_long(
            target_system,
            target_component,
            mavlink.MAV_CMD_COMPONENT_ARM_DISARM,
            param1=1.0 if arm else 0.0,
        )

    def _encode_command_long(
        self,
        target_system: int,
        target_component: int,
        command: int,
        *,
        param1: float = 0.0,
        param2: float = 0.0,
        param3: float = 0.0,
        param4: float = 0.0,
        param5: float = 0.0,
        param6: float = 0.0,
        param7: float = 0.0,
    ) -> mavlink.MAVLink_message:
        return self._mav.command_long_encode(
            target_system,
            target_component,
            command,
            0,
            param1,
            param2,
            param3,
            param4,
            param5,
            param6,
            param7,
        )

    def _encode_set_position_target(
        self,
        target_system: int,
        target_component: int,
        lat: float,
        lon: float,
        alt_m: float,
    ) -> mavlink.MAVLink_message:
        type_mask = 0b0000111111111000
        return self._mav.set_position_target_global_int_encode(
            0,
            target_system,
            target_component,
            mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT_INT,
            type_mask,
            int(lat * 1e7),
            int(lon * 1e7),
            alt_m,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
        )

    def _apply_message(self, msg: mavlink.MAVLink_message) -> None:
        msg_type = msg.get_type()
        metrics = dict(self._snapshot.metrics)

        if msg_type == "HEARTBEAT":
            self._snapshot.mavlink_connected = True
            self._snapshot.autopilot = _AUTOPILOT_NAMES.get(msg.autopilot, str(msg.autopilot))
            self._snapshot.vehicle_type = _VEHICLE_NAMES.get(msg.type, str(msg.type))
            metrics["system_status"] = float(msg.system_status)
            metrics["base_mode"] = float(msg.base_mode)

        elif msg_type == "GLOBAL_POSITION_INT":
            metrics["latitude"] = msg.lat / 1e7
            metrics["longitude"] = msg.lon / 1e7
            metrics["altitude_m"] = msg.alt / 1000.0
            metrics["relative_alt_m"] = msg.relative_alt / 1000.0
            metrics["speed"] = math.hypot(msg.vx, msg.vy) / 100.0

        elif msg_type == "SYS_STATUS":
            if msg.battery_remaining != 255:
                metrics["battery"] = float(msg.battery_remaining)
            if msg.voltage_battery != 65535:
                metrics["voltage"] = msg.voltage_battery / 1000.0

        elif msg_type == "ATTITUDE":
            metrics["roll"] = math.degrees(msg.roll)
            metrics["pitch"] = math.degrees(msg.pitch)
            metrics["yaw"] = math.degrees(msg.yaw)

        self._snapshot.metrics = metrics
        self._snapshot.last_message_type = msg_type
        self._snapshot.protocol_version = MAVLINK_PROTOCOL_VERSION
