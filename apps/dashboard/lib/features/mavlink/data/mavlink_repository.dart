import 'package:dio/dio.dart';

import '../../../core/network/api_client.dart';
import '../models/mavlink_models.dart';

class MavlinkRepository {
  MavlinkRepository({ApiClient? apiClient}) : _api = (apiClient ?? ApiClient()).dio;

  final Dio _api;

  Future<MavlinkStatus> fetchStatus(String deviceId) async {
    final response = await _api.get(
      '/api/v1/hardware/mavlink/status',
      queryParameters: {'device_id': deviceId},
    );
    return MavlinkStatus.fromJson(response.data as Map<String, dynamic>);
  }
}
