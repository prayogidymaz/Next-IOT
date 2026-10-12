#!/usr/bin/env python3
"""Seed Smart Agriculture demo — run: docker compose exec api python scripts/seed_agriculture_demo.py"""

from app.seed_agriculture_demo import main

if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
