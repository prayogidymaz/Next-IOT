#!/usr/bin/env python3
"""Seed mesh workflow presets for a demo tenant.

Run: docker compose exec -T api python scripts/seed_mesh_preset_workflows.py --tenant-slug kopi-toraja-mitra
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import argparse
import asyncio

from app.database import async_session
from app.mesh.seed_preset_workflows import seed_mesh_preset_workflows


async def _run(tenant_slug: str) -> int:
    async with async_session() as db:
        created = await seed_mesh_preset_workflows(db, tenant_slug)
        await db.commit()
        return created


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--tenant-slug", required=True)
    args = parser.parse_args()
    created = asyncio.run(_run(args.tenant_slug))
    print(f"Mesh workflow presets created: {created}")


if __name__ == "__main__":
    main()
