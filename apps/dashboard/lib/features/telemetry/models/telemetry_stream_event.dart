/// Real-time telemetry payload from WebSocket / MQTT stream.
class TelemetryStreamEvent {
  const TelemetryStreamEvent({
    required this.deviceId,
    required this.metrics,
    this.status,
    this.recordedAt,
    this.source = 'stream',
  });

  final String deviceId;
  final Map<String, double> metrics;
  final String? status;
  final DateTime? recordedAt;
  final String source;

  factory TelemetryStreamEvent.fromJson(Map<String, dynamic> json) {
    final rawMetrics = json['metrics'] as Map<String, dynamic>? ?? json;
    final metrics = rawMetrics.containsKey('device_id')
        ? <String, double>{}
        : _parseMetrics(rawMetrics);

    if (metrics.isEmpty && json.containsKey('latitude')) {
      metrics.addAll(_parseMetrics(json));
    }

    return TelemetryStreamEvent(
      deviceId: (json['device_id'] ?? json['deviceId']) as String,
      metrics: metrics,
      status: json['status'] as String?,
      recordedAt: json['recorded_at'] != null
          ? DateTime.tryParse(json['recorded_at'] as String)
          : (json['recordedAt'] != null
              ? DateTime.tryParse(json['recordedAt'] as String)
              : null),
      source: json['source'] as String? ?? 'stream',
    );
  }
}

Map<String, double> _parseMetrics(Map<String, dynamic> raw) {
  final out = <String, double>{};
  raw.forEach((key, value) {
    if (value is num) out[key] = value.toDouble();
  });
  return out;
}
