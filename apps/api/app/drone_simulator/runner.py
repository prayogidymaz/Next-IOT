"""Live drone flight simulator — listens for dispatched commands via Redis Pub/Sub."""

from __future__ import annotations

import asyncio
import json
import logging
import uuid
from dataclasses import dataclass, field
from typing import Any

import redis.asyncio as aioredis
from sqlalchemy import select

from app.commands.events import DEVICE_COMMANDS_CHANNEL
from app.config import settings
from app.database import async_session
from app.drone_simulator.interpolation import GeoPoint, build_mission_path, heading_to, segment_speed_mps
from app.drone_simulator.lora_mock import build_lora_json_payload, publish_encrypted_lora_mock
from app.drone_simulator.telemetry import ensure_device_online, publish_simulated_telemetry
from app.models.device import Device
from app.seed_telemetry import DEMO_DEVICE_NAME
from app.telemetry.cache import get_latest_telemetry

logger = logging.getLogger(__name__)

SUPPORTED_COMMANDS = frozenset({"GO_TO_MISSION", "TAKEOFF", "RTL"})


@dataclass
class FlightSession:
    device_id: str
    home: GeoPoint
    battery: float = 88.0


@dataclass
class DroneSimulator:
    redis: aioredis.Redis
    tick_seconds: float = 1.0
    _sessions: dict[str, FlightSession] = field(default_factory=dict)
    _tasks: dict[str, asyncio.Task[None]] = field(default_factory=dict)

    async def run_forever(self) -> None:
        pubsub = self.redis.pubsub()
        await pubsub.subscribe(DEVICE_COMMANDS_CHANNEL)
        logger.info("Drone simulator listening on %s", DEVICE_COMMANDS_CHANNEL)

        try:
            while True:
                message = await pubsub.get_message(ignore_subscribe_messages=True, timeout=1.0)
                if message and message.get("type") == "message":
                    await self._handle_message(message["data"])
        finally:
            await pubsub.unsubscribe(DEVICE_COMMANDS_CHANNEL)
            await pubsub.aclose()

    async def _handle_message(self, raw: str) -> None:
        try:
            payload = json.loads(raw)
        except json.JSONDecodeError:
            logger.warning("Ignoring invalid command payload")
            return

        command_type = payload.get("command_type")
        if command_type not in SUPPORTED_COMMANDS:
            return

        device_id = payload.get("device_id")
        if not device_id:
            return

        params = payload.get("params") or {}
        await self._start_flight(device_id, command_type, params)

    async def _start_flight(self, device_id: str, command_type: str, params: dict[str, Any]) -> None:
        existing = self._tasks.pop(device_id, None)
        if existing and not existing.done():
            existing.cancel()
            try:
                await existing
            except asyncio.CancelledError:
                pass

        task = asyncio.create_task(self._execute_flight(device_id, command_type, params))
        self._tasks[device_id] = task

    async def _execute_flight(self, device_id: str, command_type: str, params: dict[str, Any]) -> None:
        try:
            async with async_session() as db:
                device = await self._resolve_device(db, device_id)
                if device is None:
                    logger.warning("Simulator: device %s not found", device_id)
                    return

                origin = await self._current_position(device_id)
                cruise_alt = float(params.get("altitude_m", settings.drone_simulator_default_altitude_m))
                session = FlightSession(device_id=device_id, home=origin)
                self._sessions[device_id] = session

                await ensure_device_online(db, self.redis, device)
                await db.commit()

                if command_type == "RTL":
                    path = build_mission_path(
                        origin,
                        [(session.home.latitude, session.home.longitude)],
                        cruise_altitude_m=session.home.altitude_m,
                        min_steps=settings.drone_simulator_min_steps,
                        max_steps=settings.drone_simulator_max_steps,
                    )
                    flight_mode = "rtl"
                elif command_type == "TAKEOFF":
                    takeoff_point = GeoPoint(origin.latitude, origin.longitude, cruise_alt)
                    path = build_mission_path(
                        origin,
                        [(takeoff_point.latitude, takeoff_point.longitude)],
                        cruise_altitude_m=cruise_alt,
                        min_steps=settings.drone_simulator_min_steps,
                        max_steps=settings.drone_simulator_max_steps,
                    )
                    flight_mode = "takeoff"
                else:
                    waypoints = self._parse_waypoints(params)
                    if not waypoints:
                        logger.warning("GO_TO_MISSION missing waypoints for %s", device_id)
                        return
                    path = build_mission_path(
                        origin,
                        waypoints,
                        cruise_altitude_m=cruise_alt,
                        min_steps=settings.drone_simulator_min_steps,
                        max_steps=settings.drone_simulator_max_steps,
                    )
                    flight_mode = "mission"

                prev = origin
                for point in path:
                    async with async_session() as step_db:
                        step_device = await step_db.get(Device, uuid.UUID(device_id))
                        if step_device is None:
                            return

                        speed = segment_speed_mps(prev, point, self.tick_seconds)
                        yaw = heading_to(point, prev)
                        session.battery = max(15.0, session.battery - 0.05)

                        metrics = {
                            "latitude": round(point.latitude, 6),
                            "longitude": round(point.longitude, 6),
                            "altitude_m": round(point.altitude_m, 1),
                            "battery": round(session.battery, 1),
                            "roll": round(min(12.0, speed * 0.4), 1),
                            "pitch": round(min(8.0, speed * 0.25), 1),
                            "yaw": round(yaw, 1),
                            "speed": round(speed, 2),
                            "flight_mode": flight_mode,
                        }
                        await publish_simulated_telemetry(step_db, self.redis, device=step_device, metrics=metrics)
                        await self._maybe_publish_encrypted_lora_mock(
                            node_id=settings.lora_bridge_default_node_id,
                            latitude=point.latitude,
                            longitude=point.longitude,
                            altitude_m=point.altitude_m,
                            rssi=metrics.get("rssi") if isinstance(metrics.get("rssi"), (int, float)) else -80.0,
                            snr=8.5,
                        )
                        prev = point

                    await asyncio.sleep(self.tick_seconds)

                async with async_session() as final_db:
                    final_device = await final_db.get(Device, uuid.UUID(device_id))
                    if final_device is None:
                        return

                    final_mode = "hovering" if command_type != "RTL" else "landed"
                    metrics = {
                        "latitude": round(prev.latitude, 6),
                        "longitude": round(prev.longitude, 6),
                        "altitude_m": round(prev.altitude_m, 1),
                        "battery": round(session.battery, 1),
                        "roll": 0.0,
                        "pitch": 0.0,
                        "yaw": round(heading_to(prev, session.home), 1),
                        "speed": 0.0,
                        "flight_mode": final_mode,
                    }
                    await publish_simulated_telemetry(
                        final_db,
                        self.redis,
                        device=final_device,
                        metrics=metrics,
                        flight_event="simulator.mission_complete",
                    )

                logger.info("Simulator finished %s for device %s (%s)", command_type, device.name, device_id)

        except asyncio.CancelledError:
            logger.info("Simulator flight cancelled for device %s", device_id)
            raise
        except Exception:
            logger.exception("Simulator flight failed for device %s", device_id)

    async def _resolve_device(self, db, device_id: str) -> Device | None:
        device = await db.get(Device, uuid.UUID(device_id))
        if device is not None:
            return device

        return await db.scalar(select(Device).where(Device.name == DEMO_DEVICE_NAME))

    async def _current_position(self, device_id: str) -> GeoPoint:
        cached = await get_latest_telemetry(self.redis, device_id)
        if cached:
            metrics = cached.get("metrics") or {}
            lat = metrics.get("latitude", metrics.get("lat"))
            lon = metrics.get("longitude", metrics.get("lon"))
            alt = metrics.get("altitude_m", settings.drone_simulator_default_altitude_m)
            if lat is not None and lon is not None:
                return GeoPoint(float(lat), float(lon), float(alt))

        return GeoPoint(
            settings.drone_simulator_default_latitude,
            settings.drone_simulator_default_longitude,
            28.0,
        )

    async def _maybe_publish_encrypted_lora_mock(
        self,
        *,
        node_id: str,
        latitude: float,
        longitude: float,
        altitude_m: float,
        rssi: float,
        snr: float,
    ) -> None:
        if not settings.drone_simulator_lora_encrypt_mock:
            return
        plaintext = build_lora_json_payload(
            node_id=node_id,
            latitude=latitude,
            longitude=longitude,
            altitude_m=altitude_m,
            rssi=rssi,
            snr=snr,
        )
        await publish_encrypted_lora_mock(self.redis, plaintext)

    @staticmethod
    def _parse_waypoints(params: dict[str, Any]) -> list[tuple[float, float]]:
        raw = params.get("waypoints")
        if not isinstance(raw, list):
            return []

        points: list[tuple[float, float]] = []
        for wp in raw:
            if not isinstance(wp, dict):
                continue
            lat = wp.get("lat", wp.get("latitude"))
            lon = wp.get("lon", wp.get("longitude"))
            if lat is not None and lon is not None:
                points.append((float(lat), float(lon)))
        return points
