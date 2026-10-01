import 'package:dio/dio.dart';

import '../models/field_api_models.dart';
import '../storage/token_storage.dart';

class FieldApiClient {
  FieldApiClient(this._tokens) : _dio = Dio(BaseOptions(connectTimeout: const Duration(seconds: 12)));

  final TokenStorage _tokens;
  final Dio _dio;

  Future<void> _authHeaders() async {
    final base = await _tokens.readApiBaseUrl();
    final token = await _tokens.readAccessToken();
    _dio.options.baseUrl = base.replaceAll(RegExp(r'/$'), '');
    _dio.options.headers = {
      'Accept': 'application/json',
      'Content-Type': 'application/json',
      if (token != null) 'Authorization': 'Bearer $token',
    };
  }

  Future<List<FleetDeviceDto>> listDevices() async {
    await _authHeaders();
    final res = await _dio.get<List<Object?>>('/api/v1/devices');
    final data = res.data ?? const [];
    return data
        .whereType<Map<Object?, Object?>>()
        .map((row) => FleetDeviceDto.fromJson(row.map((k, v) => MapEntry(k.toString(), v))))
        .toList();
  }

  Future<Map<String, Object?>> login(String email, String password) async {
    await _authHeaders();
    final res = await _dio.post<Map<String, Object?>>(
      '/auth/login',
      data: {'email': email, 'password': password},
    );
    return res.data ?? const {};
  }

  Future<Map<String, Object?>> dispatchRelayCommand({
    required String deviceId,
    required bool on,
    required String channel,
  }) async {
    await _authHeaders();
    final res = await _dio.post<Map<String, Object?>>(
      '/api/v1/devices/$deviceId/commands',
      data: {
        'command_type': on ? 'RELAY_ON' : 'RELAY_OFF',
        'params': {'channel': channel},
      },
    );
    return res.data ?? const {};
  }

  Future<TelemetryBulkResponse> pushTelemetryBulk({
    required List<Map<String, Object?>> items,
  }) async {
    await _authHeaders();
    final res = await _dio.post<Map<String, Object?>>(
      '/api/v1/telemetry/bulk',
      data: {'items': items},
    );
    return TelemetryBulkResponse.fromJson(res.data ?? const {});
  }

  Future<void> pushTelemetry({
    required Map<String, Object?> metrics,
    String? deviceBasicAuth,
  }) async {
    await _authHeaders();
    final headers = Map<String, Object?>.from(_dio.options.headers);
    if (deviceBasicAuth != null) {
      headers['Authorization'] = deviceBasicAuth;
    }
    await _dio.post<void>(
      '/api/v1/telemetry',
      data: {
        'timestamp': DateTime.now().toUtc().toIso8601String(),
        'metrics': metrics,
      },
      options: Options(headers: headers),
    );
  }
}
