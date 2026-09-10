class SignalHeatmapPoint {
  const SignalHeatmapPoint({
    required this.lat,
    required this.lon,
    required this.rssi,
    this.snr,
    required this.signalScore,
    required this.signalStrength,
    required this.recordedAt,
  });

  final double lat;
  final double lon;
  final double rssi;
  final double? snr;
  final int signalScore;
  final String signalStrength;
  final DateTime recordedAt;

  factory SignalHeatmapPoint.fromJson(Map<String, dynamic> json) => SignalHeatmapPoint(
        lat: (json['lat'] as num).toDouble(),
        lon: (json['lon'] as num).toDouble(),
        rssi: (json['rssi'] as num).toDouble(),
        snr: (json['snr'] as num?)?.toDouble(),
        signalScore: json['signal_score'] as int,
        signalStrength: json['signal_strength'] as String,
        recordedAt: DateTime.parse(json['recorded_at'] as String),
      );
}

class SignalHeatmapData {
  const SignalHeatmapData({
    required this.deviceId,
    required this.hours,
    required this.points,
  });

  final String deviceId;
  final int hours;
  final List<SignalHeatmapPoint> points;

  factory SignalHeatmapData.fromJson(Map<String, dynamic> json) => SignalHeatmapData(
        deviceId: json['device_id'] as String,
        hours: json['hours'] as int,
        points: (json['points'] as List<dynamic>)
            .map((e) => SignalHeatmapPoint.fromJson(e as Map<String, dynamic>))
            .toList(),
      );
}
