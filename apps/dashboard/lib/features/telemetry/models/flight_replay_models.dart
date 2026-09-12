class FlightReplayAnomalyBrief {
  const FlightReplayAnomalyBrief({
    required this.id,
    required this.severity,
    required this.anomalyType,
    required this.message,
  });

  final String id;
  final String severity;
  final String anomalyType;
  final String message;

  factory FlightReplayAnomalyBrief.fromJson(Map<String, dynamic> json) => FlightReplayAnomalyBrief(
        id: json['id'] as String,
        severity: json['severity'] as String,
        anomalyType: json['anomaly_type'] as String,
        message: json['message'] as String,
      );
}

class FlightReplaySample {
  const FlightReplaySample({
    required this.timestamp,
    required this.lat,
    required this.lon,
    this.alt,
    this.speed,
    this.heading,
    this.rssi,
    this.anomalies = const [],
  });

  final DateTime timestamp;
  final double lat;
  final double lon;
  final double? alt;
  final double? speed;
  final double? heading;
  final double? rssi;
  final List<FlightReplayAnomalyBrief> anomalies;

  factory FlightReplaySample.fromJson(Map<String, dynamic> json) {
    final rawAnomalies = json['anomalies'] as List<dynamic>? ?? [];
    return FlightReplaySample(
      timestamp: DateTime.parse(json['timestamp'] as String),
      lat: (json['lat'] as num).toDouble(),
      lon: (json['lon'] as num).toDouble(),
      alt: (json['alt'] as num?)?.toDouble(),
      speed: (json['speed'] as num?)?.toDouble(),
      heading: (json['heading'] as num?)?.toDouble(),
      rssi: (json['rssi'] as num?)?.toDouble(),
      anomalies: rawAnomalies
          .map((e) => FlightReplayAnomalyBrief.fromJson(e as Map<String, dynamic>))
          .toList(),
    );
  }
}

class FlightReplayData {
  const FlightReplayData({
    required this.deviceId,
    required this.sessionStart,
    required this.sessionEnd,
    required this.samples,
    this.hours,
  });

  final String deviceId;
  final DateTime sessionStart;
  final DateTime sessionEnd;
  final int? hours;
  final List<FlightReplaySample> samples;

  factory FlightReplayData.fromJson(Map<String, dynamic> json) {
    final rawSamples = json['samples'] as List<dynamic>? ?? [];
    return FlightReplayData(
      deviceId: json['device_id'] as String,
      sessionStart: DateTime.parse(json['session_start'] as String),
      sessionEnd: DateTime.parse(json['session_end'] as String),
      hours: json['hours'] as int?,
      samples: rawSamples
          .map((e) => FlightReplaySample.fromJson(e as Map<String, dynamic>))
          .toList(),
    );
  }

  Duration get duration => sessionEnd.difference(sessionStart);
}
