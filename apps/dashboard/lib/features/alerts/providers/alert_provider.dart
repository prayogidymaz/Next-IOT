import 'package:dio/dio.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../data/alert_repository.dart';
import '../models/alert_models.dart';

final alertRepositoryProvider = Provider<AlertRepository>((ref) => AlertRepository());

class AlertListState {
  const AlertListState({
    this.activeAlerts = const [],
    this.historyAlerts = const [],
    this.activeCount = 0,
    this.isLoading = false,
    this.error,
    this.showActiveOnly = true,
  });

  final List<DeviceAlert> activeAlerts;
  final List<DeviceAlert> historyAlerts;
  final int activeCount;
  final bool isLoading;
  final String? error;
  final bool showActiveOnly;

  List<DeviceAlert> get displayedAlerts => showActiveOnly ? activeAlerts : historyAlerts;

  AlertListState copyWith({
    List<DeviceAlert>? activeAlerts,
    List<DeviceAlert>? historyAlerts,
    int? activeCount,
    bool? isLoading,
    String? error,
    bool? showActiveOnly,
    bool clearError = false,
  }) {
    return AlertListState(
      activeAlerts: activeAlerts ?? this.activeAlerts,
      historyAlerts: historyAlerts ?? this.historyAlerts,
      activeCount: activeCount ?? this.activeCount,
      isLoading: isLoading ?? this.isLoading,
      error: clearError ? null : (error ?? this.error),
      showActiveOnly: showActiveOnly ?? this.showActiveOnly,
    );
  }
}

class AlertNotifier extends StateNotifier<AlertListState> {
  AlertNotifier(this._repository) : super(const AlertListState());

  final AlertRepository _repository;

  Future<void> loadAlerts() async {
    state = state.copyWith(isLoading: true, clearError: true);
    try {
      final summary = await _repository.fetchSummary();
      final history = await _repository.fetchAlerts(status: 'history', limit: 50);
      state = AlertListState(
        activeAlerts: summary.items,
        activeCount: summary.activeCount,
        historyAlerts: history.items,
      );
    } catch (e) {
      state = state.copyWith(isLoading: false, error: _mapError(e));
    }
  }

  Future<void> loadSummary() async {
    try {
      final summary = await _repository.fetchSummary();
      state = state.copyWith(
        activeAlerts: summary.items,
        activeCount: summary.activeCount,
      );
    } catch (_) {
      // Banner is best-effort
    }
  }

  void setShowActiveOnly(bool value) {
    state = state.copyWith(showActiveOnly: value);
  }

  String _mapError(Object e) {
    if (e is DioException && e.response?.statusCode == 404) {
      return 'No alerts found.';
    }
    return 'Failed to load alerts.';
  }
}

final alertProvider = StateNotifierProvider<AlertNotifier, AlertListState>((ref) {
  return AlertNotifier(ref.watch(alertRepositoryProvider));
});
