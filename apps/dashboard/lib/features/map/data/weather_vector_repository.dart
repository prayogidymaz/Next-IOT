import 'package:dio/dio.dart';

import '../../../core/network/api_client.dart';
import '../models/weather_vector_models.dart';

class WeatherVectorRepository {
  WeatherVectorRepository({ApiClient? apiClient}) : _api = (apiClient ?? ApiClient()).dio;

  final Dio _api;

  Future<WeatherVectorData> fetchWeatherVector({
    required double lat,
    required double lon,
    double radiusM = 2000,
  }) async {
    final response = await _api.get(
      '/api/v1/telemetry/weather-vector',
      queryParameters: {
        'lat': lat,
        'lon': lon,
        'radius': radiusM,
      },
    );
    return WeatherVectorData.fromJson(response.data as Map<String, dynamic>);
  }
}
