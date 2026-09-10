enum TelemetryTimeRange {
  oneHour('1H', Duration(hours: 1), 60),
  twentyFourHours('24H', Duration(hours: 24), 200),
  sevenDays('7D', Duration(days: 7), 1000);

  const TelemetryTimeRange(this.label, this.duration, this.limit);

  final String label;
  final Duration duration;
  final int limit;
}

class TelemetryLatest {
  const TelemetryLatest({
    required this.deviceId,
    this.readingId,
    this.recordedAt,
    required this.metrics,
    this.cachedAt,
    this.source = 'redis',
  });

  final String deviceId;
  final String? readingId;
  final DateTime? recordedAt;
  final Map<String, double> metrics;
  final DateTime? cachedAt;
  final String source;

  factory TelemetryLatest.fromJson(Map<String, dynamic> json) {
    final rawMetrics = json['metrics'] as Map<String, dynamic>? ?? {};
    return TelemetryLatest(
      deviceId: json['device_id'] as String,
      readingId: json['reading_id'] as String?,
      recordedAt: json['recorded_at'] != null
          ? DateTime.parse(json['recorded_at'] as String)
          : null,
      metrics: _parseMetrics(rawMetrics),
      cachedAt: json['cached_at'] != null
          ? DateTime.parse(json['cached_at'] as String)
          : null,
      source: json['source'] as String? ?? 'redis',
    );
  }
}

class TelemetryHistoryItem {
  const TelemetryHistoryItem({
    required this.readingId,
    required this.recordedAt,
    required this.metrics,
    required this.ingestedAt,
  });

  final String readingId;
  final DateTime recordedAt;
  final Map<String, double> metrics;
  final DateTime ingestedAt;

  factory TelemetryHistoryItem.fromJson(Map<String, dynamic> json) =>
      TelemetryHistoryItem(
        readingId: json['reading_id'] as String,
        recordedAt: DateTime.parse(json['recorded_at'] as String),
        metrics: _parseMetrics(json['metrics'] as Map<String, dynamic>),
        ingestedAt: DateTime.parse(json['ingested_at'] as String),
      );
}

class TelemetryHistory {
  const TelemetryHistory({
    required this.deviceId,
    required this.count,
    required this.items,
  });

  final String deviceId;
  final int count;
  final List<TelemetryHistoryItem> items;

  factory TelemetryHistory.fromJson(Map<String, dynamic> json) {
    final items = (json['items'] as List<dynamic>)
        .map((e) => TelemetryHistoryItem.fromJson(e as Map<String, dynamic>))
        .toList();
    return TelemetryHistory(
      deviceId: json['device_id'] as String,
      count: json['count'] as int,
      items: items,
    );
  }
}

Map<String, double> _parseMetrics(Map<String, dynamic> raw) {
  final result = <String, double>{};
  raw.forEach((key, value) {
    if (value is num) {
      result[key] = value.toDouble();
    }
  });
  return result;
}

enum MetricKind { temperature, humidity, battery, orientation, gps, custom }

class MetricDefinition {
  const MetricDefinition({
    required this.key,
    required this.label,
    required this.unit,
    required this.kind,
    this.min = 0,
    this.max = 100,
  });

  final String key;
  final String label;
  final String unit;
  final MetricKind kind;
  final double min;
  final double max;

  static const knownMetrics = [
    MetricDefinition(
      key: 'temperature',
      label: 'Temperature',
      unit: '°C',
      kind: MetricKind.temperature,
      min: -10,
      max: 50,
    ),
    MetricDefinition(
      key: 'humidity',
      label: 'Humidity',
      unit: '%',
      kind: MetricKind.humidity,
      min: 0,
      max: 100,
    ),
    MetricDefinition(
      key: 'battery',
      label: 'Battery',
      unit: '%',
      kind: MetricKind.battery,
      min: 0,
      max: 100,
    ),
    MetricDefinition(
      key: 'roll',
      label: 'Roll',
      unit: '°',
      kind: MetricKind.orientation,
      min: -180,
      max: 180,
    ),
    MetricDefinition(
      key: 'pitch',
      label: 'Pitch',
      unit: '°',
      kind: MetricKind.orientation,
      min: -90,
      max: 90,
    ),
    MetricDefinition(
      key: 'yaw',
      label: 'Yaw',
      unit: '°',
      kind: MetricKind.orientation,
      min: 0,
      max: 360,
    ),
  ];

  static MetricDefinition? lookup(String key) {
    for (final def in knownMetrics) {
      if (def.key == key) return def;
    }
    return null;
  }

  static MetricDefinition custom(String key) => MetricDefinition(
        key: key,
        label: _titleCase(key),
        unit: '',
        kind: MetricKind.custom,
      );

  static String _titleCase(String key) {
    return key
        .split('_')
        .map((part) => part.isEmpty ? part : '${part[0].toUpperCase()}${part.substring(1)}')
        .join(' ');
  }
}

List<MetricDefinition> resolveGaugeMetrics(Map<String, double> metrics) {
  final defs = <MetricDefinition>[];
  for (final known in MetricDefinition.knownMetrics) {
    if (metrics.containsKey(known.key)) defs.add(known);
  }
  for (final key in metrics.keys) {
    if (MetricDefinition.lookup(key) == null &&
        key != 'latitude' &&
        key != 'longitude' &&
        key != 'altitude_m') {
      defs.add(MetricDefinition.custom(key));
    }
  }
  return defs;
}

List<TelemetryHistoryItem> sortHistoryChronologically(List<TelemetryHistoryItem> items) {
  final sorted = List<TelemetryHistoryItem>.from(items);
  sorted.sort((a, b) => a.recordedAt.compareTo(b.recordedAt));
  return sorted;
}

List<double> seriesForMetric(List<TelemetryHistoryItem> items, String metricKey) {
  return items
      .where((item) => item.metrics.containsKey(metricKey))
      .map((item) => item.metrics[metricKey]!)
      .toList();
}
