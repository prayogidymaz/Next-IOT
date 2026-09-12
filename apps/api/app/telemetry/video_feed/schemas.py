from datetime import datetime
from enum import StrEnum
from typing import Any

from pydantic import BaseModel, Field, field_validator


class TargetType(StrEnum):
    PERSON = "person"
    VEHICLE = "vehicle"


class DetectionBox(BaseModel):
    target_type: TargetType
    confidence: float = Field(ge=0.0, le=1.0)
    bbox: list[float] = Field(min_length=4, max_length=4)

    @field_validator("bbox")
    @classmethod
    def bbox_values_normalized(cls, value: list[float]) -> list[float]:
        for index, component in enumerate(value):
            if component < 0 or component > 1:
                raise ValueError(f"bbox[{index}] must be between 0 and 1")
        return value


class VideoFramePayload(BaseModel):
    type: str = "video_frame"
    device_id: str
    frame_index: int = Field(ge=0)
    timestamp: datetime
    codec: str = "H264"
    stream_protocol: str = "RTSP"
    frame_b64: str
    width: int = 640
    height: int = 360
    detections: list[DetectionBox] = Field(default_factory=list)


class StreamInfoPayload(BaseModel):
    type: str = "stream_info"
    device_id: str
    codec: str = "H264"
    stream_protocol: str = "RTSP"
    fps: float = 5.0
    resolution: str = "640x360"


class VideoFeedMessage(BaseModel):
    """Union wrapper for inbound/outbound video feed websocket messages."""

    type: str
    payload: dict[str, Any]
