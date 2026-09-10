import 'package:dio/dio.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../core/config/api_config.dart';
import '../data/auth_repository.dart';
import '../models/auth_models.dart';

final authRepositoryProvider = Provider<AuthRepository>((ref) => AuthRepository());

class AuthState {
  const AuthState({
    this.user,
    this.isLoading = false,
    this.error,
  });

  final AuthUser? user;
  final bool isLoading;
  final String? error;

  bool get isAuthenticated => user != null;

  AuthState copyWith({AuthUser? user, bool? isLoading, String? error, bool clearError = false}) {
    return AuthState(
      user: user ?? this.user,
      isLoading: isLoading ?? this.isLoading,
      error: clearError ? null : (error ?? this.error),
    );
  }
}

class AuthNotifier extends StateNotifier<AuthState> {
  AuthNotifier(this._repository) : super(const AuthState());

  final AuthRepository _repository;

  Future<void> bootstrap() async {
    state = state.copyWith(isLoading: true, clearError: true);
    try {
      if (await _repository.hasSession()) {
        final user = await _repository.fetchCurrentUser();
        state = AuthState(user: user);
      } else {
        state = const AuthState();
      }
    } catch (_) {
      await _repository.logout();
      state = const AuthState();
    }
  }

  Future<bool> login(String email, String password) async {
    state = state.copyWith(isLoading: true, clearError: true);
    try {
      final user = await _repository.login(
        LoginRequest(email: email.trim(), password: password),
      );
      state = AuthState(user: user);
      return true;
    } catch (e) {
      state = AuthState(error: _mapError(e));
      return false;
    }
  }

  Future<void> logout() async {
    await _repository.logout();
    state = const AuthState();
  }

  String _mapError(Object e) {
    if (e is DioException) {
      if (e.response?.statusCode == 401) {
        return 'Invalid email or password';
      }
      if (e.type == DioExceptionType.connectionError ||
          e.type == DioExceptionType.connectionTimeout ||
          e.response == null) {
        return 'Cannot reach API at ${ApiConfig.baseUrl}. Start backend: docker compose up -d api';
      }
    }
    return 'Login failed. Check your connection and credentials.';
  }
}

final authProvider = StateNotifierProvider<AuthNotifier, AuthState>((ref) {
  return AuthNotifier(ref.watch(authRepositoryProvider));
});
