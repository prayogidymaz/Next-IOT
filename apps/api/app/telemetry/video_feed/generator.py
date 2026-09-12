"""Mock H.264/RTSP video frame generator with edge-AI detection metadata."""

from __future__ import annotations

import base64
from dataclasses import dataclass, field
from datetime import UTC, datetime

from app.telemetry.video_feed.schemas import DetectionBox, StreamInfoPayload, TargetType, VideoFramePayload

# Minimal mock Annex-B NAL header bytes for UI/testing (not a decodable stream).
_MOCK_H264_NAL = bytes([0x00, 0x00, 0x00, 0x01, 0x67, 0x42, 0x00, 0x1E, 0xAB, 0x40, 0xF0])


@dataclass
class MockVideoFrameGenerator:
    device_id: str
    width: int = 640
    height: int = 360
    fps: float = 5.0
    _frame_index: int = field(default=0, init=False)

    def stream_info(self) -> StreamInfoPayload:
        return StreamInfoPayload(
            device_id=self.device_id,
            codec="H264",
            stream_protocol="RTSP",
            fps=self.fps,
            resolution=f"{self.width}x{self.height}",
        )

    def next_frame(self) -> VideoFramePayload:
        self._frame_index += 1
        detections = self._synthetic_detections(self._frame_index)
        payload = f"{self.device_id}:{self._frame_index}".encode()
        frame_b64 = base64.b64encode(_MOCK_H264_NAL + payload).decode("ascii")
        return VideoFramePayload(
            device_id=self.device_id,
            frame_index=self._frame_index,
            timestamp=datetime.now(UTC),
            codec="H264",
            stream_protocol="RTSP",
            frame_b64=frame_b64,
            width=self.width,
            height=self.height,
            detections=detections,
        )

    def _synthetic_detections(self, frame_index: int) -> list[DetectionBox]:
        phase = frame_index % 6
        if phase in {0, 1}:
            return [
                DetectionBox(
                    target_type=TargetType.PERSON,
                    confidence=0.95,
                    bbox=[0.18 + phase * 0.02, 0.32, 0.14, 0.38],
                )
            ]
        if phase in {2, 3}:
            return [
                DetectionBox(
                    target_type=TargetType.VEHICLE,
                    confidence=0.93,
                    bbox=[0.52, 0.48, 0.28, 0.22],
                )
            ]
        return [
            DetectionBox(
                target_type=TargetType.PERSON,
                confidence=0.91,
                bbox=[0.22, 0.35, 0.12, 0.34],
            ),
            DetectionBox(
                target_type=TargetType.VEHICLE,
                confidence=0.89,
                bbox=[0.58, 0.50, 0.24, 0.20],
            ),
        ]
