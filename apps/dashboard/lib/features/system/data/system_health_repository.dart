import 'package:dio/dio.dart';

import '../../../core/network/api_client.dart';
import '../models/system_health_models.dart';

class SystemHealthRepository {
  SystemHealthRepository({ApiClient? apiClient})
      : _api = (apiClient ?? ApiClient()).dio;

  final Dio _api;

  Future<SystemHealthSnapshot> fetchHealth() async {
    final response = await _api.get('/api/v1/system/health');
    return SystemHealthSnapshot.fromJson(response.data as Map<String, dynamic>);
  }
}
