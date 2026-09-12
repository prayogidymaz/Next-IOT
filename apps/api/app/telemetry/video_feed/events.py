import json
from typing import Any

import redis.asyncio as aioredis

DEVICE_VIDEO_CHANNEL = "device:video:pubsub"


def video_channel_for_device(device_id: str) -> str:
    return f"{DEVICE_VIDEO_CHANNEL}:{device_id}"


async def publish_video_frame(
    redis: aioredis.Redis,
    *,
    device_id: str,
    frame_payload: dict[str, Any],
) -> None:
    await redis.publish(video_channel_for_device(device_id), json.dumps(frame_payload))
