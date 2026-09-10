import 'package:flutter_test/flutter_test.dart';
import 'package:next_iot_dashboard/features/auth/models/auth_models.dart';

void main() {
  test('TokenPair.fromJson parses login response', () {
    final pair = TokenPair.fromJson({
      'access_token': 'access123',
      'refresh_token': 'refresh456',
      'token_type': 'bearer',
    });
    expect(pair.accessToken, 'access123');
    expect(pair.refreshToken, 'refresh456');
  });

  test('AuthUser.fromMeJson parses profile', () {
    final user = AuthUser.fromMeJson({
      'user_id': 'u1',
      'email': 'admin@test.com',
      'role': 'tenant_admin',
      'tenant_id': 't1',
    });
    expect(user.email, 'admin@test.com');
    expect(user.role, 'tenant_admin');
  });

  test('LoginRequest.toJson', () {
    const req = LoginRequest(email: 'a@b.com', password: 'secret');
    expect(req.toJson(), {'email': 'a@b.com', 'password': 'secret'});
  });
}
