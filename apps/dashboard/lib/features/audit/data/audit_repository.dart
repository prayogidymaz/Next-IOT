import 'package:dio/dio.dart';

import '../../../core/network/api_client.dart';
import '../models/audit_log_models.dart';

class AuditRepository {
  AuditRepository({ApiClient? apiClient})
      : _api = (apiClient ?? ApiClient()).dio;

  final Dio _api;

  Future<AuditLogPage> fetchLogs({
    String? action,
    String? actor,
    int page = 1,
    int pageSize = 50,
  }) async {
    final response = await _api.get(
      '/api/v1/audit-logs',
      queryParameters: {
        if (action != null && action.isNotEmpty) 'action': action,
        if (actor != null && actor.isNotEmpty) 'actor': actor,
        'page': page,
        'page_size': pageSize,
      },
    );
    return AuditLogPage.fromJson(response.data as Map<String, dynamic>);
  }

  Future<List<int>> downloadExportCsv({String? action, String? actor}) async {
    final response = await _api.get<List<int>>(
      '/api/v1/audit-logs/export',
      queryParameters: {
        if (action != null && action.isNotEmpty) 'action': action,
        if (actor != null && actor.isNotEmpty) 'actor': actor,
      },
      options: Options(responseType: ResponseType.bytes),
    );
    return response.data ?? [];
  }
}
