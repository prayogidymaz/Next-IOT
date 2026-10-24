import "package:dio/dio.dart";

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

  Map<String, String> _headers({bool json = false}) {
    final headers = <String, String>{"Accept": "application/json"};
    if (json) {
      headers["Content-Type"] = "application/json";
    }
    if (_jwt != null) {
      headers["Authorization"] = "Bearer $_jwt";
    }
    return headers;
  }

  Future<List<Map<String, dynamic>>> getFarms() async {
    final res = await _client.get<List<dynamic>>(
      "$_baseUrl/api/agriculture/farms",
      options: Options(headers: _headers()),
    );
    final data = res.data;
    if (data == null) {
      return [];
    }
    return data.cast<Map<String, dynamic>>();
  }

  Future<List<Map<String, dynamic>>> getSensors(String farmId) async {
    final res = await _client.get<Map<String, dynamic>>(
      "$_baseUrl/api/agriculture/farms/$farmId/map-data",
      options: Options(headers: _headers()),
    );
    final sensors = res.data?["sensors"];
    if (sensors is List) {
      return sensors.cast<Map<String, dynamic>>();
    }
    return [];
  }

  Future<List<Map<String, dynamic>>> getAlerts() async {
    final res = await _client.get<List<dynamic>>(
      "$_baseUrl/api/v1/alarms",
      options: Options(headers: _headers()),
    );
    final data = res.data;
    if (data is List) {
      return data.cast<Map<String, dynamic>>();
    }
    return [];
  }

  Future<void> postIrrigation(String valveId, String action) async {
    await _client.post<void>(
      "$_baseUrl/api/agriculture/valves/$valveId/$action",
      options: Options(headers: _headers(json: true)),
    );
  }

  Future<void> acknowledgeAlarm(String alarmId) async {
    await _client.post<void>(
      "$_baseUrl/api/v1/alarms/$alarmId/acknowledge",
      data: {},
      options: Options(headers: _headers(json: true)),
    );
  }

  Future<void> publishUserAcknowledged({
    required String deviceId,
    required String alertId,
  }) async {
    await _client.post<void>(
      "$_baseUrl/api/v1/mesh/events",
      data: {
        "device_id": deviceId,
        "domain": "ui",
        "event_type": "user_acknowledged",
        "payload": {"alert_id": alertId},
      },
      options: Options(headers: _headers(json: true)),
    );
  }

  Future<void> registerFcmToken(String token) async {
    await _client.post<void>(
      "$_baseUrl/api/v1/notifications/fcm/register",
      data: {"token": token, "device_type": "wear"},
      options: Options(headers: _headers(json: true)),
    );
  }
}
