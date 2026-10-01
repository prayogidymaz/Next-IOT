import 'package:dio/dio.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../data/ota_repository.dart';
import '../models/ota_models.dart';

final otaRepositoryProvider = Provider<OtaRepository>((ref) => OtaRepository());

class OtaFirmwareState {
  const OtaFirmwareState({
    this.releases = const [],
    this.rolloutsByRelease = const {},
    this.isLoading = false,
    this.isUploading = false,
    this.error,
    this.selectedReleaseId,
  });

  final List<FirmwareRelease> releases;
  final Map<String, List<OtaRolloutRow>> rolloutsByRelease;
  final bool isLoading;
  final bool isUploading;
  final String? error;
  final String? selectedReleaseId;

  OtaFirmwareState copyWith({
    List<FirmwareRelease>? releases,
    Map<String, List<OtaRolloutRow>>? rolloutsByRelease,
    bool? isLoading,
    bool? isUploading,
    String? error,
    String? selectedReleaseId,
    bool clearError = false,
  }) {
    return OtaFirmwareState(
      releases: releases ?? this.releases,
      rolloutsByRelease: rolloutsByRelease ?? this.rolloutsByRelease,
      isLoading: isLoading ?? this.isLoading,
      isUploading: isUploading ?? this.isUploading,
      error: clearError ? null : (error ?? this.error),
      selectedReleaseId: selectedReleaseId ?? this.selectedReleaseId,
    );
  }
}

class OtaFirmwareNotifier extends StateNotifier<OtaFirmwareState> {
  OtaFirmwareNotifier(this._repo) : super(const OtaFirmwareState());

  final OtaRepository _repo;

  Future<void> load() async {
    state = state.copyWith(isLoading: true, clearError: true);
    try {
      final releases = await _repo.fetchReleases();
      state = state.copyWith(releases: releases, isLoading: false);
    } catch (e) {
      state = state.copyWith(isLoading: false, error: _mapError(e));
    }
  }

  Future<void> uploadAndPublish({
    required String version,
    required String targetCategory,
    required String filename,
    required List<int> bytes,
  }) async {
    state = state.copyWith(isUploading: true, clearError: true);
    try {
      final release = await _repo.uploadRelease(
        version: version,
        targetDeviceCategory: targetCategory,
        filename: filename,
        bytes: bytes,
      );
      await _repo.publishRelease(release.id);
      await load();
      await loadRollouts(release.id);
      state = state.copyWith(isUploading: false, selectedReleaseId: release.id);
    } catch (e) {
      state = state.copyWith(isUploading: false, error: _mapError(e));
    }
  }

  Future<void> loadRollouts(String releaseId) async {
    try {
      final rows = await _repo.fetchRollouts(releaseId);
      state = state.copyWith(
        rolloutsByRelease: {...state.rolloutsByRelease, releaseId: rows},
        selectedReleaseId: releaseId,
      );
    } catch (e) {
      state = state.copyWith(error: _mapError(e));
    }
  }

  String _mapError(Object e) {
    if (e is DioException) {
      final data = e.response?.data;
      if (data is Map && data['detail'] != null) return data['detail'].toString();
      return e.message ?? 'Request failed';
    }
    return e.toString();
  }
}

final otaFirmwareProvider =
    StateNotifierProvider<OtaFirmwareNotifier, OtaFirmwareState>((ref) {
  return OtaFirmwareNotifier(ref.watch(otaRepositoryProvider));
});
