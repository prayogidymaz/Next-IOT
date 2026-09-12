import 'dart:io';

import 'package:dio/dio.dart';
import 'package:path_provider/path_provider.dart';

import '../../../core/network/api_client.dart';
import '../models/telemetry_analytics_models.dart';
import '../models/telemetry_models.dart';

class TelemetryRepository {
  TelemetryRepository({ApiClient? apiClient}) : _api = (apiClient ?? ApiClient()).dio;

  final Dio _api;

  Future<TelemetryLatest> fetchLatest(String deviceId) async {
    final response = await _api.get('/api/v1/devices/$deviceId/telemetry/latest');
    return TelemetryLatest.fromJson(response.data as Map<String, dynamic>);
  }

  /// Latest from Redis cache, falling back to most recent DB reading (any device status).
  Future<TelemetryLatest?> fetchResolvableLatest(String deviceId) async {
    try {
      return await fetchLatest(deviceId);
    } on DioException catch (e) {
      if (e.response?.statusCode != 404) rethrow;
    }

    final now = DateTime.now().toUtc();
    final history = await fetchHistory(
      deviceId,
      startTime: now.subtract(const Duration(days: 30)),
      endTime: now,
      limit: 1,
    );
    if (history.items.isEmpty) return null;

    final item = history.items.first;
    return TelemetryLatest(
      deviceId: deviceId,
      readingId: item.readingId,
      recordedAt: item.recordedAt,
      metrics: item.metrics,
      source: 'history',
    );
  }

  Future<TelemetryHistory> fetchHistory(
    String deviceId, {
    required DateTime startTime,
    required DateTime endTime,
    required int limit,
  }) async {
    final response = await _api.get(
      '/api/v1/devices/$deviceId/telemetry/history',
      queryParameters: {
        'start_time': startTime.toUtc().toIso8601String(),
        'end_time': endTime.toUtc().toIso8601String(),
        'limit': limit,
      },
    );
    return TelemetryHistory.fromJson(response.data as Map<String, dynamic>);
  }

  Future<TelemetryAnalytics> fetchAnalytics({
    required String deviceId,
    int hours = 24,
  }) async {
    final response = await _api.get(
      '/api/v1/telemetry/analytics',
      queryParameters: {'device_id': deviceId, 'hours': hours},
    );
    return TelemetryAnalytics.fromJson(response.data as Map<String, dynamic>);
  }

  Future<String> downloadExport({
    required String deviceId,
    required TelemetryExportFormat format,
    int hours = 24,
  }) async {
    final response = await _api.get<List<int>>(
      '/api/v1/telemetry/export',
      queryParameters: {
        'device_id': deviceId,
        'format': format.apiValue,
        'hours': hours,
      },
      options: Options(responseType: ResponseType.bytes),
    );

    final bytes = response.data ?? [];
    final dir = await getDownloadsDirectory() ?? await getApplicationDocumentsDirectory();
    final timestamp = DateTime.now().toUtc().toIso8601String().replaceAll(':', '-');
    final filename = 'telemetry_${deviceId.substring(0, 8)}_${hours}h_$timestamp${format.extension}';
    final file = File('${dir.path}/$filename');
    await file.writeAsBytes(bytes, flush: true);
    return file.path;
  }
}
