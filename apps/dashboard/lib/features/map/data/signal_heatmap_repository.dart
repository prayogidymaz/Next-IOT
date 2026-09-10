import 'package:dio/dio.dart';

import '../../../core/network/api_client.dart';
import '../models/signal_heatmap_models.dart';

class SignalHeatmapRepository {
  SignalHeatmapRepository({ApiClient? apiClient}) : _api = (apiClient ?? ApiClient()).dio;

  final Dio _api;

  Future<SignalHeatmapData> fetchHeatmap({
    required String deviceId,
    int hours = 24,
  }) async {
    final response = await _api.get(
      '/api/v1/telemetry/signal-heatmap',
      queryParameters: {
        'device_id': deviceId,
        'hours': hours,
      },
    );
    return SignalHeatmapData.fromJson(response.data as Map<String, dynamic>);
  }
}
