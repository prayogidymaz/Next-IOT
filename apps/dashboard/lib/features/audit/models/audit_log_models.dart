class AuditLogEntry {
  AuditLogEntry({
    required this.id,
    required this.timestamp,
    required this.actorEmail,
    this.actorId,
    this.tenantId,
    required this.action,
    required this.resourceTarget,
    this.ipAddress,
    required this.status,
  });

  final String id;
  final DateTime timestamp;
  final String? actorId;
  final String actorEmail;
  final String? tenantId;
  final String action;
  final String resourceTarget;
  final String? ipAddress;
  final String status;

  factory AuditLogEntry.fromJson(Map<String, dynamic> json) {
    return AuditLogEntry(
      id: json['id'] as String,
      timestamp: DateTime.parse(json['timestamp'] as String),
      actorId: json['actor_id'] as String?,
      actorEmail: json['actor_email'] as String,
      tenantId: json['tenant_id'] as String?,
      action: json['action'] as String,
      resourceTarget: json['resource_target'] as String? ?? '',
      ipAddress: json['ip_address'] as String?,
      status: json['status'] as String,
    );
  }
}

class AuditLogPage {
  AuditLogPage({
    required this.items,
    required this.total,
    required this.page,
    required this.pageSize,
  });

  final List<AuditLogEntry> items;
  final int total;
  final int page;
  final int pageSize;

  factory AuditLogPage.fromJson(Map<String, dynamic> json) {
    final raw = json['items'] as List<dynamic>? ?? [];
    return AuditLogPage(
      items: raw
          .map((e) => AuditLogEntry.fromJson(e as Map<String, dynamic>))
          .toList(),
      total: json['total'] as int? ?? 0,
      page: json['page'] as int? ?? 1,
      pageSize: json['page_size'] as int? ?? 50,
    );
  }
}
