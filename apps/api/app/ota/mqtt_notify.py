"""Publish OTA commands to devices over MQTT."""

from __future__ import annotations

import uuid

from pydantic import JsonValue
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.device import Device
from app.models.firmware_release import FirmwareRelease, OtaDeviceRollout
from app.mqtt_publisher.protocol import MqttPublisherProtocol


def _ota_topic(tenant_id: uuid.UUID, device_id: uuid.UUID) -> str:
    return f"tenants/{tenant_id}/devices/{device_id}/ota/update"


async def publish_ota_rollouts_for_release(
    db: AsyncSession,
    publisher: MqttPublisherProtocol,
    release_id: uuid.UUID,
) -> int:
    release = await db.scalar(select(FirmwareRelease).where(FirmwareRelease.id == release_id))
    if release is None:
        return 0
    rollouts = list(
        await db.scalars(select(OtaDeviceRollout).where(OtaDeviceRollout.release_id == release_id))
    )
    sent = 0
    for rollout in rollouts:
        device = await db.scalar(select(Device).where(Device.id == rollout.device_id))
        if device is None:
            continue
        payload: dict[str, JsonValue] = {
            "firmware_release_id": str(release.id),
            "version": release.version,
            "file_url": release.file_url,
            "checksum_sha256": release.checksum_sha256,
        }
        await publisher.publish_json(_ota_topic(device.tenant_id, device.id), payload, qos=1)
        sent += 1
    return sent
