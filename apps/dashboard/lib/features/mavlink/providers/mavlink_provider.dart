import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../map/models/device_map_models.dart';
import '../data/mavlink_repository.dart';
import '../models/mavlink_models.dart';

final mavlinkRepositoryProvider = Provider<MavlinkRepository>((ref) => MavlinkRepository());

class MavlinkState {
  const MavlinkState({
    this.status,
    this.isLoading = false,
    this.error,
    this.deviceId,
  });

  final MavlinkStatus? status;
  final bool isLoading;
  final String? error;
  final String? deviceId;

  bool get isConnected => status?.connected ?? false;

  MavlinkState copyWith({
    MavlinkStatus? status,
    bool? isLoading,
    String? error,
    String? deviceId,
    bool clearError = false,
  }) {
    return MavlinkState(
      status: status ?? this.status,
      isLoading: isLoading ?? this.isLoading,
      error: clearError ? null : (error ?? this.error),
      deviceId: deviceId ?? this.deviceId,
    );
  }
}

class MavlinkNotifier extends StateNotifier<MavlinkState> {
  MavlinkNotifier(this._repository) : super(const MavlinkState());

  final MavlinkRepository _repository;

  Future<void> loadForDevice(String deviceId, {DeviceMapMarker? marker}) async {
    state = state.copyWith(isLoading: true, deviceId: deviceId, clearError: true);

    MavlinkStatus? markerStatus;
    if (marker != null) {
      markerStatus = _statusFromMarker(marker);
    }

    try {
      final remote = await _repository.fetchStatus(deviceId);
      final merged = MavlinkStatus(
        deviceId: deviceId,
        connected: remote.connected || (markerStatus?.connected ?? false),
        protocolVersion: remote.protocolVersion,
        autopilot: remote.autopilot ?? markerStatus?.autopilot,
        lastHeartbeatAt: remote.lastHeartbeatAt,
        metrics: {...?markerStatus?.metrics, ...remote.metrics},
      );
      state = state.copyWith(isLoading: false, status: merged);
    } catch (_) {
      if (markerStatus != null) {
        state = state.copyWith(isLoading: false, status: markerStatus);
      } else {
        state = state.copyWith(isLoading: false, error: 'Failed to load MAVLink status.');
      }
    }
  }

  void applyMarker(DeviceMapMarker marker) {
    if (state.deviceId != null && state.deviceId != marker.device.id) return;
    final markerStatus = _statusFromMarker(marker);
    if (!markerStatus.connected && state.status?.connected != true) return;
    state = state.copyWith(
      deviceId: marker.device.id,
      status: MavlinkStatus(
        deviceId: marker.device.id,
        connected: markerStatus.connected || (state.status?.connected ?? false),
        protocolVersion: markerStatus.protocolVersion,
        autopilot: state.status?.autopilot,
        metrics: {
          ...?state.status?.metrics,
          ...markerStatus.metrics,
          if (marker.roll != null) 'roll': marker.roll!,
          if (marker.pitch != null) 'pitch': marker.pitch!,
          if (marker.yaw != null) 'yaw': marker.yaw!,
        },
      ),
    );
  }

  MavlinkStatus _statusFromMarker(DeviceMapMarker marker) {
    final metrics = <String, double>{
      if (marker.roll != null) 'roll': marker.roll!,
      if (marker.pitch != null) 'pitch': marker.pitch!,
      if (marker.yaw != null) 'yaw': marker.yaw!,
      if (marker.battery != null) 'battery': marker.battery!,
    };
    return MavlinkStatus.fromMarkerMetrics(metrics);
  }

  void clear() => state = const MavlinkState();
}

final mavlinkProvider = StateNotifierProvider<MavlinkNotifier, MavlinkState>((ref) {
  return MavlinkNotifier(ref.watch(mavlinkRepositoryProvider));
});
