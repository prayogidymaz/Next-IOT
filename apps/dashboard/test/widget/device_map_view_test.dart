import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:next_iot_dashboard/features/devices/models/device_models.dart';
import 'package:next_iot_dashboard/features/map/widgets/device_map_view.dart';
import 'package:next_iot_dashboard/features/map/widgets/telemetry_map_overlay.dart';
import 'package:next_iot_dashboard/features/telemetry/models/telemetry_models.dart';

void main() {
  final device = Device(
    id: 'd1',
    tenantId: 't1',
    name: 'Cyberdeck Node',
    deviceType: 'cyberdeck',
    status: 'online',
    createdAt: DateTime(2026, 9, 10),
  );

  testWidgets('DeviceMapView renders overlay and center button with GPS telemetry', (tester) async {
    await tester.pumpWidget(
      MaterialApp(
        home: Scaffold(
          body: DeviceMapView(
            device: device,
            telemetry: TelemetryLatest(
              deviceId: 'd1',
              metrics: const {
                'latitude': -6.2088,
                'longitude': 106.8456,
                'altitude_m': 28,
                'battery': 88,
                'roll': 4,
                'pitch': -1,
                'yaw': 90,
                'speed': 7.5,
              },
            ),
          ),
        ),
      ),
    );
    await tester.pump();

    expect(find.byType(TelemetryMapOverlay), findsOneWidget);
    expect(find.text('Center on Device'), findsOneWidget);
    expect(find.text('CYBERDECK NODE'), findsOneWidget);

    await tester.pumpWidget(const SizedBox.shrink());
    await tester.pump();
  });

  testWidgets('DeviceMapView shows no-fix message without GPS', (tester) async {
    await tester.pumpWidget(
      MaterialApp(
        home: Scaffold(
          body: DeviceMapView(
            device: device,
            telemetry: TelemetryLatest(
              deviceId: 'd1',
              metrics: const {'battery': 50},
            ),
          ),
        ),
      ),
    );
    await tester.pumpAndSettle();

    expect(find.text('No GPS fix available for this device.'), findsOneWidget);
  });
}
