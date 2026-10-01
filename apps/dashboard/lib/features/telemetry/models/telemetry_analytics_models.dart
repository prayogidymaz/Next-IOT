class MetricStatsSummary {
  const MetricStatsSummary({
    this.avg,
    this.min,
    this.max,
    this.latest,
  });

  final double? avg;
  final double? min;
  final double? max;
  final double? latest;

  factory MetricStatsSummary.fromJson(Map<String, dynamic> json) {
    return MetricStatsSummary(
      avg: (json['avg'] as num?)?.toDouble(),
      min: (json['min'] as num?)?.toDouble(),
      max: (json['max'] as num?)?.toDouble(),
      latest: (json['latest'] as num?)?.toDouble(),
    );
  }
}

class TimeSeriesBucketPoint {
  const TimeSeriesBucketPoint({
    required this.bucketStart,
    this.avg,
    this.min,
    this.max,
    this.count = 0,
  });

  final DateTime bucketStart;
  final double? avg;
  final double? min;
  final double? max;
  final int count;

  factory TimeSeriesBucketPoint.fromJson(Map<String, dynamic> json) {
    return TimeSeriesBucketPoint(
      bucketStart: DateTime.parse(json['bucket_start'] as String),
      avg: (json['avg'] as num?)?.toDouble(),
      min: (json['min'] as num?)?.toDouble(),
      max: (json['max'] as num?)?.toDouble(),
      count: json['count'] as int? ?? 0,
    );
  }
}

class MetricTimeSeries {
  const MetricTimeSeries({
    required this.metric,
    required this.stats,
    this.points = const [],
  });

  final String metric;
  final MetricStatsSummary stats;
  final List<TimeSeriesBucketPoint> points;

  factory MetricTimeSeries.fromJson(Map<String, dynamic> json) {
    final points = (json['points'] as List<dynamic>? ?? [])
        .map((e) => TimeSeriesBucketPoint.fromJson(e as Map<String, dynamic>))
        .toList();
    return MetricTimeSeries(
      metric: json['metric'] as String,
      stats: MetricStatsSummary.fromJson(json['stats'] as Map<String, dynamic>),
      points: points,
    );
  }
}

class TelemetryAnalytics {
  const TelemetryAnalytics({
    required this.deviceId,
    required this.readingCount,
    required this.totalDistanceM,
    required this.anomalyCount,
    this.hours,
    this.startTime,
    this.endTime,
    this.interval,
    this.maxSpeedMs,
    this.avgAltitudeM,
    this.minVoltageV,
    this.series = const [],
  });

  final String deviceId;
  final int? hours;
  final DateTime? startTime;
  final DateTime? endTime;
  final String? interval;
  final int readingCount;
  final double? maxSpeedMs;
  final double? avgAltitudeM;
  final double? minVoltageV;
  final double totalDistanceM;
  final int anomalyCount;
  final List<MetricTimeSeries> series;

  MetricTimeSeries? seriesFor(String metric) {
    for (final s in series) {
      if (s.metric == metric) return s;
    }
    return null;
  }

  factory TelemetryAnalytics.fromJson(Map<String, dynamic> json) {
    final series = (json['series'] as List<dynamic>? ?? [])
        .map((e) => MetricTimeSeries.fromJson(e as Map<String, dynamic>))
        .toList();
    return TelemetryAnalytics(
      deviceId: json['device_id'].toString(),
      hours: json['hours'] as int?,
      startTime: json['start_time'] != null
          ? DateTime.parse(json['start_time'] as String)
          : null,
      endTime: json['end_time'] != null
          ? DateTime.parse(json['end_time'] as String)
          : null,
      interval: json['interval'] as String?,
      readingCount: json['reading_count'] as int? ?? 0,
      maxSpeedMs: (json['max_speed_m_s'] as num?)?.toDouble(),
      avgAltitudeM: (json['avg_altitude_m'] as num?)?.toDouble(),
      minVoltageV: (json['min_voltage_v'] as num?)?.toDouble(),
      totalDistanceM: (json['total_distance_m'] as num?)?.toDouble() ?? 0,
      anomalyCount: json['anomaly_count'] as int? ?? 0,
      series: series,
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
