import 'package:dio/dio.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../data/telemetry_repository.dart';
import '../models/telemetry_models.dart';

final telemetryRepositoryProvider =
    Provider<TelemetryRepository>((ref) => TelemetryRepository());

class TelemetryState {
  const TelemetryState({
    this.latest,
    this.history = const [],
    this.timeRange = TelemetryTimeRange.twentyFourHours,
    this.selectedChartMetric = 'temperature',
    this.isLoading = false,
    this.error,
  });

  final TelemetryLatest? latest;
  final List<TelemetryHistoryItem> history;
  final TelemetryTimeRange timeRange;
  final String selectedChartMetric;
  final bool isLoading;
  final String? error;

  List<TelemetryHistoryItem> get chronologicalHistory =>
      sortHistoryChronologically(history);

  List<String> get chartMetricOptions {
    if (history.isEmpty && latest != null) return latest!.metrics.keys.toList();
    final keys = <String>{};
    for (final item in history) {
      keys.addAll(item.metrics.keys);
    }
    return keys.toList()..sort();
  }

  TelemetryState copyWith({
    TelemetryLatest? latest,
    List<TelemetryHistoryItem>? history,
    TelemetryTimeRange? timeRange,
    String? selectedChartMetric,
    bool? isLoading,
    String? error,
    bool clearError = false,
  }) {
    return TelemetryState(
      latest: latest ?? this.latest,
      history: history ?? this.history,
      timeRange: timeRange ?? this.timeRange,
      selectedChartMetric: selectedChartMetric ?? this.selectedChartMetric,
      isLoading: isLoading ?? this.isLoading,
      error: clearError ? null : (error ?? this.error),
    );
  }
}

class TelemetryNotifier extends StateNotifier<TelemetryState> {
  TelemetryNotifier(this._repository, this.deviceId) : super(const TelemetryState());

  final TelemetryRepository _repository;
  final String deviceId;

  Future<void> load({TelemetryTimeRange? range}) async {
    final activeRange = range ?? state.timeRange;
    state = state.copyWith(isLoading: true, timeRange: activeRange, clearError: true);

    try {
      final now = DateTime.now().toUtc();
      final start = now.subtract(activeRange.duration);

      final results = await Future.wait([
        _repository.fetchLatest(deviceId),
        _repository.fetchHistory(
          deviceId,
          startTime: start,
          endTime: now,
          limit: activeRange.limit,
        ),
      ]);

      final latest = results[0] as TelemetryLatest;
      final historyResponse = results[1] as TelemetryHistory;
      final chartMetric = state.selectedChartMetric;
      final options = historyResponse.items.expand((e) => e.metrics.keys).toSet();

      state = TelemetryState(
        latest: latest,
        history: historyResponse.items,
        timeRange: activeRange,
        selectedChartMetric: options.contains(chartMetric)
            ? chartMetric
            : (options.isNotEmpty ? options.first : 'temperature'),
        isLoading: false,
      );
    } catch (e) {
      state = state.copyWith(isLoading: false, error: _mapError(e));
    }
  }

  void setTimeRange(TelemetryTimeRange range) => load(range: range);

  void setChartMetric(String metric) {
    state = state.copyWith(selectedChartMetric: metric);
  }

  String _mapError(Object e) {
    if (e is DioException && e.response?.statusCode == 404) {
      return 'No telemetry data yet for this device.';
    }
    return 'Failed to load telemetry. Check connection and try again.';
  }
}

final telemetryProvider =
    StateNotifierProvider.family<TelemetryNotifier, TelemetryState, String>(
  (ref, deviceId) => TelemetryNotifier(ref.watch(telemetryRepositoryProvider), deviceId),
);
