#!/usr/bin/env python3
"""Create mesh simulator devices + MQTT credentials for a tenant.

Run:
  docker compose exec -T api python scripts/bootstrap_mesh_simulator_devices.py --tenant-slug kopi-toraja-mitra
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import argparse
import asyncio
import uuid

from app.database import async_session
from app.devices.security import generate_client_secret, hash_device_secret
from app.models.device import Device, DeviceStatus
from app.models.device_credential import (
    CredentialType,
    DeviceCredential,
    generate_access_token,
    generate_connection_client_id,
)
from app.models.device_profile import DeviceProfile
from app.models.tenant import Tenant
from sqlalchemy import select

SIMULATOR_SPECS: list[tuple[str, str, str]] = [
    ("cctv-plot-a", "agri_cctv_outdoor", "cctv"),
    ("sprayer-plot-a", "agri_sprayer_station", "sprayer"),
    ("gate-north", "agri_gate_lock", "gate"),
    ("cyberdeck-field", "agri_cyberdeck_field", "cyberdeck"),
    ("weather-plot-a", "agri_weather_station", "weather"),
    ("smartwatch-op1", "agri_cyberdeck_field", "smartwatch"),
    ("drone-patrol-1", "agri_drone_patrol", "drone"),
]


async def _bootstrap(tenant_slug: str, farm_id: uuid.UUID | None) -> int:
    created = 0
    async with async_session() as db:
        tenant = await db.scalar(select(Tenant).where(Tenant.slug == tenant_slug))
        if tenant is None:
            raise SystemExit(f"Tenant not found: {tenant_slug}")
        for slug, profile_key, role in SIMULATOR_SPECS:
            existing = await db.scalar(
                select(Device).where(Device.tenant_id == tenant.id, Device.name == slug)
            )
            if existing is not None:
                continue
            profile = await db.scalar(
                select(DeviceProfile).where(
                    DeviceProfile.tenant_id == tenant.id,
                    DeviceProfile.key == profile_key,
                )
            )
            if profile is None:
                continue
            device = Device(
                tenant_id=tenant.id,
                profile_id=profile.id,
                name=slug,
                device_type=role,
                status=DeviceStatus.PROVISIONED,
            )
            db.add(device)
            await db.flush()
            secret = generate_client_secret()
            cred = DeviceCredential(
                device_id=device.id,
                tenant_id=tenant.id,
                credential_type=CredentialType.BASIC_AUTH,
                access_token=generate_access_token(),
                client_id=generate_connection_client_id(),
                secret_hash=hash_device_secret(secret),
                is_active=True,
            )
            db.add(cred)
            created += 1
            print(
                f"{role}: device_id={device.id} client_id={cred.client_id} "
                f"client_secret={secret} tenant_id={tenant.id} farm_id={farm_id}"
            )
        await db.commit()
    return created


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--tenant-slug", required=True)
    parser.add_argument("--farm-id", default="")
    args = parser.parse_args()
    farm_uuid = uuid.UUID(args.farm_id) if args.farm_id else None
    count = asyncio.run(_bootstrap(args.tenant_slug, farm_uuid))
    print(f"Created {count} simulator device(s)")


if __name__ == "__main__":
    main()
