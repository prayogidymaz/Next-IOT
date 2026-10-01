class TenantSummary {
  const TenantSummary({
    required this.id,
    required this.name,
    required this.slug,
    required this.securityTier,
    required this.isActive,
    this.membershipRole,
  });

  final String id;
  final String name;
  final String slug;
  final String securityTier;
  final bool isActive;
  final String? membershipRole;

  factory TenantSummary.fromJson(Map<String, dynamic> json) => TenantSummary(
        id: json['id'].toString(),
        name: json['name'] as String,
        slug: json['slug'] as String,
        securityTier: json['security_tier'] as String,
        isActive: json['is_active'] as bool,
        membershipRole: json['membership_role'] as String?,
      );
}

class TenantMember {
  const TenantMember({
    required this.userId,
    required this.email,
    required this.role,
    required this.isActive,
    required this.createdAt,
  });

  final String userId;
  final String email;
  final String role;
  final bool isActive;
  final DateTime createdAt;

  factory TenantMember.fromJson(Map<String, dynamic> json) => TenantMember(
        userId: json['user_id'] as String,
        email: json['email'] as String,
        role: json['role'] as String,
        isActive: json['is_active'] as bool,
        createdAt: DateTime.parse(json['created_at'] as String),
      );
}
