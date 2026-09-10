class TelemetryAnomaly {
  const TelemetryAnomaly({
    required this.id,
    required this.deviceId,
    required this.severity,
    required this.anomalyType,
    required this.message,
    required this.metadata,
    required this.recordedAt,
    required this.detectedAt,
  });

  final String id;
  final String deviceId;
  final String severity;
  final String anomalyType;
  final String message;
  final Map<String, dynamic> metadata;
  final DateTime recordedAt;
  final DateTime detectedAt;

  factory TelemetryAnomaly.fromJson(Map<String, dynamic> json) {
    return TelemetryAnomaly(
      id: json['id'] as String,
      deviceId: json['device_id'] as String,
      severity: json['severity'] as String,
      anomalyType: json['anomaly_type'] as String,
      message: json['message'] as String,
      metadata: Map<String, dynamic>.from(json['metadata'] as Map? ?? {}),
      recordedAt: DateTime.parse(json['recorded_at'] as String),
      detectedAt: DateTime.parse(json['detected_at'] as String),
    );
  }
}

class TelemetryAnomalyList {
  const TelemetryAnomalyList({
    required this.deviceId,
    required this.hours,
    required this.count,
    required this.items,
  });

  final String deviceId;
  final int hours;
  final int count;
  final List<TelemetryAnomaly> items;

  factory TelemetryAnomalyList.fromJson(Map<String, dynamic> json) {
    final rawItems = json['items'] as List<dynamic>? ?? [];
    return TelemetryAnomalyList(
      deviceId: json['device_id'] as String,
      hours: json['hours'] as int,
      count: json['count'] as int,
      items: rawItems
          .map((e) => TelemetryAnomaly.fromJson(e as Map<String, dynamic>))
          .toList(),
    );
  }

  bool get hasCritical => items.any((a) => a.severity == 'critical');
  bool get hasWarning => items.any((a) => a.severity == 'warning');
}
