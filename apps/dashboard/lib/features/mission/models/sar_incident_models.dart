enum SarIncidentType {
  personLost('PERSON_LOST', 'Person Lost'),
  vehicleCrash('VEHICLE_CRASH', 'Vehicle Crash'),
  droneDown('DRONE_DOWN', 'Drone Down');

  const SarIncidentType(this.apiValue, this.label);
  final String apiValue;
  final String label;

  static SarIncidentType fromApi(String value) {
    return SarIncidentType.values.firstWhere(
      (t) => t.apiValue == value,
      orElse: () => SarIncidentType.personLost,
    );
  }
}

enum SarIncidentStatus {
  active('ACTIVE'),
  resolved('RESOLVED');

  const SarIncidentStatus(this.apiValue);
  final String apiValue;
}

class SarIncident {
  const SarIncident({
    required this.id,
    required this.tenantId,
    required this.incidentType,
    required this.status,
    required this.targetLat,
    required this.targetLon,
    required this.severity,
    this.assignedDeviceId,
    this.message,
    this.sarGrid = const {},
    this.metadata = const {},
    this.createdAt,
    this.resolvedAt,
  });

  final String id;
  final String tenantId;
  final SarIncidentType incidentType;
  final SarIncidentStatus status;
  final double targetLat;
  final double targetLon;
  final String severity;
  final String? assignedDeviceId;
  final String? message;
  final Map<String, dynamic> sarGrid;
  final Map<String, dynamic> metadata;
  final DateTime? createdAt;
  final DateTime? resolvedAt;

  bool get isActive => status == SarIncidentStatus.active;

  factory SarIncident.fromJson(Map<String, dynamic> json) {
    return SarIncident(
      id: json['id'] as String,
      tenantId: json['tenant_id'] as String,
      incidentType: SarIncidentType.fromApi(json['incident_type'] as String),
      status: (json['status'] as String) == 'RESOLVED'
          ? SarIncidentStatus.resolved
          : SarIncidentStatus.active,
      targetLat: (json['target_lat'] as num).toDouble(),
      targetLon: (json['target_lon'] as num).toDouble(),
      severity: json['severity'] as String? ?? 'critical',
      assignedDeviceId: json['assigned_device_id'] as String?,
      message: json['message'] as String?,
      sarGrid: json['sar_grid'] as Map<String, dynamic>? ?? const {},
      metadata: json['metadata'] as Map<String, dynamic>? ?? const {},
      createdAt: json['created_at'] != null ? DateTime.parse(json['created_at'] as String) : null,
      resolvedAt: json['resolved_at'] != null ? DateTime.parse(json['resolved_at'] as String) : null,
    );
  }
}

class SarIncidentListData {
  const SarIncidentListData({required this.count, required this.incidents});

  final int count;
  final List<SarIncident> incidents;

  factory SarIncidentListData.fromJson(Map<String, dynamic> json) {
    final items = (json['items'] as List<dynamic>? ?? [])
        .map((e) => SarIncident.fromJson(e as Map<String, dynamic>))
        .toList();
    return SarIncidentListData(count: json['count'] as int? ?? items.length, incidents: items);
  }
}
