import 'package:dio/dio.dart';

import '../../../core/network/api_client.dart';
import '../models/gateway_models.dart';

class HardwareRepository {
  HardwareRepository({ApiClient? apiClient}) : _api = (apiClient ?? ApiClient()).dio;

  final Dio _api;

  Future<GatewayStatus> fetchGatewayStatus() async {
    try {
      final response = await _api.get('/api/v1/hardware/gateway-status');
      return GatewayStatus.fromJson(response.data as Map<String, dynamic>);
    } catch (_) {
      return GatewayStatus.disconnected;
    }
  }
}
