import 'package:dio/dio.dart';

import '../../../core/auth/token_storage.dart';
import '../../../core/network/api_client.dart';
import '../models/auth_models.dart';

class AuthRepository {
  AuthRepository({ApiClient? apiClient, TokenStorage? tokenStorage})
      : _api = (apiClient ?? ApiClient()).dio,
        _tokenStorage = tokenStorage ?? TokenStorage();

  final Dio _api;
  final TokenStorage _tokenStorage;

  Future<AuthUser> login(LoginRequest request) async {
    final response = await _api.post('/auth/login', data: request.toJson());
    final tokens = TokenPair.fromJson(response.data as Map<String, dynamic>);
    await _tokenStorage.saveTokens(
      accessToken: tokens.accessToken,
      refreshToken: tokens.refreshToken,
    );
    return fetchCurrentUser();
  }

  Future<AuthUser> fetchCurrentUser() async {
    final response = await _api.get('/api/v1/me');
    return AuthUser.fromMeJson(response.data as Map<String, dynamic>);
  }

  Future<void> logout() async {
    final refresh = await _tokenStorage.getRefreshToken();
    if (refresh != null) {
      try {
        await _api.post('/auth/logout', data: {'refresh_token': refresh});
      } catch (_) {
        // Best-effort server logout
      }
    }
    await _tokenStorage.clear();
  }

  Future<bool> hasSession() => _tokenStorage.hasSession();
}
