from app.telemetry.video_feed.generator import MockVideoFrameGenerator


def test_mock_video_frame_generator_produces_detections():
    generator = MockVideoFrameGenerator(device_id="drone-1")
    frame = generator.next_frame()
    assert frame.codec == "H264"
    assert frame.stream_protocol == "RTSP"
    assert frame.frame_b64
    assert frame.detections
    assert frame.detections[0].target_type.value in {"person", "vehicle"}
    assert frame.detections[0].confidence >= 0.89
