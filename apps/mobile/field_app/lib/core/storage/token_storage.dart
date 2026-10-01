import 'package:flutter_secure_storage/flutter_secure_storage.dart';

class TokenStorage {
  TokenStorage({FlutterSecureStorage? storage})
      : _storage = storage ?? const FlutterSecureStorage();

  static const _accessKey = 'next_iot_field_access';
  static const _refreshKey = 'next_iot_field_refresh';
  static const _apiBaseKey = 'next_iot_field_api_base';

  final FlutterSecureStorage _storage;

  Future<void> saveTokens({required String access, required String refresh}) async {
    await _storage.write(key: _accessKey, value: access);
    await _storage.write(key: _refreshKey, value: refresh);
  }

  Future<String?> readAccessToken() => _storage.read(key: _accessKey);

  Future<void> clear() async {
    await _storage.delete(key: _accessKey);
    await _storage.delete(key: _refreshKey);
  }

  Future<void> saveApiBaseUrl(String url) => _storage.write(key: _apiBaseKey, value: url);

  Future<String> readApiBaseUrl() async =>
      await _storage.read(key: _apiBaseKey) ?? 'http://10.0.2.2:8000';
}
