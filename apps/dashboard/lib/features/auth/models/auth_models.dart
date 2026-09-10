class LoginRequest {
  const LoginRequest({required this.email, required this.password});

  final String email;
  final String password;

  Map<String, dynamic> toJson() => {'email': email, 'password': password};
}

class TokenPair {
  const TokenPair({required this.accessToken, required this.refreshToken});

  final String accessToken;
  final String refreshToken;

  factory TokenPair.fromJson(Map<String, dynamic> json) => TokenPair(
        accessToken: json['access_token'] as String,
        refreshToken: json['refresh_token'] as String,
      );
}

class AuthUser {
  const AuthUser({
    required this.userId,
    required this.email,
    required this.role,
    required this.tenantId,
  });

  final String userId;
  final String email;
  final String role;
  final String tenantId;

  factory AuthUser.fromMeJson(Map<String, dynamic> json) => AuthUser(
        userId: json['user_id'] as String,
        email: json['email'] as String,
        role: json['role'] as String,
        tenantId: json['tenant_id'] as String,
      );
}
