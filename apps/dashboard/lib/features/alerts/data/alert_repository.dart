import 'package:dio/dio.dart';

import '../../../core/network/api_client.dart';
import '../models/alert_models.dart';

class AlertRepository {
  AlertRepository({ApiClient? apiClient}) : _api = (apiClient ?? ApiClient()).dio;

  final Dio _api;

  Future<AlertList> fetchAlerts({String? status, int limit = 50}) async {
    final response = await _api.get(
      '/api/v1/alerts',
      queryParameters: {
        if (status != null) 'status': status,
        'limit': limit,
      },
    );
    return AlertList.fromJson(response.data as Map<String, dynamic>);
  }

  Future<AlertSummary> fetchSummary({int limit = 5}) async {
    final response = await _api.get(
      '/api/v1/alerts/summary',
      queryParameters: {'limit': limit},
    );
    return AlertSummary.fromJson(response.data as Map<String, dynamic>);
  }
}
