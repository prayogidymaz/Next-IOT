"""Parse JSON and NMEA telemetry packets from ESP32 LoRa gateway serial stream."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass


@dataclass(frozen=True)
class LoRaPacket:
    node_id: str
    latitude: float
    longitude: float
    altitude_m: float
    rssi: float | None = None
    snr: float | None = None
    raw: str = ""


def _parse_nmea_coordinate(value: str, hemisphere: str) -> float | None:
    if not value or not hemisphere:
        return None
    try:
        degrees = int(float(value) / 100)
        minutes = float(value) - degrees * 100
        decimal = degrees + minutes / 60.0
        if hemisphere.upper() in {"S", "W"}:
            decimal *= -1
        return decimal
    except (TypeError, ValueError):
        return None


def parse_nmea_gpgga(line: str, *, default_node_id: str) -> LoRaPacket | None:
    """Parse `$GPGGA` sentence; optional prefix `NODE_ID,$GPGGA,...`."""
    stripped = line.strip()
    if not stripped:
        return None

    node_id = default_node_id
    sentence = stripped
    if "," in stripped and not stripped.startswith("$"):
        prefix, remainder = stripped.split(",", 1)
        if remainder.startswith("$"):
            node_id = prefix.strip() or default_node_id
            sentence = remainder.strip()

    if not sentence.startswith("$GPGGA"):
        return None

    parts = sentence.split(",")
    if len(parts) < 10:
        return None

    lat = _parse_nmea_coordinate(parts[2], parts[3])
    lon = _parse_nmea_coordinate(parts[4], parts[5])
    if lat is None or lon is None:
        return None

    try:
        altitude_m = float(parts[9]) if parts[9] else 0.0
    except ValueError:
        altitude_m = 0.0

    return LoRaPacket(
        node_id=node_id,
        latitude=lat,
        longitude=lon,
        altitude_m=altitude_m,
        raw=stripped,
    )


def parse_json_packet(line: str) -> LoRaPacket | None:
    stripped = line.strip()
    if not stripped.startswith("{"):
        return None

    try:
        payload = json.loads(stripped)
    except json.JSONDecodeError:
        return None

    if not isinstance(payload, dict):
        return None

    node_id = str(payload.get("node_id") or payload.get("device_id") or "").strip()
    if not node_id:
        return None

    lat = payload.get("lat", payload.get("latitude"))
    lon = payload.get("lon", payload.get("longitude"))
    if lat is None or lon is None:
        return None

    alt = payload.get("alt", payload.get("altitude_m", 0.0))
    rssi = payload.get("rssi")
    snr = payload.get("snr")

    return LoRaPacket(
        node_id=node_id,
        latitude=float(lat),
        longitude=float(lon),
        altitude_m=float(alt),
        rssi=float(rssi) if rssi is not None else None,
        snr=float(snr) if snr is not None else None,
        raw=stripped,
    )


def parse_serial_line(line: str, *, default_node_id: str = "DRONE-01") -> LoRaPacket | None:
    """Parse one serial line as JSON or NMEA GPGGA."""
    stripped = line.strip()
    if not stripped or stripped.startswith("#"):
        return None

    packet = parse_json_packet(stripped)
    if packet is not None:
        return packet

    return parse_nmea_gpgga(stripped, default_node_id=default_node_id)


def packet_to_metrics(packet: LoRaPacket) -> dict[str, float | int]:
    """Numeric telemetry metrics accepted by `/api/v1/telemetry`."""
    metrics: dict[str, float | int] = {
        "latitude": round(packet.latitude, 6),
        "longitude": round(packet.longitude, 6),
        "altitude_m": round(packet.altitude_m, 1),
    }
    if packet.rssi is not None:
        metrics["rssi"] = round(packet.rssi, 1)
    if packet.snr is not None:
        metrics["snr"] = round(packet.snr, 1)
    return metrics


def normalize_serial_line(raw: bytes | str) -> str:
    if isinstance(raw, bytes):
        text = raw.decode("utf-8", errors="ignore")
    else:
        text = raw
    return re.sub(r"[\r\n]+$", "", text.strip())
