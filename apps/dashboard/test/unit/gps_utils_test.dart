import 'package:flutter_test/flutter_test.dart';
import 'package:next_iot_dashboard/features/devices/models/device_models.dart';
import 'package:next_iot_dashboard/features/map/models/device_map_models.dart';
import 'package:next_iot_dashboard/features/map/utils/gps_utils.dart';
import 'package:next_iot_dashboard/features/telemetry/models/telemetry_models.dart';

void main() {
  test('parseGpsFix extracts latitude/longitude and alt/speed', () {
    final fix = parseGpsFix({
      'latitude': -6.2088,
      'longitude': 106.8456,
      'altitude_m': 28.0,
      'speed_mps': 12.5,
    });

    expect(fix, isNotNull);
    expect(fix!.latitude, -6.2088);
    expect(fix.longitude, 106.8456);
    expect(fix.altitudeM, 28.0);
    expect(fix.speed, 12.5);
  });

  test('parseGpsFix accepts lat/lon aliases', () {
    final fix = parseGpsFix({
      'lat': -6.2,
      'lon': 106.8,
    });

    expect(fix, isNotNull);
    expect(fix!.latitude, -6.2);
    expect(fix.longitude, 106.8);
  });

  test('parseGpsFix returns null without coordinates', () {
    expect(parseGpsFix({'battery': 90}), isNull);
  });

  test('resolveGpsFix uses Jakarta fallback when telemetry has no GPS keys', () {
    final fix = resolveGpsFix(
      const {'temperature': 24.5, 'battery': 80},
      allowDefaultFallback: true,
    );

    expect(fix, isNotNull);
    expect(fix!.latitude, kDefaultMapLatitude);
    expect(fix.longitude, kDefaultMapLongitude);
  });

  test('resolveGpsFix does not fallback on empty metrics', () {
    expect(resolveGpsFix(const {}, allowDefaultFallback: true), isNull);
  });

  test('buildMapMarker includes offline devices with GPS telemetry', () {
    final device = Device(
      id: 'd1',
      tenantId: 't1',
      name: 'Offline Drone',
      deviceType: 'drone',
      status: 'offline',
      createdAt: DateTime(2026, 9, 10),
    );
    final telemetry = TelemetryLatest(
      deviceId: 'd1',
      metrics: const {
        'lat': -6.2088,
        'lon': 106.8456,
        'battery': 80,
      },
    );

    final marker = buildMapMarker(
      device: device,
      telemetry: telemetry,
      allowDefaultCoordinates: true,
    );

    expect(marker, isNotNull);
    expect(marker!.status, MapMarkerStatus.offline);
    expect(marker.fix.latitude, -6.2088);
    expect(marker.fix.longitude, 106.8456);
  });

  test('buildMapMarker sets alert status', () {
    final device = Device(
      id: 'd1',
      tenantId: 't1',
      name: 'Field Drone',
      deviceType: 'drone',
      status: 'online',
      createdAt: DateTime(2026, 9, 10),
    );
    final telemetry = TelemetryLatest(
      deviceId: 'd1',
      metrics: const {
        'latitude': 1.0,
        'longitude': 2.0,
        'battery': 80,
        'roll': 1,
        'pitch': 2,
        'yaw': 3,
      },
    );

    final marker = buildMapMarker(
      device: device,
      telemetry: telemetry,
      hasActiveAlert: true,
    );

    expect(marker, isNotNull);
    expect(marker!.status, MapMarkerStatus.alert);
    expect(marker.battery, 80);
  });
}
