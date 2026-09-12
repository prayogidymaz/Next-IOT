import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:next_iot_dashboard/features/devices/models/device_models.dart';
import 'package:next_iot_dashboard/features/map/models/device_map_models.dart';
import 'package:next_iot_dashboard/features/map/widgets/telemetry_map_overlay.dart';
import 'package:next_iot_dashboard/features/mavlink/models/mavlink_models.dart';
import 'package:next_iot_dashboard/features/mavlink/widgets/mavlink_attitude_horizon.dart';
import 'package:next_iot_dashboard/features/mavlink/widgets/mavlink_status_badge.dart';

void main() {
  const attitude = MavlinkAttitude(roll: 8, pitch: -4, yaw: 120);

  testWidgets('MavlinkStatusBadge shows connected label', (tester) async {
    await tester.pumpWidget(
      const MaterialApp(
        home: Scaffold(
          body: MavlinkStatusBadge(connected: true, protocolVersion: '2.0'),
        ),
      ),
    );
    await tester.pump();

    expect(find.textContaining('MAVLink 2.0 Connected'), findsOneWidget);
    expect(find.byIcon(Icons.link), findsOneWidget);
  });

  testWidgets('MavlinkStatusBadge shows offline state', (tester) async {
    await tester.pumpWidget(
      const MaterialApp(
        home: Scaffold(
          body: MavlinkStatusBadge(connected: false),
        ),
      ),
    );
    await tester.pump();

    expect(find.text('MAVLink Offline'), findsOneWidget);
  });

  testWidgets('MavlinkAttitudeHorizon renders attitude readout', (tester) async {
    await tester.pumpWidget(
      const MaterialApp(
        home: Scaffold(
          body: MavlinkAttitudeHorizon(attitude: attitude),
        ),
      ),
    );
    await tester.pump();

    expect(find.textContaining('R 8°'), findsOneWidget);
    expect(find.text('-4°'), findsOneWidget);
    expect(find.byType(CustomPaint), findsWidgets);
  });

  testWidgets('TelemetryMapOverlay shows MAVLink badge and horizon', (tester) async {
    final device = Device(
      id: 'd1',
      tenantId: 't1',
      name: 'Pixhawk Drone',
      deviceType: 'drone',
      status: 'online',
      createdAt: DateTime(2026, 9, 10),
    );
    final marker = DeviceMapMarker(
      device: device,
      fix: const DeviceGpsFix(latitude: -6.2, longitude: 106.8, altitudeM: 50),
      roll: 8,
      pitch: -4,
      yaw: 120,
      battery: 90,
      speed: 12,
    );

    await tester.pumpWidget(
      MaterialApp(
        home: Scaffold(
          body: TelemetryMapOverlay(
            marker: marker,
            mavlinkStatus: const MavlinkStatus(
              deviceId: 'd1',
              connected: true,
              protocolVersion: '2.0',
              autopilot: 'ArduPilot',
            ),
            showMavlinkHud: true,
          ),
        ),
      ),
    );
    await tester.pump();

    expect(find.textContaining('MAVLink 2.0 Connected'), findsOneWidget);
    expect(find.text('MAVLink ATTITUDE'), findsOneWidget);
    expect(find.byType(MavlinkAttitudeHorizon), findsOneWidget);
  });
}
