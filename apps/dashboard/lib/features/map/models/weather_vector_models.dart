enum FlightSafetyStatus {
  safe('SAFE'),
  caution('CAUTION'),
  noFly('NO_FLY');

  const FlightSafetyStatus(this.apiValue);
  final String apiValue;

  static FlightSafetyStatus fromApi(String value) {
    return FlightSafetyStatus.values.firstWhere(
      (s) => s.apiValue == value,
      orElse: () => FlightSafetyStatus.safe,
    );
  }
}

class WindVectorPoint {
  const WindVectorPoint({
    required this.lat,
    required this.lon,
    required this.windSpeedMs,
    required this.windDirectionDeg,
  });

  final double lat;
  final double lon;
  final double windSpeedMs;
  final double windDirectionDeg;

  factory WindVectorPoint.fromJson(Map<String, dynamic> json) => WindVectorPoint(
        lat: (json['lat'] as num).toDouble(),
        lon: (json['lon'] as num).toDouble(),
        windSpeedMs: (json['wind_speed_m_s'] as num).toDouble(),
        windDirectionDeg: (json['wind_direction_deg'] as num).toDouble(),
      );
}

class WeatherVectorData {
  const WeatherVectorData({
    required this.lat,
    required this.lon,
    required this.radiusM,
    required this.windSpeedMs,
    required this.windDirectionDeg,
    required this.visibilityM,
    required this.rainRateMmH,
    required this.flightSafetyStatus,
    required this.vectors,
  });

  final double lat;
  final double lon;
  final double radiusM;
  final double windSpeedMs;
  final double windDirectionDeg;
  final double visibilityM;
  final double rainRateMmH;
  final FlightSafetyStatus flightSafetyStatus;
  final List<WindVectorPoint> vectors;

  factory WeatherVectorData.fromJson(Map<String, dynamic> json) {
    final rawVectors = json['vectors'] as List<dynamic>? ?? [];
    return WeatherVectorData(
      lat: (json['lat'] as num).toDouble(),
      lon: (json['lon'] as num).toDouble(),
      radiusM: (json['radius_m'] as num).toDouble(),
      windSpeedMs: (json['wind_speed_m_s'] as num).toDouble(),
      windDirectionDeg: (json['wind_direction_deg'] as num).toDouble(),
      visibilityM: (json['visibility_m'] as num).toDouble(),
      rainRateMmH: (json['rain_rate_mm_h'] as num).toDouble(),
      flightSafetyStatus: FlightSafetyStatus.fromApi(json['flight_safety_status'] as String),
      vectors: rawVectors
          .map((e) => WindVectorPoint.fromJson(e as Map<String, dynamic>))
          .toList(),
    );
  }
}
