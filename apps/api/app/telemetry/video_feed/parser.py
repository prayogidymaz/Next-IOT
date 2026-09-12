"""Parse and validate tactical video feed WebSocket metadata messages."""

from __future__ import annotations

import json
from typing import Any

from pydantic import ValidationError

from app.telemetry.video_feed.schemas import DetectionBox, StreamInfoPayload, VideoFramePayload


class VideoFeedParseError(ValueError):
    """Raised when a websocket payload cannot be parsed as video feed metadata."""


def parse_video_feed_message(raw: str | bytes | dict[str, Any]) -> VideoFramePayload | StreamInfoPayload:
    """Parse JSON websocket payload into a typed video feed message."""
    data = _coerce_dict(raw)
    message_type = data.get("type")
    if message_type == "stream_info":
        return StreamInfoPayload.model_validate(data)
    if message_type == "video_frame":
        return VideoFramePayload.model_validate(data)
    raise VideoFeedParseError(f"Unsupported video feed message type: {message_type}")


def parse_detection_box(raw: dict[str, Any]) -> DetectionBox:
    try:
        return DetectionBox.model_validate(raw)
    except ValidationError as exc:
        raise VideoFeedParseError(str(exc)) from exc


def serialize_video_frame(frame: VideoFramePayload) -> dict[str, Any]:
    return frame.model_dump(mode="json")


def serialize_stream_info(info: StreamInfoPayload) -> dict[str, Any]:
    return info.model_dump(mode="json")


def _coerce_dict(raw: str | bytes | dict[str, Any]) -> dict[str, Any]:
    if isinstance(raw, dict):
        return raw
    if isinstance(raw, (str, bytes)):
        try:
            parsed = json.loads(raw)
        except json.JSONDecodeError as exc:
            raise VideoFeedParseError("Invalid JSON payload") from exc
        if not isinstance(parsed, dict):
            raise VideoFeedParseError("Video feed payload must be a JSON object")
        return parsed
    raise VideoFeedParseError(f"Unsupported payload type: {type(raw)!r}")
