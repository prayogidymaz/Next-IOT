import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../data/telemetry_repository.dart';
import '../models/telemetry_analytics_models.dart';
import '../models/telemetry_models.dart';
import 'telemetry_provider.dart';

class TelemetryAnalyticsState {
  const TelemetryAnalyticsState({
    this.data,
    this.isLoading = false,
    this.error,
    this.hours = 24,
  });

  final TelemetryAnalytics? data;
  final bool isLoading;
  final String? error;
  final int hours;

  TelemetryAnalyticsState copyWith({
    TelemetryAnalytics? data,
    bool? isLoading,
    String? error,
    int? hours,
    bool clearError = false,
    bool clearData = false,
  }) {
    return TelemetryAnalyticsState(
      data: clearData ? null : (data ?? this.data),
      isLoading: isLoading ?? this.isLoading,
      error: clearError ? null : (error ?? this.error),
      hours: hours ?? this.hours,
    );
  }
}

class TelemetryAnalyticsNotifier extends StateNotifier<TelemetryAnalyticsState> {
  TelemetryAnalyticsNotifier(this._repository, this.deviceId) : super(const TelemetryAnalyticsState());

  final TelemetryRepository _repository;
  final String deviceId;

  Future<void> load({int? hours}) async {
    final lookback = hours ?? state.hours;
    state = state.copyWith(isLoading: true, hours: lookback, clearError: true);
    try {
      final data = await _repository.fetchAnalytics(deviceId: deviceId, hours: lookback);
      state = state.copyWith(isLoading: false, data: data);
    } catch (_) {
      state = state.copyWith(
        isLoading: false,
        error: 'Failed to load flight analytics.',
        clearData: true,
      );
    }
  }

  Future<void> loadForTimeRange(TelemetryTimeRange range) async {
    final hours = range == TelemetryTimeRange.oneHour ? 1 : 24;
    await load(hours: hours);
  }
}

final telemetryAnalyticsProvider =
    StateNotifierProvider.family<TelemetryAnalyticsNotifier, TelemetryAnalyticsState, String>(
  (ref, deviceId) => TelemetryAnalyticsNotifier(ref.watch(telemetryRepositoryProvider), deviceId),
);
