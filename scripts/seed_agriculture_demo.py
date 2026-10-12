#!/usr/bin/env python3
"""Seed demo — from repo root: docker compose exec api python scripts/seed_agriculture_demo.py"""

from __future__ import annotations

import asyncio

from app.seed_agriculture_demo import main

if __name__ == "__main__":
    asyncio.run(main())
