class UserPermissions {
  const UserPermissions({
    required this.userId,
    required this.tenantId,
    required this.role,
    required this.permissions,
  });

  final String userId;
  final String tenantId;
  final String role;
  final Set<String> permissions;

  bool can(String permission) => permissions.contains(permission);

  factory UserPermissions.fromJson(Map<String, dynamic> json) {
    final raw = json['permissions'];
    final list = raw is List ? raw.map((e) => e.toString()).toList() : <String>[];
    return UserPermissions(
      userId: json['user_id'].toString(),
      tenantId: json['tenant_id'].toString(),
      role: json['role'] as String,
      permissions: list.toSet(),
    );
  }
}
