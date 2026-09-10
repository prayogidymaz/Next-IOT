"""USB Serial LoRa gateway bridge — forwards ESP32 packets to telemetry API & Redis."""

from __future__ import annotations

import asyncio
import base64
import logging
import uuid
from datetime import UTC, datetime
from typing import Any

import httpx
import redis.asyncio as aioredis
from sqlalchemy import select
from app.config import settings
from app.database import async_session
from app.devices.liveness import touch_liveness
from app.devices.state_machine import should_emit_online
from app.devices.events import emit_device_event
from app.hardware.events import get_gateway_status, publish_lora_telemetry, update_gateway_status
from app.hardware.parser import LoRaPacket, normalize_serial_line, packet_to_metrics, parse_serial_line
from app.models.device import Device, DeviceStatus
from app.models.device_credential import DeviceCredential
from app.models.device_metadata import DeviceMetadata

logger = logging.getLogger(__name__)


class LoRaBridge:
    def __init__(
        self,
        redis: aioredis.Redis,
        *,
        serial_port: str | None = None,
        baud_rate: int | None = None,
        api_base_url: str | None = None,
    ) -> None:
        self.redis = redis
        self.serial_port = serial_port or settings.lora_bridge_serial_port
        self.baud_rate = baud_rate or settings.lora_bridge_baud_rate
        self.api_base_url = (api_base_url or settings.lora_bridge_api_base_url).rstrip("/")
        self._packets_received = 0
        self._serial_connected = False
        self._last_packet_at: datetime | None = None
        self._last_node_id: str | None = None
        self._last_rssi: float | None = None
        self._last_snr: float | None = None

    async def run_forever(self) -> None:
        await self._publish_status(serial_connected=False, lora_link="starting")
        while True:
            try:
                await self._run_serial_loop()
            except asyncio.CancelledError:
                raise
            except Exception:
                logger.exception("LoRa bridge serial loop crashed; retrying in 3s")
                await self._publish_status(serial_connected=False, lora_link="error")
                await asyncio.sleep(3)

    async def _run_serial_loop(self) -> None:
        try:
            import serial
        except ImportError as exc:
            raise RuntimeError("pyserial is required for LoRa bridge") from exc

        logger.info("Opening serial port %s @ %d baud", self.serial_port, self.baud_rate)
        with serial.Serial(self.serial_port, self.baud_rate, timeout=1) as port:
            self._serial_connected = True
            await self._publish_status(serial_connected=True, lora_link="connected")
            while True:
                raw = await asyncio.to_thread(port.readline)
                if not raw:
                    await asyncio.sleep(0.05)
                    continue
                line = normalize_serial_line(raw)
                packet = parse_serial_line(line, default_node_id=settings.lora_bridge_default_node_id)
                if packet is None:
                    continue
                await self.process_packet(packet)

    async def process_packet(self, packet: LoRaPacket) -> None:
        self._packets_received += 1
        self._last_packet_at = datetime.now(UTC)
        self._last_node_id = packet.node_id
        self._last_rssi = packet.rssi
        self._last_snr = packet.snr

        device_ctx = await self._resolve_device(packet.node_id)
        metrics = packet_to_metrics(packet)
        recorded_at = datetime.now(UTC).isoformat()

        event_payload = {
            "node_id": packet.node_id,
            "device_id": str(device_ctx["device_id"]) if device_ctx else None,
            "latitude": packet.latitude,
            "longitude": packet.longitude,
            "altitude_m": packet.altitude_m,
            "rssi": packet.rssi,
            "snr": packet.snr,
            "recorded_at": recorded_at,
            "source": "lora_bridge",
        }
        await publish_lora_telemetry(self.redis, event_payload)

        if device_ctx is None:
            logger.warning("No device mapped for LoRa node_id=%s", packet.node_id)
            await self._publish_status(serial_connected=self._serial_connected, lora_link="connected")
            return

        await self._ensure_device_online(device_ctx["device_id"])
        await self._forward_to_api(
            client_id=device_ctx["client_id"],
            client_secret=device_ctx["client_secret"],
            metrics=metrics,
        )
        await self._publish_status(serial_connected=self._serial_connected, lora_link="connected")

    async def _resolve_device(self, node_id: str) -> dict[str, Any] | None:
        async with async_session() as db:
            meta = await db.scalar(
                select(DeviceMetadata)
                .where(DeviceMetadata.key == "lora_node_id", DeviceMetadata.value == node_id)
                .limit(1)
            )
            device: Device | None = None
            if meta is not None:
                device = await db.get(Device, meta.device_id)
            if device is None:
                device = await db.scalar(select(Device).where(Device.name.ilike(node_id)))
            if device is None and node_id == settings.lora_bridge_default_node_id:
                device = await db.scalar(
                    select(Device).where(Device.name == settings.lora_bridge_demo_device_name)
                )
            if device is None:
                return None

            cred = await db.scalar(
                select(DeviceCredential)
                .where(DeviceCredential.device_id == device.id)
                .order_by(DeviceCredential.issued_at.desc())
            )
            if cred is None:
                logger.warning("Device %s has no credentials for LoRa ingest", device.id)
                return None

            from app.devices.security import verify_device_secret

            # Credentials are hashed; bridge needs plaintext secret from env mapping or metadata.
            secret = await self._lookup_device_secret(db, device.id)
            if secret is None:
                return None

            return {
                "device_id": device.id,
                "client_id": cred.client_id,
                "client_secret": secret,
            }

    async def _lookup_device_secret(self, db, device_id: uuid.UUID) -> str | None:
        entry = await db.scalar(
            select(DeviceMetadata).where(
                DeviceMetadata.device_id == device_id,
                DeviceMetadata.key == "lora_bridge_client_secret",
            )
        )
        if entry is not None and entry.value:
            return entry.value

        if settings.lora_bridge_default_client_id and settings.lora_bridge_default_client_secret:
            cred = await db.scalar(
                select(DeviceCredential).where(
                    DeviceCredential.device_id == device_id,
                    DeviceCredential.client_id == settings.lora_bridge_default_client_id,
                )
            )
            if cred is not None and verify_device_secret(
                settings.lora_bridge_default_client_secret, cred.secret_hash
            ):
                return settings.lora_bridge_default_client_secret
        return None

    async def _ensure_device_online(self, device_id: uuid.UUID) -> None:
        async with async_session() as db:
            device = await db.get(Device, device_id)
            if device is None:
                return
            previous = device.status
            now = datetime.now(UTC)
            device.status = DeviceStatus.ONLINE
            device.last_seen_at = now
            await touch_liveness(self.redis, str(device.id))
            if should_emit_online(previous, device.status):
                await emit_device_event(
                    self.redis,
                    "device.online",
                    device_id=str(device.id),
                    tenant_id=str(device.tenant_id),
                    extra={"previous_status": previous, "source": "lora_bridge"},
                )
            await db.commit()

    async def _forward_to_api(self, *, client_id: str, client_secret: str, metrics: dict[str, Any]) -> None:
        payload = {
            "timestamp": datetime.now(UTC).isoformat(),
            "metrics": metrics,
        }
        token = base64.b64encode(f"{client_id}:{client_secret}".encode()).decode()
        headers = {"Authorization": f"Basic {token}"}

        async with httpx.AsyncClient(base_url=self.api_base_url, timeout=10.0) as client:
            response = await client.post("/api/v1/telemetry", json=payload, headers=headers)
            if response.status_code >= 400:
                logger.warning(
                    "Telemetry ingest failed (%s): %s",
                    response.status_code,
                    response.text[:200],
                )

    async def _publish_status(self, *, serial_connected: bool, lora_link: str) -> None:
        await update_gateway_status(
            self.redis,
            {
                "serial_connected": serial_connected,
                "serial_port": self.serial_port,
                "lora_link": lora_link,
                "last_packet_at": self._last_packet_at.isoformat() if self._last_packet_at else None,
                "node_id": self._last_node_id,
                "rssi": self._last_rssi,
                "snr": self._last_snr,
                "packets_received": self._packets_received,
            },
        )


async def read_gateway_status(redis: aioredis.Redis) -> dict[str, Any]:
    status = await get_gateway_status(redis)
    if status is None:
        return {
            "serial_connected": False,
            "serial_port": settings.lora_bridge_serial_port,
            "lora_link": "disconnected",
            "packets_received": 0,
        }
    return status
