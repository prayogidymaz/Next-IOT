import 'package:dio/dio.dart';

import '../../../core/network/api_client.dart';
import '../models/device_models.dart';
import '../models/ota_models.dart';

class DeviceRepository {
  DeviceRepository({ApiClient? apiClient})
      : _api = (apiClient ?? ApiClient()).dio;

  final Dio _api;

  Future<List<Device>> fetchDevices() async {
    final response = await _api.get('/api/v1/devices');
    final data = response.data as List<dynamic>;
    return data
        .map((item) => Device.fromJson(item as Map<String, dynamic>))
        .toList();
  }

  Future<RegisterDeviceResult> registerDevice(
      RegisterDeviceRequest request) async {
    final response = await _api.post('/api/v1/devices', data: request.toJson());
    return RegisterDeviceResult.fromJson(response.data as Map<String, dynamic>);
  }

  Future<BulkImportResult> bulkImportJson(Map<String, dynamic> payload) async {
    final response =
        await _api.post('/api/v1/devices/bulk-import', data: payload);
    return BulkImportResult.fromJson(response.data as Map<String, dynamic>);
  }

  Future<BulkImportResult> bulkImportFile({
    required String filename,
    required List<int> bytes,
  }) async {
    final form = FormData.fromMap({
      'file': MultipartFile.fromBytes(bytes, filename: filename),
    });
    final response = await _api.post('/api/v1/devices/bulk-import', data: form);
    return BulkImportResult.fromJson(response.data as Map<String, dynamic>);
  }
}
