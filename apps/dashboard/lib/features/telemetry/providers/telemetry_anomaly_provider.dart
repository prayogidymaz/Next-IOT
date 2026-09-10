import 'dart:async';

import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../data/telemetry_anomaly_repository.dart';
import '../models/telemetry_anomaly_models.dart';

final telemetryAnomalyRepositoryProvider =
    Provider<TelemetryAnomalyRepository>((ref) => TelemetryAnomalyRepository());

class TelemetryAnomalyState {
  const TelemetryAnomalyState({
    this.items = const [],
    this.isLoading = false,
    this.error,
    this.deviceId,
    this.hours = 24,
  });

  final List<TelemetryAnomaly> items;
  final bool isLoading;
  final String? error;
  final String? deviceId;
  final int hours;

  bool get hasAnomalies => items.isNotEmpty;
  bool get hasCritical => items.any((a) => a.severity == 'critical');
  int get count => items.length;

  TelemetryAnomalyState copyWith({
    List<TelemetryAnomaly>? items,
    bool? isLoading,
    String? error,
    String? deviceId,
    int? hours,
    bool clearError = false,
  }) {
    return TelemetryAnomalyState(
      items: items ?? this.items,
      isLoading: isLoading ?? this.isLoading,
      error: clearError ? null : (error ?? this.error),
      deviceId: deviceId ?? this.deviceId,
      hours: hours ?? this.hours,
    );
  }
}

class TelemetryAnomalyNotifier extends StateNotifier<TelemetryAnomalyState> {
  TelemetryAnomalyNotifier(this._repository) : super(const TelemetryAnomalyState());

  final TelemetryAnomalyRepository _repository;
  Timer? _refreshTimer;

  Future<void> loadForDevice(String deviceId) async {
    state = state.copyWith(deviceId: deviceId, isLoading: true, clearError: true);
    try {
      final data = await _repository.fetchAnomalies(deviceId: deviceId, hours: state.hours);
      state = state.copyWith(
        deviceId: deviceId,
        items: data.items,
        isLoading: false,
      );
    } catch (_) {
      state = state.copyWith(
        isLoading: false,
        error: 'Failed to load anomalies.',
        items: const [],
      );
    }
  }

  void startRefreshLoop() {
    _refreshTimer?.cancel();
    _refreshTimer = Timer.periodic(const Duration(seconds: 15), (_) {
      final deviceId = state.deviceId;
      if (deviceId != null) {
        loadForDevice(deviceId);
      }
    });
  }

  void stopRefreshLoop() {
    _refreshTimer?.cancel();
  }

  @override
  void dispose() {
    _refreshTimer?.cancel();
    super.dispose();
  }
}

final telemetryAnomalyProvider =
    StateNotifierProvider<TelemetryAnomalyNotifier, TelemetryAnomalyState>((ref) {
  return TelemetryAnomalyNotifier(ref.watch(telemetryAnomalyRepositoryProvider));
});
