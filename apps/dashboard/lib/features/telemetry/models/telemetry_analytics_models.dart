class TelemetryAnalytics {
  const TelemetryAnalytics({
    required this.deviceId,
    required this.hours,
    required this.readingCount,
    required this.totalDistanceM,
    required this.anomalyCount,
    this.maxSpeedMs,
    this.avgAltitudeM,
    this.minVoltageV,
  });

  final String deviceId;
  final int hours;
  final int readingCount;
  final double? maxSpeedMs;
  final double? avgAltitudeM;
  final double? minVoltageV;
  final double totalDistanceM;
  final int anomalyCount;

  factory TelemetryAnalytics.fromJson(Map<String, dynamic> json) {
    return TelemetryAnalytics(
      deviceId: json['device_id'] as String,
      hours: json['hours'] as int,
      readingCount: json['reading_count'] as int,
      maxSpeedMs: (json['max_speed_m_s'] as num?)?.toDouble(),
      avgAltitudeM: (json['avg_altitude_m'] as num?)?.toDouble(),
      minVoltageV: (json['min_voltage_v'] as num?)?.toDouble(),
      totalDistanceM: (json['total_distance_m'] as num?)?.toDouble() ?? 0,
      anomalyCount: json['anomaly_count'] as int? ?? 0,
    );
  }
}

enum TelemetryExportFormat {
  csv('csv', 'CSV', '.csv'),
  json('json', 'JSON', '.json'),
  kml('kml', 'KML (Google Earth)', '.kml');

  const TelemetryExportFormat(this.apiValue, this.label, this.extension);
  final String apiValue;
  final String label;
  final String extension;
}
