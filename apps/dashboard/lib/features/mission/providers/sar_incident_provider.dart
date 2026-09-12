import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../data/sar_incident_repository.dart';
import '../models/sar_grid_models.dart';
import '../models/sar_incident_models.dart';
import 'sar_grid_provider.dart';

final sarIncidentRepositoryProvider = Provider<SarIncidentRepository>((ref) => SarIncidentRepository());

class SarIncidentState {
  const SarIncidentState({
    this.panelOpen = false,
    this.isLoading = false,
    this.incidents = const [],
    this.selectedIncidentId,
    this.error,
  });

  final bool panelOpen;
  final bool isLoading;
  final List<SarIncident> incidents;
  final String? selectedIncidentId;
  final String? error;

  List<SarIncident> get activeIncidents =>
      incidents.where((i) => i.status == SarIncidentStatus.active).toList();

  SarIncident? get selectedIncident {
    if (selectedIncidentId == null) return null;
    for (final item in incidents) {
      if (item.id == selectedIncidentId) return item;
    }
    return null;
  }

  SarIncidentState copyWith({
    bool? panelOpen,
    bool? isLoading,
    List<SarIncident>? incidents,
    String? selectedIncidentId,
    String? error,
    bool clearError = false,
  }) {
    return SarIncidentState(
      panelOpen: panelOpen ?? this.panelOpen,
      isLoading: isLoading ?? this.isLoading,
      incidents: incidents ?? this.incidents,
      selectedIncidentId: selectedIncidentId ?? this.selectedIncidentId,
      error: clearError ? null : (error ?? this.error),
    );
  }
}

class SarIncidentNotifier extends StateNotifier<SarIncidentState> {
  SarIncidentNotifier(this._repository, this._ref) : super(const SarIncidentState());

  final SarIncidentRepository _repository;
  final Ref _ref;

  Future<void> togglePanel() async {
    final next = !state.panelOpen;
    state = state.copyWith(panelOpen: next, clearError: true);
    if (next) await loadIncidents();
  }

  Future<void> loadIncidents() async {
    state = state.copyWith(isLoading: true, clearError: true);
    try {
      final data = await _repository.fetchIncidents();
      state = state.copyWith(isLoading: false, incidents: data.incidents);
    } catch (_) {
      state = state.copyWith(isLoading: false, error: 'Failed to load SAR incidents.');
    }
  }

  void selectIncident(String? incidentId) {
    state = state.copyWith(selectedIncidentId: incidentId);
  }

  Future<void> assignDrone(String incidentId, String deviceId) async {
    try {
      final updated = await _repository.assignDevice(incidentId: incidentId, deviceId: deviceId);
      _replaceIncident(updated);
    } catch (_) {
      state = state.copyWith(error: 'Failed to assign drone.');
    }
  }

  Future<void> dispatchSarGrid(String incidentId) async {
    try {
      final updated = await _repository.dispatchSarGrid(incidentId);
      _replaceIncident(updated);
      final grid = updated.sarGrid;
      if (grid.isNotEmpty) {
        _ref.read(sarGridProvider.notifier).applyResult(SarGridResult.fromJson(grid));
      }
    } catch (_) {
      state = state.copyWith(error: 'Failed to dispatch SAR grid.');
    }
  }

  Future<void> resolveIncident(String incidentId) async {
    try {
      final updated = await _repository.resolveIncident(incidentId);
      _replaceIncident(updated);
    } catch (_) {
      state = state.copyWith(error: 'Failed to resolve incident.');
    }
  }

  void _replaceIncident(SarIncident updated) {
    final next = state.incidents.map((i) => i.id == updated.id ? updated : i).toList();
    state = state.copyWith(incidents: next, clearError: true);
  }
}

final sarIncidentProvider = StateNotifierProvider<SarIncidentNotifier, SarIncidentState>((ref) {
  return SarIncidentNotifier(ref.watch(sarIncidentRepositoryProvider), ref);
});
