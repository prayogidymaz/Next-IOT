import 'package:dio/dio.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../data/device_repository.dart';
import '../models/device_models.dart';

final deviceRepositoryProvider = Provider<DeviceRepository>((ref) => DeviceRepository());

class DeviceListState {
  const DeviceListState({
    this.devices = const [],
    this.isLoading = false,
    this.isRegistering = false,
    this.error,
    this.statusFilter = DeviceStatusFilter.all,
  });

  final List<Device> devices;
  final bool isLoading;
  final bool isRegistering;
  final String? error;
  final DeviceStatusFilter statusFilter;

  List<Device> get filteredDevices => filterDevices(devices, statusFilter);

  DeviceListState copyWith({
    List<Device>? devices,
    bool? isLoading,
    bool? isRegistering,
    String? error,
    DeviceStatusFilter? statusFilter,
    bool clearError = false,
  }) {
    return DeviceListState(
      devices: devices ?? this.devices,
      isLoading: isLoading ?? this.isLoading,
      isRegistering: isRegistering ?? this.isRegistering,
      error: clearError ? null : (error ?? this.error),
      statusFilter: statusFilter ?? this.statusFilter,
    );
  }
}

class DeviceNotifier extends StateNotifier<DeviceListState> {
  DeviceNotifier(this._repository) : super(const DeviceListState());

  final DeviceRepository _repository;

  Future<void> loadDevices() async {
    state = state.copyWith(isLoading: true, clearError: true);
    try {
      final devices = await _repository.fetchDevices();
      state = state.copyWith(devices: devices, isLoading: false);
    } catch (e) {
      state = state.copyWith(isLoading: false, error: _mapError(e));
    }
  }

  void setStatusFilter(DeviceStatusFilter filter) {
    state = state.copyWith(statusFilter: filter);
  }

  Future<RegisterDeviceResult?> registerDevice({
    required String name,
    required DeviceType deviceType,
  }) async {
    state = state.copyWith(isRegistering: true, clearError: true);
    try {
      final result = await _repository.registerDevice(
        RegisterDeviceRequest(name: name.trim(), deviceType: deviceType.apiValue),
      );
      state = state.copyWith(
        devices: [result.device, ...state.devices],
        isRegistering: false,
      );
      return result;
    } catch (e) {
      state = state.copyWith(isRegistering: false, error: _mapError(e));
      return null;
    }
  }

  String _mapError(Object e) {
    if (e is DioException) {
      final detail = e.response?.data;
      if (detail is Map && detail['detail'] != null) {
        return detail['detail'].toString();
      }
      if (e.response?.statusCode == 403) {
        return 'You do not have permission to register devices.';
      }
    }
    return 'Failed to load devices. Check your connection.';
  }
}

final deviceProvider = StateNotifierProvider<DeviceNotifier, DeviceListState>((ref) {
  return DeviceNotifier(ref.watch(deviceRepositoryProvider));
});
