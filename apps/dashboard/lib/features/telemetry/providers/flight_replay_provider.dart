import 'dart:async';

import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:latlong2/latlong.dart';

import '../data/flight_replay_repository.dart';
import '../models/flight_replay_models.dart';

final flightReplayRepositoryProvider = Provider<FlightReplayRepository>((ref) => FlightReplayRepository());

class FlightReplayPosition {
  const FlightReplayPosition({
    required this.point,
    this.alt,
    this.speed,
    this.heading,
    this.rssi,
    this.sampleIndex = 0,
    this.progress = 0,
  });

  final LatLng point;
  final double? alt;
  final double? speed;
  final double? heading;
  final double? rssi;
  final int sampleIndex;
  final double progress;
}

class FlightReplayState {
  const FlightReplayState({
    this.enabled = false,
    this.isLoading = false,
    this.isPlaying = false,
    this.data,
    this.error,
    this.progress = 0,
    this.speedMultiplier = 1,
    this.trailPoints = const [],
    this.currentPosition,
    this.deviceId,
  });

  final bool enabled;
  final bool isLoading;
  final bool isPlaying;
  final FlightReplayData? data;
  final String? error;
  final double progress;
  final int speedMultiplier;
  final List<LatLng> trailPoints;
  final FlightReplayPosition? currentPosition;
  final String? deviceId;

  bool get hasData => data != null && data!.samples.isNotEmpty;

  FlightReplayState copyWith({
    bool? enabled,
    bool? isLoading,
    bool? isPlaying,
    FlightReplayData? data,
    String? error,
    double? progress,
    int? speedMultiplier,
    List<LatLng>? trailPoints,
    FlightReplayPosition? currentPosition,
    String? deviceId,
    bool clearData = false,
    bool clearError = false,
  }) {
    return FlightReplayState(
      enabled: enabled ?? this.enabled,
      isLoading: isLoading ?? this.isLoading,
      isPlaying: isPlaying ?? this.isPlaying,
      data: clearData ? null : (data ?? this.data),
      error: clearError ? null : (error ?? this.error),
      progress: progress ?? this.progress,
      speedMultiplier: speedMultiplier ?? this.speedMultiplier,
      trailPoints: trailPoints ?? this.trailPoints,
      currentPosition: currentPosition ?? this.currentPosition,
      deviceId: deviceId ?? this.deviceId,
    );
  }
}

class FlightReplayNotifier extends StateNotifier<FlightReplayState> {
  FlightReplayNotifier(this._repository) : super(const FlightReplayState());

  final FlightReplayRepository _repository;
  Timer? _playbackTimer;
  static const _tickMs = 100;

  Future<void> toggleForDevice(String? deviceId) async {
    if (state.enabled) {
      stop();
      return;
    }
    if (deviceId == null) {
      state = state.copyWith(error: 'Select a device to replay.');
      return;
    }
    await loadForDevice(deviceId);
  }

  Future<void> loadForDevice(String deviceId, {int hours = 24}) async {
    state = state.copyWith(
      enabled: true,
      isLoading: true,
      deviceId: deviceId,
      clearError: true,
      isPlaying: false,
      progress: 0,
      trailPoints: const [],
    );
    _stopTimer();

    try {
      final data = await _repository.fetchReplay(deviceId: deviceId, hours: hours);
      if (data.samples.isEmpty) {
        state = state.copyWith(
          isLoading: false,
          data: data,
          error: 'No GPS telemetry samples in this flight window.',
        );
        return;
      }
      final position = _positionAtProgress(data, 0);
      state = state.copyWith(
        isLoading: false,
        data: data,
        currentPosition: position,
        trailPoints: position != null ? [position.point] : const [],
      );
    } catch (_) {
      state = state.copyWith(
        isLoading: false,
        error: 'Failed to load flight replay.',
      );
    }
  }

  void play() {
    if (!state.hasData) return;
    state = state.copyWith(isPlaying: true);
    _startTimer();
  }

  void pause() {
    state = state.copyWith(isPlaying: false);
    _stopTimer();
  }

  void togglePlayPause() {
    if (state.isPlaying) {
      pause();
    } else {
      play();
    }
  }

  void setProgress(double value) {
    if (!state.hasData) return;
    final clamped = value.clamp(0.0, 1.0);
    final position = _positionAtProgress(state.data!, clamped);
    state = state.copyWith(
      progress: clamped,
      currentPosition: position,
      trailPoints: _trailUpToProgress(state.data!, clamped),
      isPlaying: false,
    );
    _stopTimer();
  }

