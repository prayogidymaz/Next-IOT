import "package:dio/dio.dart";

/// Week 9-10 skeleton — methods return mock JSON until Week 11-12 wiring.
class MeshApi {
  MeshApi({Dio? client, String? baseUrl})
      : _client = client ?? Dio(),
        _baseUrl = baseUrl ?? const String.fromEnvironment(
          "WEAR_API_BASE",
          defaultValue: "http://10.0.2.2:8000",
        );

  final Dio _client;
  final String _baseUrl;
  String? _jwt;

  void setJwt(String token) {
    _jwt = token;
  }

  Map<String, String> _headers() {
    final headers = <String, String>{"Accept": "application/json"};
    if (_jwt != null) {
      headers["Authorization"] = "Bearer $_jwt";
    }
    return headers;
  }

  Future<List<Map<String, dynamic>>> getFarms() async {
    try {
      final res = await _client.get<List<dynamic>>(
        "$_baseUrl/api/agriculture/farms",
        options: Options(headers: _headers()),
      );
      final data = res.data;
      if (data == null) return _mockFarms();
      return data.cast<Map<String, dynamic>>();
    } catch (_) {
      return _mockFarms();
    }
  }

  Future<List<Map<String, dynamic>>> getSensors(String farmId) async {
    try {
      final res = await _client.get<Map<String, dynamic>>(
        "$_baseUrl/api/agriculture/farms/$farmId/map-data",
        options: Options(headers: _headers()),
      );
      final sensors = res.data?["sensors"];
      if (sensors is List) {
        return sensors.cast<Map<String, dynamic>>();
      }
    } catch (_) {
      /* skeleton fallback */
    }
    return _mockSensors();
  }

  Future<List<Map<String, dynamic>>> getAlerts() async {
    return _mockAlerts();
  }

  Future<void> postIrrigation(String valveId, String action) async {
    try {
      await _client.post<void>(
        "$_baseUrl/api/agriculture/valves/$valveId/$action",
        options: Options(headers: _headers()),
      );
    } catch (_) {
      /* mock no-op */
    }
  }

  List<Map<String, dynamic>> _mockFarms() => [
        {"id": "farm-1", "name": "Kopi Toraja Plot A"},
      ];

  List<Map<String, dynamic>> _mockSensors() => [
        {"name": "Soil moisture", "last_moisture": 42.5},
        {"name": "Air temp", "last_moisture": 28.1},
        {"name": "Humidity", "last_moisture": 76.0},
      ];

  List<Map<String, dynamic>> _mockAlerts() => [
        {
          "id": "a1",
          "title": "Intrusion plot A",
          "severity": "critical",
          "acknowledged": false,
        },
        {
          "id": "a2",
          "title": "Tank low sprayer-2",
          "severity": "major",
          "acknowledged": false,
        },
      ];
}
