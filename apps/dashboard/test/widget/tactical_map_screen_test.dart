import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:next_iot_dashboard/features/devices/data/device_repository.dart';
import 'package:next_iot_dashboard/features/devices/models/device_models.dart';
import 'package:next_iot_dashboard/features/devices/providers/device_provider.dart';
import 'package:next_iot_dashboard/features/map/models/device_map_models.dart';
import 'package:next_iot_dashboard/features/map/providers/map_provider.dart';
import 'package:next_iot_dashboard/features/map/screens/tactical_map_screen.dart';
import 'package:next_iot_dashboard/features/map/utils/gps_utils.dart';
import 'package:next_iot_dashboard/features/mission/data/command_repository.dart';
import 'package:next_iot_dashboard/features/mission/providers/mission_provider.dart';

class _TestDeviceNotifier extends DeviceNotifier {
  _TestDeviceNotifier(DeviceListState initial) : super(DeviceRepository()) {
    state = initial;
  }

  @override
  Future<void> loadDevices() async {}
}

class _TestMapNotifier extends TacticalMapNotifier {
  _TestMapNotifier(Ref ref, TacticalMapState initial) : super(ref) {
    state = initial;
  }

  @override
  Future<void> loadMarkers({List<Device>? devicesOverride, bool silent = false}) async {}
}

void main() {
  final offlineDevice = Device(
    id: 'd1',
    tenantId: 't1',
    name: 'Demo Sensor Node',
    deviceType: 'sensor',
    status: 'offline',
    createdAt: DateTime(2026, 9, 10),
  );

  final marker = DeviceMapMarker(
    device: offlineDevice,
    fix: const DeviceGpsFix(
      latitude: kDefaultMapLatitude,
      longitude: kDefaultMapLongitude,
      altitudeM: 28,
      speed: 10,
    ),
    battery: 91,
    roll: 5,
    pitch: -2,
    yaw: 120,
    speed: 10,
  );

  Widget buildApp(TacticalMapState state) {
    return ProviderScope(
      overrides: [
        deviceProvider.overrideWith((ref) => _TestDeviceNotifier(DeviceListState(devices: [offlineDevice]))),
        tacticalMapProvider.overrideWith((ref) => _TestMapNotifier(ref, state)),
      ],
      child: const MaterialApp(
        home: Scaffold(body: TacticalMapScreen()),
      ),
    );
  }

  testWidgets('TacticalMapScreen renders map header and GPS fix count', (tester) async {
    await tester.pumpWidget(buildApp(TacticalMapState(markers: [marker])));
    await tester.pump();

    expect(find.text('TACTICAL MAP'), findsOneWidget);
    expect(find.text('1 GPS FIX'), findsOneWidget);

    await tester.pumpWidget(const SizedBox.shrink());
    await tester.pump();
  });

  testWidgets('TacticalMapScreen shows overlay for offline device with GPS telemetry', (tester) async {
    await tester.pumpWidget(
      buildApp(TacticalMapState(markers: [marker], selectedDeviceId: 'd1')),
    );
    await tester.pump();

    expect(find.text('DEMO SENSOR NODE'), findsOneWidget);
    expect(find.text('OFFLINE'), findsOneWidget);
    expect(find.text('Center on Device'), findsWidgets);

    await tester.pumpWidget(const SizedBox.shrink());
    await tester.pump();
  });

  testWidgets('TacticalMapScreen shows mission planner toggle', (tester) async {
    await tester.pumpWidget(buildApp(TacticalMapState(markers: [marker])));
    await tester.pump();

    expect(find.text('Mission Planner'), findsOneWidget);

    await tester.pumpWidget(const SizedBox.shrink());
    await tester.pump();
  });

  testWidgets('TacticalMapScreen shows empty state without GPS markers', (tester) async {
    await tester.pumpWidget(buildApp(const TacticalMapState()));
    await tester.pump();

    expect(find.text('No devices with GPS telemetry yet.'), findsOneWidget);

    await tester.pumpWidget(const SizedBox.shrink());
    await tester.pump();
  });
}
