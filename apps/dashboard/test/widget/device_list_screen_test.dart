import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:next_iot_dashboard/features/devices/data/device_repository.dart';
import 'package:next_iot_dashboard/features/devices/models/device_models.dart';
import 'package:next_iot_dashboard/features/devices/providers/device_provider.dart';
import 'package:next_iot_dashboard/features/devices/screens/device_list_screen.dart';
import 'package:next_iot_dashboard/features/devices/widgets/device_status_badge.dart';

class _TestDeviceNotifier extends DeviceNotifier {
  _TestDeviceNotifier(DeviceListState initial) : super(DeviceRepository()) {
    state = initial;
  }

  @override
  Future<void> loadDevices() async {}
}

void main() {
  final createdAt = DateTime(2026, 9, 10);

  final sampleDevices = [
    Device(
      id: '1',
      tenantId: 't1',
      name: 'Field Drone',
      deviceType: 'drone',
      status: 'online',
      lastSeenAt: DateTime(2026, 9, 10, 11, 0),
      createdAt: createdAt,
    ),
    Device(
      id: '2',
      tenantId: 't1',
      name: 'Warehouse Robot',
      deviceType: 'robot',
      status: 'offline',
      lastSeenAt: DateTime(2026, 9, 9, 8, 0),
      createdAt: createdAt,
    ),
    Device(
      id: '3',
      tenantId: 't1',
      name: 'LoRa Gateway',
      deviceType: 'lorawan',
      status: 'pending',
      createdAt: createdAt,
    ),
    Device(
      id: '4',
      tenantId: 't1',
      name: 'Cyberdeck Node',
      deviceType: 'cyberdeck',
      status: 'provisioned',
      createdAt: createdAt,
    ),
    Device(
      id: '5',
      tenantId: 't1',
      name: 'Temp Sensor',
      deviceType: 'sensor',
      status: 'online',
      lastSeenAt: DateTime(2026, 9, 10, 11, 55),
      createdAt: createdAt,
    ),
  ];

  Widget buildTestApp(DeviceListState initial) {
    return ProviderScope(
      overrides: [
        deviceProvider.overrideWith((ref) => _TestDeviceNotifier(initial)),
      ],
      child: const MaterialApp(
        home: Scaffold(body: DeviceListScreen()),
      ),
    );
  }

  testWidgets('DeviceListScreen renders device list with status badges', (tester) async {
    await tester.pumpWidget(
      buildTestApp(DeviceListState(devices: sampleDevices)),
    );
    await tester.pumpAndSettle();

    expect(find.text('Field Drone'), findsOneWidget);
    expect(find.text('Warehouse Robot'), findsOneWidget);
    expect(find.text('LoRa Gateway'), findsOneWidget);
    expect(find.text('Cyberdeck Node'), findsOneWidget);
    expect(find.text('Temp Sensor'), findsOneWidget);
    expect(find.byType(Card), findsNWidgets(5));
    expect(find.byType(DeviceStatusBadge), findsNWidgets(5));
    expect(find.textContaining('Last seen:'), findsNWidgets(5));
  });

  testWidgets('DeviceListScreen filters devices by status', (tester) async {
    await tester.pumpWidget(
      buildTestApp(DeviceListState(devices: sampleDevices)),
    );
    await tester.pumpAndSettle();

    await tester.tap(find.text('Offline'));
    await tester.pumpAndSettle();

    expect(find.text('Warehouse Robot'), findsOneWidget);
    expect(find.text('Field Drone'), findsNothing);
    expect(find.text('LoRa Gateway'), findsNothing);

    await tester.tap(find.text('Pending'));
    await tester.pumpAndSettle();

    expect(find.text('LoRa Gateway'), findsOneWidget);
    expect(find.text('Cyberdeck Node'), findsOneWidget);
    expect(find.text('Warehouse Robot'), findsNothing);

    await tester.tap(find.text('Online'));
    await tester.pumpAndSettle();

    expect(find.text('Field Drone'), findsOneWidget);
    expect(find.text('Temp Sensor'), findsOneWidget);
    expect(find.text('LoRa Gateway'), findsNothing);
  });

  testWidgets('DeviceListScreen shows register button and opens dialog', (tester) async {
    await tester.pumpWidget(
      buildTestApp(DeviceListState(devices: sampleDevices)),
    );
    await tester.pumpAndSettle();

    expect(find.text('Register New Device'), findsOneWidget);

    await tester.tap(find.text('Register New Device').first);
    await tester.pumpAndSettle();

    expect(find.text('Register New Device'), findsNWidgets(2));
    expect(find.text('Device name'), findsOneWidget);
    expect(find.text('Device type'), findsOneWidget);
    expect(find.text('Register'), findsOneWidget);
  });
}
