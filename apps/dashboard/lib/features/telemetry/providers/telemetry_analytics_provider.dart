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
    this.timeRange = TelemetryTimeRange.twentyFourHours,
    this.selectedMetrics = const [],
    this.customStart,
    this.customEnd,
  });

  final TelemetryAnalytics? data;
  final bool isLoading;
  final String? error;
  final TelemetryTimeRange timeRange;
  final List<String> selectedMetrics;
  final DateTime? customStart;
  final DateTime? customEnd;

  TelemetryAnalyticsState copyWith({
    TelemetryAnalytics? data,
    bool? isLoading,
    String? error,
    TelemetryTimeRange? timeRange,
    List<String>? selectedMetrics,
    DateTime? customStart,
    DateTime? customEnd,
    bool clearError = false,
    bool clearData = false,
  }) {
    return TelemetryAnalyticsState(
      data: clearData ? null : (data ?? this.data),
      isLoading: isLoading ?? this.isLoading,
      error: clearError ? null : (error ?? this.error),
      timeRange: timeRange ?? this.timeRange,
      selectedMetrics: selectedMetrics ?? this.selectedMetrics,
      customStart: customStart ?? this.customStart,
      customEnd: customEnd ?? this.customEnd,
    );
  }
}

class TelemetryAnalyticsNotifier
    extends StateNotifier<TelemetryAnalyticsState> {
  TelemetryAnalyticsNotifier(this._repository, this.deviceId)
      : super(const TelemetryAnalyticsState());

  final TelemetryRepository _repository;
  final String deviceId;

  Future<void> load({
    TelemetryTimeRange? range,
    List<String>? metrics,
    DateTime? customStart,
    DateTime? customEnd,
  }) async {
    final activeRange = range ?? state.timeRange;
    final (start, end) = activeRange.window(
      customStart: customStart ?? state.customStart,
      customEnd: customEnd ?? state.customEnd,
    );
    final metricKeys = metrics ?? state.selectedMetrics;
    state = state.copyWith(
      isLoading: true,
      timeRange: activeRange,
      selectedMetrics: metricKeys,
      customStart: customStart ?? state.customStart,
      customEnd: customEnd ?? state.customEnd,
      clearError: true,
    );
    try {
      final data = await _repository.fetchAnalytics(
        deviceId: deviceId,
        startTime: start,
        endTime: end,
        interval: activeRange.defaultInterval,
        metrics: metricKeys.isEmpty ? null : metricKeys,
      );
      state = state.copyWith(isLoading: false, data: data);
    } catch (_) {
      state = state.copyWith(
        isLoading: false,
        error: 'Failed to load telemetry analytics.',
        clearData: true,
      );
    }
  }

  Future<void> loadForTimeRange(TelemetryTimeRange range) async {
    await load(range: range);
  }
}

final telemetryAnalyticsProvider = StateNotifierProvider.family<
    TelemetryAnalyticsNotifier, TelemetryAnalyticsState, String>(
  (ref, deviceId) => TelemetryAnalyticsNotifier(
      ref.watch(telemetryRepositoryProvider), deviceId),
);
