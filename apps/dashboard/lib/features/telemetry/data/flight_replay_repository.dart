import 'package:dio/dio.dart';

import '../../../core/network/api_client.dart';
import '../models/flight_replay_models.dart';

class FlightReplayRepository {
  FlightReplayRepository({ApiClient? apiClient}) : _api = (apiClient ?? ApiClient()).dio;

  final Dio _api;

  Future<FlightReplayData> fetchReplay({
    required String deviceId,
    int hours = 24,
    DateTime? startTime,
    DateTime? endTime,
  }) async {
    final params = <String, dynamic>{
      'device_id': deviceId,
      if (startTime == null && endTime == null) 'hours': hours,
      if (startTime != null) 'start_time': startTime.toUtc().toIso8601String(),
      if (endTime != null) 'end_time': endTime.toUtc().toIso8601String(),
    };

    final response = await _api.get('/api/v1/telemetry/flight-replay', queryParameters: params);
    return FlightReplayData.fromJson(response.data as Map<String, dynamic>);
  }
}
