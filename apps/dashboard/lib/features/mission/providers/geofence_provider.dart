import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../data/geofence_repository.dart';
import '../models/geofence_models.dart';

final geofenceRepositoryProvider = Provider<GeofenceRepository>((ref) => GeofenceRepository());

class GeofenceState {
  const GeofenceState({
    this.enabled = false,
    this.isLoading = false,
    this.zones = const [],
    this.error,
    this.hasActiveBreach = false,
  });

  final bool enabled;
  final bool isLoading;
  final List<GeofenceZone> zones;
  final String? error;
  final bool hasActiveBreach;

  GeofenceState copyWith({
    bool? enabled,
    bool? isLoading,
    List<GeofenceZone>? zones,
    String? error,
    bool? hasActiveBreach,
    bool clearError = false,
  }) {
    return GeofenceState(
      enabled: enabled ?? this.enabled,
      isLoading: isLoading ?? this.isLoading,
      zones: zones ?? this.zones,
      error: clearError ? null : (error ?? this.error),
      hasActiveBreach: hasActiveBreach ?? this.hasActiveBreach,
    );
  }
}

class GeofenceNotifier extends StateNotifier<GeofenceState> {
  GeofenceNotifier(this._repository) : super(const GeofenceState());

  final GeofenceRepository _repository;

  Future<void> toggle() async {
    final next = !state.enabled;
    state = state.copyWith(enabled: next, clearError: true);
    if (!next) return;
    if (state.zones.isEmpty) {
      await loadZones();
    }
  }

  Future<void> loadZones() async {
    state = state.copyWith(isLoading: true, clearError: true);
    try {
      final data = await _repository.fetchZones();
      state = state.copyWith(isLoading: false, zones: data.zones);
    } catch (_) {
      state = state.copyWith(
        isLoading: false,
        error: 'Failed to load geofence zones.',
        zones: const [],
      );
    }
  }

  void setBreachActive(bool active) {
    if (state.hasActiveBreach == active) return;
    state = state.copyWith(hasActiveBreach: active);
  }
}

final geofenceProvider = StateNotifierProvider<GeofenceNotifier, GeofenceState>((ref) {
  return GeofenceNotifier(ref.watch(geofenceRepositoryProvider));
});
