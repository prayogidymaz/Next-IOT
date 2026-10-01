import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../alerts/providers/alert_provider.dart';
import '../../devices/models/device_models.dart';
import '../../devices/providers/device_provider.dart';
import '../../telemetry/data/telemetry_repository.dart';
import '../../telemetry/models/telemetry_stream_event.dart';
import '../models/device_map_models.dart';
import '../utils/gps_utils.dart';

final telemetryRepositoryProvider =
    Provider<TelemetryRepository>((ref) => TelemetryRepository());

class TacticalMapState {
  const TacticalMapState({
    this.markers = const [],
    this.selectedDeviceId,
    this.isLoading = false,
    this.error,
  });

  final List<DeviceMapMarker> markers;
  final String? selectedDeviceId;
  final bool isLoading;
  final String? error;

  DeviceMapMarker? get selected {
    if (selectedDeviceId == null) return null;
    for (final marker in markers) {
      if (marker.device.id == selectedDeviceId) return marker;
    }
    return null;
  }

  TacticalMapState copyWith({
    List<DeviceMapMarker>? markers,
    String? selectedDeviceId,
    bool? isLoading,
    String? error,
    bool clearError = false,
    bool clearSelection = false,
  }) {
    return TacticalMapState(
      markers: markers ?? this.markers,
      selectedDeviceId:
          clearSelection ? null : (selectedDeviceId ?? this.selectedDeviceId),
      isLoading: isLoading ?? this.isLoading,
      error: clearError ? null : (error ?? this.error),
    );
  }
}

class TacticalMapNotifier extends StateNotifier<TacticalMapState> {
  TacticalMapNotifier(this._ref) : super(const TacticalMapState());

  final Ref _ref;

  Future<void> loadMarkers(
      {List<Device>? devicesOverride, bool silent = false}) async {
    if (!silent) {
      state = state.copyWith(isLoading: true, clearError: true);
    }

    try {
      var devices = devicesOverride ?? _ref.read(deviceProvider).devices;
      if (devices.isEmpty) {
        await _ref.read(deviceProvider.notifier).loadDevices();
        devices = _ref.read(deviceProvider).devices;
      }

      if (devices.isEmpty) {
        state = state.copyWith(markers: const [], isLoading: false);
        return;
      }

      final alertDeviceIds =
          _ref.read(alertProvider).activeAlerts.map((a) => a.deviceId).toSet();
      final repo = _ref.read(telemetryRepositoryProvider);

      final markerResults = await Future.wait(
        devices.map((device) => _loadMarkerForDevice(
              device: device,
              repo: repo,
              hasActiveAlert: alertDeviceIds.contains(device.id),
            )),
      );

      final markers = markerResults.whereType<DeviceMapMarker>().toList()
        ..sort((a, b) => a.device.name.compareTo(b.device.name));

      state = TacticalMapState(
        markers: markers,
        selectedDeviceId: state.selectedDeviceId,
        isLoading: false,
      );
    } catch (_) {
      if (!silent) {
        state = state.copyWith(
            isLoading: false, error: 'Failed to load map telemetry.');
      }
    }
  }

  Future<void> refreshMarkersSilent() => loadMarkers(silent: true);

  Future<DeviceMapMarker?> _loadMarkerForDevice({
    required Device device,
    required TelemetryRepository repo,
    required bool hasActiveAlert,
  }) async {
    try {
      final latest = await repo.fetchResolvableLatest(device.id);
      return buildMapMarker(
        device: device,
        telemetry: latest,
        hasActiveAlert: hasActiveAlert,
        allowDefaultCoordinates: true,
      );
    } catch (_) {
      return null;
    }
  }

  Device? _deviceById(String deviceId) {
    for (final d in _ref.read(deviceProvider).devices) {
      if (d.id == deviceId) return d;
    }
    return null;
  }

  Device? _deviceForStream(String deviceId, String? status) {
    final base = _deviceById(deviceId);
    if (base == null) return null;
    if (status == null || base.status == status) return base;
    return Device(
      id: base.id,
      tenantId: base.tenantId,
      name: base.name,
      deviceType: base.deviceType,
      status: status,
      lastSeenAt: DateTime.now().toUtc(),
      createdAt: base.createdAt,
    );
  }

  void selectDevice(String? deviceId) {
    state = state.copyWith(
      selectedDeviceId: deviceId,
      clearSelection: deviceId == null,
    );
  }

  void applyStreamEvent(TelemetryStreamEvent event) {
    if (event.metrics.isEmpty) return;

    final alertDeviceIds =
        _ref.read(alertProvider).activeAlerts.map((a) => a.deviceId).toSet();
    final hasActiveAlert = alertDeviceIds.contains(event.deviceId);

    final index =
        state.markers.indexWhere((m) => m.device.id == event.deviceId);
    if (index >= 0) {
      final device = _deviceForStream(event.deviceId, event.status) ??
          state.markers[index].device;
      final updated = applyStreamMetricsToMarker(
        marker: state.markers[index].copyWith(device: device),
        metrics: event.metrics,
        recordedAt: event.recordedAt,
      );
      if (updated == null) return;
      final markers = [...state.markers];
      markers[index] = updated;
      state = state.copyWith(markers: markers);
      return;
    }

    final device = _deviceForStream(event.deviceId, event.status);
    if (device == null) return;

    final fix = resolveGpsFix(event.metrics, allowDefaultFallback: true);
    if (fix == null) return;

    final marker = buildMapMarkerFromMetrics(
      device: device,
      metrics: event.metrics,
      fix: fix,
      hasActiveAlert: hasActiveAlert,
      recordedAt: event.recordedAt,
    );

    state = state.copyWith(
      markers: [...state.markers, marker]
        ..sort((a, b) => a.device.name.compareTo(b.device.name)),
    );
  }
}

final tacticalMapProvider =
    StateNotifierProvider<TacticalMapNotifier, TacticalMapState>((ref) {
  return TacticalMapNotifier(ref);
});
