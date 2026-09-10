"""Encrypted LoRa serial mock payloads for simulator integration tests."""

from __future__ import annotations

import json
from typing import Any

import redis.asyncio as aioredis

from app.config import settings
from app.hardware.lora_crypto import LoRaCipherMode, encrypt_serial_payload, parse_aes128_key

LORA_SERIAL_MOCK_CHANNEL = "hardware:lora:serial_mock"


def build_lora_json_payload(
    *,
    node_id: str,
    latitude: float,
    longitude: float,
    altitude_m: float,
    rssi: float | None = None,
    snr: float | None = None,
    extra: dict[str, Any] | None = None,
) -> str:
    payload = {
        "node_id": node_id,
        "lat": latitude,
        "lon": longitude,
        "alt": altitude_m,
    }
    if rssi is not None:
        payload["rssi"] = rssi
    if snr is not None:
        payload["snr"] = snr
    if extra:
        payload.update(extra)
    return json.dumps(payload, separators=(",", ":"))


def maybe_encrypt_lora_line(plaintext: str) -> str:
    if not settings.drone_simulator_lora_encrypt_mock:
        return plaintext
    key = parse_aes128_key(settings.lora_encryption_key)
    if key is None:
        return plaintext
    mode = LoRaCipherMode.GCM if settings.lora_encryption_mode.upper().endswith("GCM") else LoRaCipherMode.CBC
    return encrypt_serial_payload(plaintext, key, mode=mode)


async def publish_encrypted_lora_mock(redis: aioredis.Redis, plaintext_line: str) -> str:
    line = maybe_encrypt_lora_line(plaintext_line)
    await redis.publish(LORA_SERIAL_MOCK_CHANNEL, line)
    return line
