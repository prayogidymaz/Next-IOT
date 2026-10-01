import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../core/api/field_api_client.dart';
import '../../core/storage/token_storage.dart';

final tokenStorageProvider = Provider<TokenStorage>((ref) => TokenStorage());

final fieldApiProvider = Provider<FieldApiClient>(
  (ref) => FieldApiClient(ref.watch(tokenStorageProvider)),
);

class AuthState {
  const AuthState({required this.isAuthenticated, this.loading = false, this.error});

  final bool isAuthenticated;
  final bool loading;
  final String? error;

  AuthState copyWith({bool? isAuthenticated, bool? loading, String? error}) {
    return AuthState(
      isAuthenticated: isAuthenticated ?? this.isAuthenticated,
      loading: loading ?? this.loading,
      error: error,
    );
  }
}

class AuthController extends StateNotifier<AuthState> {
  AuthController(this._api, this._tokens) : super(const AuthState(isAuthenticated: false)) {
    _bootstrap();
  }

  final FieldApiClient _api;
  final TokenStorage _tokens;

  Future<void> _bootstrap() async {
    final token = await _tokens.readAccessToken();
    state = state.copyWith(isAuthenticated: token != null && token.isNotEmpty);
  }

  Future<void> login(String email, String password) async {
    state = state.copyWith(loading: true, error: null);
    try {
      final body = await _api.login(email, password);
      final access = body['access_token']?.toString();
      final refresh = body['refresh_token']?.toString();
      if (access == null || refresh == null) {
        throw StateError('Missing tokens');
      }
      await _tokens.saveTokens(access: access, refresh: refresh);
      state = state.copyWith(isAuthenticated: true, loading: false);
    } catch (e) {
      state = state.copyWith(loading: false, error: e.toString());
    }
  }

  Future<void> logout() async {
    await _tokens.clear();
    state = const AuthState(isAuthenticated: false);
  }
}

final authControllerProvider = StateNotifierProvider<AuthController, AuthState>((ref) {
  return AuthController(ref.watch(fieldApiProvider), ref.watch(tokenStorageProvider));
});
