#!/usr/bin/env python3
"""Seed mesh agriculture device profiles.

Run: docker compose exec api bash -c "cd /app && PYTHONPATH=/app python scripts/seed_mesh_agri_profiles.py"
"""

import asyncio

from app.device_profiles.seed_mesh_agri import run_mesh_agri_profile_seed


def main() -> None:
    created = asyncio.run(run_mesh_agri_profile_seed())
    print(f"Mesh agri profiles created: {created}")


if __name__ == "__main__":
    main()