  void cycleSpeed() {
    final next = switch (state.speedMultiplier) {
      1 => 2,
      2 => 4,
      _ => 1,
    };
    state = state.copyWith(speedMultiplier: next);
  }

  void stop() {
    _stopTimer();
    state = const FlightReplayState();
  }

  void _startTimer() {
    _stopTimer();
    _playbackTimer = Timer.periodic(const Duration(milliseconds: _tickMs), (_) => _tick());
  }

  void _stopTimer() {
    _playbackTimer?.cancel();
    _playbackTimer = null;
  }

  void _tick() {
    final data = state.data;
    if (data == null || data.samples.isEmpty) return;

    final durationMs = data.duration.inMilliseconds;
    if (durationMs <= 0) return;

    final increment = (_tickMs * state.speedMultiplier) / durationMs;
    var nextProgress = state.progress + increment;
    if (nextProgress >= 1.0) {
      nextProgress = 1.0;
      pause();
    }

    final position = _positionAtProgress(data, nextProgress);
    state = state.copyWith(
      progress: nextProgress,
      currentPosition: position,
      trailPoints: _trailUpToProgress(data, nextProgress),
    );
  }

  FlightReplayPosition? _positionAtProgress(FlightReplayData data, double progress) {
    final samples = data.samples;
    if (samples.isEmpty) return null;

    final startMs = data.sessionStart.millisecondsSinceEpoch;
    final endMs = data.sessionEnd.millisecondsSinceEpoch;
    final targetMs = startMs + ((endMs - startMs) * progress).round();

    FlightReplaySample? prev;
    for (var i = 0; i < samples.length; i++) {
      final sample = samples[i];
      final sampleMs = sample.timestamp.millisecondsSinceEpoch;
      if (sampleMs >= targetMs) {
        if (prev == null) {
          return FlightReplayPosition(
            point: LatLng(sample.lat, sample.lon),
            alt: sample.alt,
            speed: sample.speed,
            heading: sample.heading,
            rssi: sample.rssi,
            sampleIndex: i,
            progress: progress,
          );
        }
        final prevMs = prev.timestamp.millisecondsSinceEpoch;
        final span = sampleMs - prevMs;
        final t = span == 0 ? 1.0 : (targetMs - prevMs) / span;
        return FlightReplayPosition(
          point: LatLng(
            prev.lat + (sample.lat - prev.lat) * t,
            prev.lon + (sample.lon - prev.lon) * t,
          ),
          alt: _lerp(prev.alt, sample.alt, t),
          speed: _lerp(prev.speed, sample.speed, t),
          heading: _lerp(prev.heading, sample.heading, t),
          rssi: _lerp(prev.rssi, sample.rssi, t),
          sampleIndex: i,
          progress: progress,
        );
      }
      prev = sample;
    }

    final last = samples.last;
    return FlightReplayPosition(
      point: LatLng(last.lat, last.lon),
      alt: last.alt,
      speed: last.speed,
      heading: last.heading,
      rssi: last.rssi,
      sampleIndex: samples.length - 1,
      progress: progress,
    );
  }

  List<LatLng> _trailUpToProgress(FlightReplayData data, double progress) {
    final samples = data.samples;
    if (samples.isEmpty) return const [];

    final startMs = data.sessionStart.millisecondsSinceEpoch;
    final endMs = data.sessionEnd.millisecondsSinceEpoch;
    final targetMs = startMs + ((endMs - startMs) * progress).round();

    final points = <LatLng>[];
    for (final sample in samples) {
      if (sample.timestamp.millisecondsSinceEpoch > targetMs) break;
      points.add(LatLng(sample.lat, sample.lon));
    }
    final current = _positionAtProgress(data, progress);
    if (current != null &&
        (points.isEmpty ||
            points.last.latitude != current.point.latitude ||
            points.last.longitude != current.point.longitude)) {
      points.add(current.point);
    }
    return points;
  }

  double? _lerp(double? a, double? b, double t) {
    if (a == null || b == null) return a ?? b;
    return a + (b - a) * t;
  }

  @override
  void dispose() {
    _stopTimer();
    super.dispose();
  }
}

final flightReplayProvider = StateNotifierProvider<FlightReplayNotifier, FlightReplayState>((ref) {
  return FlightReplayNotifier(ref.watch(flightReplayRepositoryProvider));
});
