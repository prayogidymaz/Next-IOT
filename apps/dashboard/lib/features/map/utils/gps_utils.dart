import '../../devices/models/device_models.dart';
import '../../telemetry/models/telemetry_models.dart';
import '../models/device_map_models.dart';

/// Default tactical map center (Jakarta) when telemetry exists but GPS keys are absent.
const double kDefaultMapLatitude = -6.2088;
const double kDefaultMapLongitude = 106.8456;
const double kDefaultMapAltitudeM = 28.0;

const _latitudeKeys = ['latitude', 'lat', 'gps_lat'];
const _longitudeKeys = ['longitude', 'lon', 'lng', 'gps_lon'];

double? _readMetric(Map<String, double> metrics, List<String> keys) {
  for (final key in keys) {
    final value = metrics[key];
    if (value != null && !value.isNaN) return value;
  }
  return null;
}

bool isValidGpsCoordinate(double? lat, double? lon) {
  if (lat == null || lon == null) return false;
  if (lat.isNaN || lon.isNaN) return false;
  if (lat.abs() > 90 || lon.abs() > 180) return false;
  return true;
}

/// Extract GPS fix from telemetry metrics (`latitude`/`longitude` or `lat`/`lon`).
DeviceGpsFix? parseGpsFix(Map<String, double> metrics) {
  final lat = _readMetric(metrics, _latitudeKeys);
  final lon = _readMetric(metrics, _longitudeKeys);
  if (!isValidGpsCoordinate(lat, lon)) return null;

  return DeviceGpsFix(
    latitude: lat!,
    longitude: lon!,
    altitudeM: metrics['altitude_m'] ?? metrics['altitude'] ?? metrics['alt'],
    speed: _parseSpeed(metrics),
  );
}

/// Parsed GPS or Jakarta fallback when telemetry payload exists but lacks coordinates.
DeviceGpsFix? resolveGpsFix(
  Map<String, double> metrics, {
  bool allowDefaultFallback = false,
}) {
  final parsed = parseGpsFix(metrics);
  if (parsed != null) return parsed;

  if (allowDefaultFallback && metrics.isNotEmpty) {
    return const DeviceGpsFix(
      latitude: kDefaultMapLatitude,
      longitude: kDefaultMapLongitude,
      altitudeM: kDefaultMapAltitudeM,
    );
  }
  return null;
}

double? _parseSpeed(Map<String, double> metrics) {
  for (final key in ['speed', 'speed_mps', 'ground_speed', 'velocity']) {
    final value = metrics[key];
    if (value != null && !value.isNaN) return value;
  }
  return null;
}

bool telemetryHasGpsKeys(Map<String, double> metrics) => parseGpsFix(metrics) != null;

DeviceMapMarker? buildMapMarker({
  required Device device,
  required TelemetryLatest? telemetry,
  bool hasActiveAlert = false,
  bool allowDefaultCoordinates = false,
}) {
  if (telemetry == null || telemetry.metrics.isEmpty) return null;

  final fix = resolveGpsFix(
    telemetry.metrics,
    allowDefaultFallback: allowDefaultCoordinates,
  );
  if (fix == null) return null;

  final metrics = telemetry.metrics;
  return DeviceMapMarker(
    device: device,
    fix: fix,
    battery: metrics['battery'],
    roll: metrics['roll'],
    pitch: metrics['pitch'],
    yaw: metrics['yaw'],
    speed: fix.speed ?? _parseSpeed(metrics),
    hasActiveAlert: hasActiveAlert,
    recordedAt: telemetry.recordedAt,
  );
}
