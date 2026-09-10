"""Run the live drone flight simulator worker.

Usage:
    python -m app.drone_simulator
"""

import asyncio
import logging
import signal

import redis.asyncio as aioredis

from app.config import settings
from app.drone_simulator.runner import DroneSimulator

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s [drone_simulator] %(message)s",
)
logger = logging.getLogger(__name__)


async def _main() -> None:
    redis = aioredis.from_url(settings.redis_url, decode_responses=True)
    simulator = DroneSimulator(redis=redis, tick_seconds=settings.drone_simulator_tick_seconds)

    stop = asyncio.Event()

    def _request_stop(*_: object) -> None:
        logger.info("Shutdown requested")
        stop.set()

    loop = asyncio.get_running_loop()
    for sig in (signal.SIGINT, signal.SIGTERM):
        try:
            loop.add_signal_handler(sig, _request_stop)
        except NotImplementedError:
            pass

    run_task = asyncio.create_task(simulator.run_forever())
    await stop.wait()
    run_task.cancel()
    try:
        await run_task
    except asyncio.CancelledError:
        pass
    await redis.aclose()
    logger.info("Drone simulator stopped")


def main() -> None:
    asyncio.run(_main())


if __name__ == "__main__":
    main()
