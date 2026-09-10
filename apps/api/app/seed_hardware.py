"""Seed demo LoRa node mapping and bridge credentials for Demo Sensor Node."""

import asyncio
import logging

import redis.asyncio as aioredis
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.config import settings
from app.database import async_session
from app.devices.liveness import touch_liveness
from app.devices.security import generate_client_id, generate_client_secret, hash_device_secret
from app.models.device import Device, DeviceStatus
from app.models.device_credential import DeviceCredential
from app.models.device_metadata import DeviceMetadata
from app.models.tenant import Tenant
from app.seed_telemetry import DEMO_DEVICE_NAME

logger = logging.getLogger(__name__)


async def ensure_demo_lora_hardware(db, redis: aioredis.Redis) -> bool:
    tenant = await db.scalar(select(Tenant).where(Tenant.slug == settings.seed_tenant_slug))
    if tenant is None:
        return False

    device = await db.scalar(
        select(Device)
        .options(selectinload(Device.metadata_entries), selectinload(Device.credentials))
        .where(Device.tenant_id == tenant.id, Device.name == DEMO_DEVICE_NAME)
    )
    if device is None:
        return False

    changed = False
    for key, value in {
        "lora_node_id": settings.lora_bridge_default_node_id,
    }.items():
        existing = next((m for m in device.metadata_entries if m.key == key), None)
        if existing is None or existing.value != value:
            if existing:
                existing.value = value
            else:
                db.add(DeviceMetadata(device_id=device.id, key=key, value=value))
            changed = True

    cred = device.credentials[0] if device.credentials else None
    secret_plain = settings.lora_bridge_default_client_secret or None
    client_id = cred.client_id if cred is not None else None

    if cred is None:
        secret_plain = secret_plain or generate_client_secret()
        client_id = settings.lora_bridge_default_client_id or generate_client_id()
        db.add(
            DeviceCredential(
                device_id=device.id,
                client_id=client_id,
                secret_hash=hash_device_secret(secret_plain),
            )
        )
        changed = True
    elif secret_plain:
        client_id = cred.client_id
    else:
        client_id = cred.client_id
        secret_plain = None

    if secret_plain:
        meta_secret = next((m for m in device.metadata_entries if m.key == "lora_bridge_client_secret"), None)
        if meta_secret is None or meta_secret.value != secret_plain:
            if meta_secret:
                meta_secret.value = secret_plain
            else:
                db.add(
                    DeviceMetadata(
                        device_id=device.id,
                        key="lora_bridge_client_secret",
                        value=secret_plain,
                    )
                )
            changed = True

    if device.status != DeviceStatus.ONLINE:
        device.status = DeviceStatus.ONLINE
        changed = True

    await touch_liveness(redis, str(device.id))
    await db.commit()
    if changed:
        logger.info(
            "Seeded LoRa hardware mapping for %s (node=%s, client_id=%s)",
            device.name,
            settings.lora_bridge_default_node_id,
            client_id,
        )
    return changed


async def run_hardware_seed(redis: aioredis.Redis) -> bool:
    async with async_session() as db:
        return await ensure_demo_lora_hardware(db, redis)


def main() -> None:
    redis = aioredis.from_url(settings.redis_url, decode_responses=True)

    async def _run() -> bool:
        try:
            return await run_hardware_seed(redis)
        finally:
            await redis.aclose()

    changed = asyncio.run(_run())
    print("Demo LoRa hardware seed applied" if changed else "Demo LoRa hardware seed already present")


if __name__ == "__main__":
    main()
