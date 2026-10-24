import "package:flutter_secure_storage/flutter_secure_storage.dart";

class AuthStorage {
  AuthStorage({FlutterSecureStorage? storage})
      : _storage = storage ?? const FlutterSecureStorage();

  static const _jwtKey = "wear_jwt";

  final FlutterSecureStorage _storage;

  Future<void> saveJwt(String token) => _storage.write(key: _jwtKey, value: token);

  Future<String?> readJwt() => _storage.read(key: _jwtKey);

  Future<void> clear() => _storage.delete(key: _jwtKey);
}
