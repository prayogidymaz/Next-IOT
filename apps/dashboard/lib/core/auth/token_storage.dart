import 'package:flutter_secure_storage/flutter_secure_storage.dart';

class TokenStorage {
  static const _accessKey = 'access_token';
  static const _refreshKey = 'refresh_token';
  static const _tenantKey = 'active_tenant_id';

  TokenStorage({FlutterSecureStorage? secureStorage})
      : _secure = secureStorage ??
            const FlutterSecureStorage(
              aOptions: AndroidOptions(encryptedSharedPreferences: true),
            );

  final FlutterSecureStorage _secure;

  Future<void> saveTokens({
    required String accessToken,
    required String refreshToken,
    String? tenantId,
  }) async {
    await _secure.write(key: _accessKey, value: accessToken);
    await _secure.write(key: _refreshKey, value: refreshToken);
    if (tenantId != null && tenantId.isNotEmpty) {
      await _secure.write(key: _tenantKey, value: tenantId);
    }
  }

  Future<String?> getActiveTenantId() => _secure.read(key: _tenantKey);

  Future<void> saveActiveTenantId(String tenantId) async {
    await _secure.write(key: _tenantKey, value: tenantId);
  }

  Future<String?> getAccessToken() => _secure.read(key: _accessKey);

  Future<String?> getRefreshToken() => _secure.read(key: _refreshKey);

  Future<void> clear() async {
    await _secure.delete(key: _accessKey);
    await _secure.delete(key: _refreshKey);
    await _secure.delete(key: _tenantKey);
  }

  Future<bool> hasSession() async {
    final token = await getAccessToken();
    return token != null && token.isNotEmpty;
  }
}
