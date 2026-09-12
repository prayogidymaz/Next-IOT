import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../map/widgets/tactical_tile_layer.dart' show isFlutterTestEnvironment;
import '../data/video_feed_repository.dart';
import '../models/video_feed_models.dart';
import '../utils/video_feed_parser.dart';

final videoFeedConnectionProvider = Provider<VideoFeedConnection>((ref) {
  if (isFlutterTestEnvironment) return MockVideoFeedConnection();
  return WebSocketVideoFeedConnection();
});

class VideoFeedState {
  const VideoFeedState({
    this.enabled = false,
    this.isConnecting = false,
    this.isConnected = false,
    this.layout = VideoPanelLayout.pip,
    this.streamInfo,
    this.currentFrame,
    this.error,
    this.deviceId,
  });

  final bool enabled;
  final bool isConnecting;
  final bool isConnected;
  final VideoPanelLayout layout;
  final VideoStreamInfo? streamInfo;
  final VideoFrameMessage? currentFrame;
  final String? error;
  final String? deviceId;

  VideoFeedState copyWith({
    bool? enabled,
    bool? isConnecting,
    bool? isConnected,
    VideoPanelLayout? layout,
    VideoStreamInfo? streamInfo,
    VideoFrameMessage? currentFrame,
    String? error,
    String? deviceId,
    bool clearError = false,
    bool clearFrame = false,
  }) {
    return VideoFeedState(
      enabled: enabled ?? this.enabled,
      isConnecting: isConnecting ?? this.isConnecting,
      isConnected: isConnected ?? this.isConnected,
      layout: layout ?? this.layout,
      streamInfo: streamInfo ?? this.streamInfo,
      currentFrame: clearFrame ? null : (currentFrame ?? this.currentFrame),
      error: clearError ? null : (error ?? this.error),
      deviceId: deviceId ?? this.deviceId,
    );
  }
}

class VideoFeedNotifier extends StateNotifier<VideoFeedState> {
  VideoFeedNotifier(this._connection) : super(const VideoFeedState());

  final VideoFeedConnection _connection;

  Future<void> toggleForDevice(String? deviceId) async {
    if (state.enabled) {
      await stop();
      return;
    }
    if (deviceId == null) {
      state = state.copyWith(error: 'Select a device for HUD video stream.');
      return;
    }
    await start(deviceId);
  }

  Future<void> start(String deviceId) async {
    await stop();
    state = VideoFeedState(
      enabled: true,
      isConnecting: true,
      deviceId: deviceId,
      layout: state.layout,
    );

    await _connection.connect(
      deviceId: deviceId,
      onMessage: _handleMessage,
      onError: (error) {
        state = state.copyWith(
          isConnecting: false,
          isConnected: false,
          error: 'Video stream error: $error',
        );
      },
      onDone: () {
        state = state.copyWith(isConnected: false);
      },
    );
  }

  void _handleMessage(Map<String, dynamic> message) {
    final streamInfo = parseVideoFeedStreamInfo(message);
    if (streamInfo != null) {
      state = state.copyWith(
        isConnecting: false,
        isConnected: true,
        streamInfo: streamInfo,
        clearError: true,
      );
      return;
    }

    final frame = parseVideoFeedFrame(message);
    if (frame != null) {
      state = state.copyWith(
        isConnecting: false,
        isConnected: true,
        currentFrame: frame,
        clearError: true,
      );
    }
  }

  void toggleLayout() {
    final next = state.layout == VideoPanelLayout.pip
        ? VideoPanelLayout.splitScreen
        : VideoPanelLayout.pip;
    state = state.copyWith(layout: next);
  }

  Future<void> stop() async {
    await _connection.disconnect();
    state = const VideoFeedState();
  }

  @override
  void dispose() {
    _connection.disconnect();
    super.dispose();
  }
}

final videoFeedProvider = StateNotifierProvider<VideoFeedNotifier, VideoFeedState>((ref) {
  return VideoFeedNotifier(ref.watch(videoFeedConnectionProvider));
});
