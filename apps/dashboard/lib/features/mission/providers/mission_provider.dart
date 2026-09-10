import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:latlong2/latlong.dart';

import '../data/command_repository.dart';
import '../models/mission_models.dart';

final commandRepositoryProvider = Provider<CommandRepository>((ref) => CommandRepository());

class MissionPlannerState {
  const MissionPlannerState({
    this.plannerMode = false,
    this.waypoints = const [],
    this.altitudeM = 60,
    this.targetDeviceId,
    this.isDispatching = false,
    this.feedback,
  });

  static const minAltitude = 50.0;
  static const maxAltitude = 80.0;

  final bool plannerMode;
  final List<MissionWaypoint> waypoints;
  final double altitudeM;
  final String? targetDeviceId;
  final bool isDispatching;
  final String? feedback;

  MissionPlannerState copyWith({
    bool? plannerMode,
    List<MissionWaypoint>? waypoints,
    double? altitudeM,
    String? targetDeviceId,
    bool? isDispatching,
    String? feedback,
    bool clearFeedback = false,
  }) {
    return MissionPlannerState(
      plannerMode: plannerMode ?? this.plannerMode,
      waypoints: waypoints ?? this.waypoints,
      altitudeM: altitudeM ?? this.altitudeM,
      targetDeviceId: targetDeviceId ?? this.targetDeviceId,
      isDispatching: isDispatching ?? this.isDispatching,
      feedback: clearFeedback ? null : (feedback ?? this.feedback),
    );
  }
}

class MissionPlannerNotifier extends StateNotifier<MissionPlannerState> {
  MissionPlannerNotifier(this._repository) : super(const MissionPlannerState());

  final CommandRepository _repository;
  int _waypointCounter = 0;

  void togglePlannerMode() {
    state = state.copyWith(plannerMode: !state.plannerMode, clearFeedback: true);
  }

  void setTargetDevice(String? deviceId) {
    state = state.copyWith(targetDeviceId: deviceId, clearFeedback: true);
  }

  void setAltitude(double value) {
    final clamped = value.clamp(MissionPlannerState.minAltitude, MissionPlannerState.maxAltitude);
    state = state.copyWith(altitudeM: clamped);
  }

  void addWaypoint(LatLng point) {
    if (!state.plannerMode) return;
    _waypointCounter += 1;
    final wp = MissionWaypoint(
      id: 'wp-$_waypointCounter',
      sequence: state.waypoints.length + 1,
      latitude: point.latitude,
      longitude: point.longitude,
    );
    state = state.copyWith(
      waypoints: [...state.waypoints, wp],
      clearFeedback: true,
    );
  }

  void removeWaypoint(String id) {
    final updated = state.waypoints.where((w) => w.id != id).toList();
    state = state.copyWith(
      waypoints: _resequence(updated),
      clearFeedback: true,
    );
  }

  void moveWaypointUp(String id) {
    final list = [...state.waypoints];
    final index = list.indexWhere((w) => w.id == id);
    if (index <= 0) return;
    final item = list.removeAt(index);
    list.insert(index - 1, item);
    state = state.copyWith(waypoints: _resequence(list), clearFeedback: true);
  }

  void moveWaypointDown(String id) {
    final list = [...state.waypoints];
    final index = list.indexWhere((w) => w.id == id);
    if (index < 0 || index >= list.length - 1) return;
    final item = list.removeAt(index);
    list.insert(index + 1, item);
    state = state.copyWith(waypoints: _resequence(list), clearFeedback: true);
  }

  void clearMission() {
    state = state.copyWith(waypoints: const [], clearFeedback: true);
  }

  List<MissionWaypoint> _resequence(List<MissionWaypoint> list) {
    return [
      for (var i = 0; i < list.length; i++)
        list[i].copyWith(sequence: i + 1),
    ];
  }

  Future<void> dispatchMission() async {
    final deviceId = state.targetDeviceId;
    if (deviceId == null) {
      state = state.copyWith(feedback: 'Select a target device first.');
      return;
    }
    if (state.waypoints.isEmpty) {
      state = state.copyWith(feedback: 'Add at least one waypoint.');
      return;
    }

    state = state.copyWith(isDispatching: true, clearFeedback: true);
    try {
      final result = await _repository.dispatchCommand(
        deviceId: deviceId,
        commandType: DeviceCommandType.goToMission,
        params: {
          'altitude_m': state.altitudeM,
          'waypoints': state.waypoints.map((w) => w.toCommandJson()).toList(),
        },
      );
      state = state.copyWith(
        isDispatching: false,
        feedback: 'Mission dispatched (${result.status}).',
      );
    } catch (_) {
      state = state.copyWith(
        isDispatching: false,
        feedback: 'Failed to dispatch mission.',
      );
    }
  }

  Future<void> emergencyRtl() async {
    final deviceId = state.targetDeviceId;
    if (deviceId == null) {
      state = state.copyWith(feedback: 'Select a target device first.');
      return;
    }

    state = state.copyWith(isDispatching: true, clearFeedback: true);
    try {
      final result = await _repository.dispatchCommand(
        deviceId: deviceId,
        commandType: DeviceCommandType.rtl,
      );
      state = state.copyWith(
        isDispatching: false,
        feedback: 'Emergency RTL sent (${result.status}).',
      );
    } catch (_) {
      state = state.copyWith(
        isDispatching: false,
        feedback: 'Failed to send RTL command.',
      );
    }
  }
}

final missionPlannerProvider =
    StateNotifierProvider<MissionPlannerNotifier, MissionPlannerState>((ref) {
  return MissionPlannerNotifier(ref.watch(commandRepositoryProvider));
});
