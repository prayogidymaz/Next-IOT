import json

import pytest

from app.telemetry.video_feed.parser import (
    VideoFeedParseError,
    parse_detection_box,
    parse_video_feed_message,
    serialize_video_frame,
)
from app.telemetry.video_feed.generator import MockVideoFrameGenerator
from app.telemetry.video_feed.schemas import DetectionBox, TargetType


def test_parse_video_frame_message():
    generator = MockVideoFrameGenerator(device_id="device-1")
    frame = generator.next_frame()
    raw = json.dumps(serialize_video_frame(frame))
    parsed = parse_video_feed_message(raw)
    assert parsed.type == "video_frame"
    assert parsed.device_id == "device-1"
    assert parsed.codec == "H264"
    assert len(parsed.detections) >= 1


def test_parse_stream_info_message():
    generator = MockVideoFrameGenerator(device_id="device-1")
    info = generator.stream_info()
    parsed = parse_video_feed_message(info.model_dump(mode="json"))
    assert parsed.type == "stream_info"
    assert parsed.stream_protocol == "RTSP"


def test_parse_detection_box_valid():
    det = parse_detection_box(
        {"target_type": "person", "confidence": 0.95, "bbox": [0.1, 0.2, 0.3, 0.4]}
    )
    assert det.target_type == TargetType.PERSON
    assert det.confidence == 0.95


def test_parse_detection_box_invalid_bbox():
    with pytest.raises(VideoFeedParseError):
        parse_detection_box(
            {"target_type": "vehicle", "confidence": 0.95, "bbox": [0.1, 0.2, 1.5, 0.4]}
        )


def test_parse_unsupported_message_type():
    with pytest.raises(VideoFeedParseError):
        parse_video_feed_message({"type": "unknown", "device_id": "x"})
