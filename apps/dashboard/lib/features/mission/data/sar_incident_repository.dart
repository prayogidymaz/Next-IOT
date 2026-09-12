import 'package:dio/dio.dart';

import '../../../core/network/api_client.dart';
import '../models/sar_incident_models.dart';

class SarIncidentRepository {
  SarIncidentRepository({ApiClient? apiClient}) : _api = (apiClient ?? ApiClient()).dio;

  final Dio _api;

  Future<SarIncidentListData> fetchIncidents({String? status}) async {
    final response = await _api.get(
      '/api/v1/mission/sar-incidents',
      queryParameters: status != null ? {'status': status} : null,
    );
    return SarIncidentListData.fromJson(response.data as Map<String, dynamic>);
  }

  Future<SarIncident> createIncident({
    required SarIncidentType incidentType,
    required double targetLat,
    required double targetLon,
    String severity = 'critical',
    String? assignedDeviceId,
    String? message,
  }) async {
    final response = await _api.post(
      '/api/v1/mission/sar-incidents',
      data: {
        'incident_type': incidentType.apiValue,
        'target_lat': targetLat,
        'target_lon': targetLon,
        'severity': severity,
        if (assignedDeviceId != null) 'assigned_device_id': assignedDeviceId,
        if (message != null) 'message': message,
      },
    );
    return SarIncident.fromJson(response.data as Map<String, dynamic>);
  }

  Future<SarIncident> assignDevice({
    required String incidentId,
    required String deviceId,
  }) async {
    final response = await _api.patch(
      '/api/v1/mission/sar-incidents/$incidentId',
      data: {'assigned_device_id': deviceId},
    );
    return SarIncident.fromJson(response.data as Map<String, dynamic>);
  }

  Future<SarIncident> dispatchSarGrid(String incidentId) async {
    final response = await _api.patch(
      '/api/v1/mission/sar-incidents/$incidentId',
      data: {'regenerate_grid': true},
    );
    return SarIncident.fromJson(response.data as Map<String, dynamic>);
  }

  Future<SarIncident> resolveIncident(String incidentId) async {
    final response = await _api.patch(
      '/api/v1/mission/sar-incidents/$incidentId',
      data: {'status': 'RESOLVED'},
    );
    return SarIncident.fromJson(response.data as Map<String, dynamic>);
  }
}
