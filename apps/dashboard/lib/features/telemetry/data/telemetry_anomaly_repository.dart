import 'package:dio/dio.dart';

import '../../../core/network/api_client.dart';
import '../models/telemetry_anomaly_models.dart';

class TelemetryAnomalyRepository {
  TelemetryAnomalyRepository({ApiClient? apiClient}) : _api = (apiClient ?? ApiClient()).dio;

  final Dio _api;

  Future<TelemetryAnomalyList> fetchAnomalies({
    required String deviceId,
    int hours = 24,
  }) async {
    final response = await _api.get(
      '/api/v1/telemetry/anomalies',
      queryParameters: {
        'device_id': deviceId,
        'hours': hours,
      },
    );
    return TelemetryAnomalyList.fromJson(response.data as Map<String, dynamic>);
  }
}
