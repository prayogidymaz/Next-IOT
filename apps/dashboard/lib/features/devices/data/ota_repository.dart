import 'package:dio/dio.dart';

import '../../../core/network/api_client.dart';
import '../models/ota_models.dart';

class OtaRepository {
  OtaRepository({ApiClient? apiClient}) : _api = (apiClient ?? ApiClient()).dio;

  final Dio _api;

  Future<List<FirmwareRelease>> fetchReleases() async {
    final response = await _api.get('/api/v1/ota/releases');
    final data = response.data as List<dynamic>;
    return data
        .map((e) => FirmwareRelease.fromJson(e as Map<String, dynamic>))
        .toList();
  }

  Future<FirmwareRelease> uploadRelease({
    required String version,
    required String targetDeviceCategory,
    required String filename,
    required List<int> bytes,
  }) async {
    final form = FormData.fromMap({
      'version': version,
      'target_device_category': targetDeviceCategory,
      'file': MultipartFile.fromBytes(bytes, filename: filename),
    });
    final response = await _api.post('/api/v1/ota/releases', data: form);
    return FirmwareRelease.fromJson(response.data as Map<String, dynamic>);
  }

  Future<void> publishRelease(String releaseId) async {
    await _api.post('/api/v1/ota/releases/$releaseId/publish');
  }

  Future<List<OtaRolloutRow>> fetchRollouts(String releaseId) async {
    final response = await _api.get('/api/v1/ota/releases/$releaseId/rollouts');
    final data = response.data as List<dynamic>;
    return data
        .map((e) => OtaRolloutRow.fromJson(e as Map<String, dynamic>))
        .toList();
  }
}
