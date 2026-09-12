import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../data/weather_vector_repository.dart';
import '../models/weather_vector_models.dart';

final weatherVectorRepositoryProvider =
    Provider<WeatherVectorRepository>((ref) => WeatherVectorRepository());

class WeatherVectorState {
  const WeatherVectorState({
    this.enabled = false,
    this.isLoading = false,
    this.data,
    this.error,
    this.radiusM = 2000,
  });

  final bool enabled;
  final bool isLoading;
  final WeatherVectorData? data;
  final String? error;
  final double radiusM;

  WeatherVectorState copyWith({
    bool? enabled,
    bool? isLoading,
    WeatherVectorData? data,
    String? error,
    double? radiusM,
    bool clearError = false,
    bool clearData = false,
  }) {
    return WeatherVectorState(
      enabled: enabled ?? this.enabled,
      isLoading: isLoading ?? this.isLoading,
      data: clearData ? null : (data ?? this.data),
      error: clearError ? null : (error ?? this.error),
      radiusM: radiusM ?? this.radiusM,
    );
  }
}

class WeatherVectorNotifier extends StateNotifier<WeatherVectorState> {
  WeatherVectorNotifier(this._repository) : super(const WeatherVectorState());

  final WeatherVectorRepository _repository;

  Future<void> toggle() async {
    final next = !state.enabled;
    state = state.copyWith(enabled: next, clearError: true);
    if (!next) {
      state = state.copyWith(clearData: true);
      return;
    }
    if (state.data != null) return;
  }

  Future<void> loadForLocation({
    required double lat,
    required double lon,
    double? radiusM,
  }) async {
    state = state.copyWith(isLoading: true, clearError: true, radiusM: radiusM);
    try {
      final data = await _repository.fetchWeatherVector(
        lat: lat,
        lon: lon,
        radiusM: radiusM ?? state.radiusM,
      );
      state = state.copyWith(isLoading: false, data: data);
    } catch (_) {
      state = state.copyWith(
        isLoading: false,
        error: 'Failed to load weather vectors.',
        clearData: true,
      );
    }
  }

  Future<void> refreshIfEnabled({required double lat, required double lon}) async {
    if (!state.enabled) return;
    await loadForLocation(lat: lat, lon: lon);
  }
}

final weatherVectorProvider = StateNotifierProvider<WeatherVectorNotifier, WeatherVectorState>((ref) {
  return WeatherVectorNotifier(ref.watch(weatherVectorRepositoryProvider));
});
