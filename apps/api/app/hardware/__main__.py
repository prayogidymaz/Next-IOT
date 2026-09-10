"""Run the ESP32 LoRa USB serial bridge worker.

Usage:
    python -m app.hardware
"""

import asyncio
import logging
import signal

import redis.asyncio as aioredis

from app.config import settings
from app.hardware.lora_bridge import LoRaBridge

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s [lora_bridge] %(message)s",
)
logger = logging.getLogger(__name__)


async def _main() -> None:
    redis = aioredis.from_url(settings.redis_url, decode_responses=True)
    bridge = LoRaBridge(redis)

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

    run_task = asyncio.create_task(bridge.run_forever())
    await stop.wait()
    run_task.cancel()
    try:
        await run_task
    except asyncio.CancelledError:
        pass
    await redis.aclose()
    logger.info("LoRa bridge stopped")


def main() -> None:
    asyncio.run(_main())


if __name__ == "__main__":
    main()
