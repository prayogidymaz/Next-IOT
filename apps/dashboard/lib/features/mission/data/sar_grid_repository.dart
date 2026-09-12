import 'package:dio/dio.dart';

import '../../../core/network/api_client.dart';
import '../models/sar_grid_models.dart';

class SarGridRepository {
  SarGridRepository({ApiClient? apiClient}) : _api = (apiClient ?? ApiClient()).dio;

  final Dio _api;

  Future<SarGridResult> generateGrid({
    required double lkpLat,
    required double lkpLon,
    required double radiusM,
    SarGridPattern pattern = SarGridPattern.expandingSquare,
    double legSpacingM = 100,
  }) async {
    final response = await _api.post(
      '/api/v1/mission/sar-grid',
      data: {
        'lkp_lat': lkpLat,
        'lkp_lon': lkpLon,
        'radius_m': radiusM,
        'pattern': pattern.apiValue,
        'leg_spacing_m': legSpacingM,
      },
    );
    return SarGridResult.fromJson(response.data as Map<String, dynamic>);
  }
}
