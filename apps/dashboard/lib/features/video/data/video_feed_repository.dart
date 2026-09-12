import 'dart:async';
import 'dart:convert';

import 'package:web_socket_channel/web_socket_channel.dart';

import '../../../core/auth/token_storage.dart';
import '../../../core/config/api_config.dart';
import '../utils/video_feed_parser.dart';

typedef VideoFeedMessageHandler = void Function(Map<String, dynamic> message);

abstract class VideoFeedConnection {
  Future<void> connect({
    required String deviceId,
    required VideoFeedMessageHandler onMessage,
    required void Function(Object error) onError,
    required void Function() onDone,
  });

  Future<void> disconnect();
}

class WebSocketVideoFeedConnection implements VideoFeedConnection {
  WebSocketVideoFeedConnection({TokenStorage? tokenStorage})
      : _tokenStorage = tokenStorage ?? TokenStorage();

  final TokenStorage _tokenStorage;
  WebSocketChannel? _channel;
  StreamSubscription<dynamic>? _subscription;

  @override
  Future<void> connect({
    required String deviceId,
    required VideoFeedMessageHandler onMessage,
    required void Function(Object error) onError,
    required void Function() onDone,
  }) async {
    final token = await _tokenStorage.getAccessToken();
    if (token == null || token.isEmpty) {
      onError(StateError('Missing access token'));
      return;
    }

    final uri = Uri.parse(
      '${ApiConfig.wsBaseUrl}/api/v1/telemetry/video-feed/$deviceId?token=$token',
    );
    _channel = WebSocketChannel.connect(uri);
    _subscription = _channel!.stream.listen(
      (event) {
        try {
          final decoded = jsonDecode(event as String) as Map<String, dynamic>;
          onMessage(decoded);
        } catch (e) {
          onError(e);
        }
      },
      onError: onError,
      onDone: onDone,
      cancelOnError: true,
    );
  }

  @override
  Future<void> disconnect() async {
    await _subscription?.cancel();
    await _channel?.sink.close();
    _subscription = null;
    _channel = null;
  }
}

class MockVideoFeedConnection implements VideoFeedConnection {
  MockVideoFeedConnection({this.interval = const Duration(milliseconds: 200)});

  final Duration interval;
  StreamSubscription<int>? _subscription;
  int _frameIndex = 0;

  @override
  Future<void> connect({
    required String deviceId,
    required VideoFeedMessageHandler onMessage,
    required void Function(Object error) onError,
    required void Function() onDone,
  }) async {
    onMessage({
      'type': 'stream_info',
      'device_id': deviceId,
      'codec': 'H264',
      'stream_protocol': 'RTSP',
      'fps': 5.0,
      'resolution': '640x360',
    });

    _subscription = Stream.periodic(interval, (tick) => tick).listen(
      (_) {
        _frameIndex += 1;
        final phase = _frameIndex % 6;
        final detections = <Map<String, dynamic>>[];
        if (phase <= 1) {
          detections.add({
            'target_type': 'person',
            'confidence': 0.95,
            'bbox': [0.18, 0.32, 0.14, 0.38],
          });
        } else if (phase <= 3) {
          detections.add({
            'target_type': 'vehicle',
            'confidence': 0.93,
            'bbox': [0.52, 0.48, 0.28, 0.22],
          });
        } else {
          detections.addAll([
            {'target_type': 'person', 'confidence': 0.91, 'bbox': [0.22, 0.35, 0.12, 0.34]},
            {'target_type': 'vehicle', 'confidence': 0.89, 'bbox': [0.58, 0.50, 0.24, 0.20]},
          ]);
        }

        onMessage({
          'type': 'video_frame',
          'device_id': deviceId,
          'frame_index': _frameIndex,
          'timestamp': DateTime.now().toUtc().toIso8601String(),
          'codec': 'H264',
          'stream_protocol': 'RTSP',
          'frame_b64': base64Encode([0, 0, 0, 1, 103]),
          'width': 640,
          'height': 360,
          'detections': detections,
        });
      },
      onError: onError,
      onDone: onDone,
    );
  }

  @override
  Future<void> disconnect() async {
    await _subscription?.cancel();
    _subscription = null;
  }
}
