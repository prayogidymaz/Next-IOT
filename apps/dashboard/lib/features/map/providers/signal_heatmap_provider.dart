import 'dart:async';

import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../data/signal_heatmap_repository.dart';
import '../models/signal_heatmap_models.dart';

final signalHeatmapRepositoryProvider =
    Provider<SignalHeatmapRepository>((ref) => SignalHeatmapRepository());

class SignalHeatmapState {
  const SignalHeatmapState({
    this.enabled = false,
    this.hours = 24,
    this.points = const [],
    this.isLoading = false,
    this.error,
    this.deviceId,
  });

  final bool enabled;
  final int hours;
  final List<SignalHeatmapPoint> points;
  final bool isLoading;
  final String? error;
  final String? deviceId;

  SignalHeatmapState copyWith({
    bool? enabled,
    int? hours,
    List<SignalHeatmapPoint>? points,
    bool? isLoading,
    String? error,
    String? deviceId,
    bool clearError = false,
  }) {
    return SignalHeatmapState(
      enabled: enabled ?? this.enabled,
      hours: hours ?? this.hours,
      points: points ?? this.points,
      isLoading: isLoading ?? this.isLoading,
      error: clearError ? null : (error ?? this.error),
      deviceId: deviceId ?? this.deviceId,
    );
  }
}

class SignalHeatmapNotifier extends StateNotifier<SignalHeatmapState> {
  SignalHeatmapNotifier(this._repository) : super(const SignalHeatmapState());

  final SignalHeatmapRepository _repository;
  Timer? _refreshTimer;

  Future<void> toggle() async {
    final next = !state.enabled;
    state = state.copyWith(enabled: next, clearError: true);
    if (next) {
      _startRefreshLoop();
    } else {
      _refreshTimer?.cancel();
      state = state.copyWith(points: const []);
    }
  }

  Future<void> setHours(int hours) async {
    state = state.copyWith(hours: hours, clearError: true);
    if (state.enabled && state.deviceId != null) {
      await loadForDevice(state.deviceId!);
    }
  }

  Future<void> loadForDevice(String deviceId) async {
    if (!state.enabled) {
      state = state.copyWith(deviceId: deviceId);
      return;
    }

    state = state.copyWith(deviceId: deviceId, isLoading: true, clearError: true);
    try {
      final data = await _repository.fetchHeatmap(deviceId: deviceId, hours: state.hours);
      state = state.copyWith(
        deviceId: deviceId,
        points: data.points,
        isLoading: false,
      );
    } catch (_) {
      state = state.copyWith(
        isLoading: false,
        error: 'Failed to load signal heatmap.',
        points: const [],
      );
    }
  }

  void _startRefreshLoop() {
    _refreshTimer?.cancel();
    _refreshTimer = Timer.periodic(const Duration(seconds: 30), (_) {
      final deviceId = state.deviceId;
      if (state.enabled && deviceId != null) {
        loadForDevice(deviceId);
      }
    });
  }

  @override
  void dispose() {
    _refreshTimer?.cancel();
    super.dispose();
  }
}

final signalHeatmapProvider = StateNotifierProvider<SignalHeatmapNotifier, SignalHeatmapState>((ref) {
  return SignalHeatmapNotifier(ref.watch(signalHeatmapRepositoryProvider));
});
