import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:next_iot_dashboard/features/video/models/video_feed_models.dart';
import 'package:next_iot_dashboard/features/video/utils/video_feed_parser.dart';
import 'package:next_iot_dashboard/features/video/widgets/ai_detection_overlay.dart';
import 'package:next_iot_dashboard/features/video/widgets/tactical_video_panel.dart';

void main() {
  const detections = [
    AiDetectionBox(
      targetType: 'person',
      confidence: 0.95,
      bbox: [0.18, 0.32, 0.14, 0.38],
    ),
    AiDetectionBox(
      targetType: 'vehicle',
      confidence: 0.93,
      bbox: [0.52, 0.48, 0.28, 0.22],
    ),
  ];

  test('parseVideoFeedFrame parses bbox metadata', () {
    final parsed = parseVideoFeedFrame({
      'type': 'video_frame',
      'device_id': 'd1',
      'frame_index': 3,
      'timestamp': '2026-09-10T10:00:00Z',
      'codec': 'H264',
      'frame_b64': 'abc',
      'width': 640,
      'height': 360,
      'detections': [
        {'target_type': 'person', 'confidence': 0.95, 'bbox': [0.1, 0.2, 0.3, 0.4]},
      ],
    });
    expect(parsed, isNotNull);
    expect(parsed!.detections.single.targetType, 'person');
  });

  test('parseDetectionBox rejects invalid bbox', () {
    expect(
      parseDetectionBox({'target_type': 'person', 'confidence': 0.95, 'bbox': [0.1, 0.2, 1.2, 0.4]}),
      isNull,
    );
  });

  testWidgets('TacticalVideoPanel renders live HUD and AI count', (tester) async {
    await tester.pumpWidget(
      MaterialApp(
        home: Scaffold(
          body: SizedBox(
            width: 320,
            height: 200,
            child: TacticalVideoPanel(
              streamInfo: const VideoStreamInfo(
                deviceId: 'd1',
                codec: 'H264',
                streamProtocol: 'RTSP',
                fps: 5,
                resolution: '640x360',
              ),
              currentFrame: VideoFrameMessage(
                deviceId: 'd1',
                frameIndex: 12,
                timestamp: DateTime(2026, 9, 10),
                codec: 'H264',
                frameB64: 'abc',
                width: 640,
                height: 360,
                detections: detections,
              ),
            ),
          ),
        ),
      ),
    );
    await tester.pump();

    expect(find.text('LIVE'), findsOneWidget);
    expect(find.textContaining('RTSP/H264'), findsOneWidget);
    expect(find.textContaining('F12 · 2 AI'), findsOneWidget);
  });

  testWidgets('AiDetectionOverlay paints without error', (tester) async {
    await tester.pumpWidget(
      const MaterialApp(
        home: Scaffold(
          body: SizedBox(
            width: 200,
            height: 120,
            child: AiDetectionOverlay(detections: detections),
          ),
        ),
      ),
    );
    await tester.pump();
    expect(find.byType(AiDetectionOverlay), findsOneWidget);
  });
}
