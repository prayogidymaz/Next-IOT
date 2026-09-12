import 'package:dio/dio.dart';

import '../../../core/network/api_client.dart';
import '../models/geofence_models.dart';

class GeofenceRepository {
  GeofenceRepository({ApiClient? apiClient}) : _api = (apiClient ?? ApiClient()).dio;

  final Dio _api;

  Future<GeofenceListData> fetchZones() async {
    final response = await _api.get('/api/v1/mission/geofence');
    return GeofenceListData.fromJson(response.data as Map<String, dynamic>);
  }

  Future<GeofenceZone> createZone({
    required String name,
    required List<GeofencePoint> polygonCoords,
    double minAltitude = 0,
    double maxAltitude = 120,
    GeofenceAction actionOnBreach = GeofenceAction.warn,
  }) async {
    final response = await _api.post(
      '/api/v1/mission/geofence',
      data: {
        'name': name,
        'polygon_coords': polygonCoords.map((p) => p.toJson()).toList(),
        'min_altitude': minAltitude,
        'max_altitude': maxAltitude,
        'action_on_breach': actionOnBreach.apiValue,
      },
    );
    return GeofenceZone.fromJson(response.data as Map<String, dynamic>);
  }
}
