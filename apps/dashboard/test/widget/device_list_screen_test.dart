import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:next_iot_dashboard/features/devices/data/device_repository.dart';
import 'package:next_iot_dashboard/features/devices/models/device_models.dart';
import 'package:next_iot_dashboard/features/devices/providers/device_provider.dart';
import 'package:next_iot_dashboard/features/alerts/data/alert_repository.dart';
import 'package:next_iot_dashboard/features/alerts/providers/alert_provider.dart';
import 'package:next_iot_dashboard/features/automation/providers/automation_summary_provider.dart';
import 'package:next_iot_dashboard/features/dashboard/widgets/compact_device_table.dart';
import 'package:next_iot_dashboard/features/auth/data/permissions_repository.dart';
import 'package:next_iot_dashboard/features/auth/providers/permissions_provider.dart';
import 'package:next_iot_dashboard/features/devices/screens/device_list_screen.dart';
import 'package:next_iot_dashboard/features/devices/widgets/device_category_filter_bar.dart';
import 'package:next_iot_dashboard/features/devices/widgets/device_status_badge.dart';

class _TestDeviceNotifier extends DeviceNotifier {
  _TestDeviceNotifier(DeviceListState initial) : super(DeviceRepository()) {
    state = initial;
  }

  @override
  Future<void> loadDevices() async {}
}

void main() {
  Future<void> useLargeSurface(WidgetTester tester) async {
    await tester.binding.setSurfaceSize(const Size(1280, 1200));
    addTearDown(() => tester.binding.setSurfaceSize(null));
  }

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
        permissionsProvider.overrideWith(
          (ref) => fullAccessPermissionsNotifier(
            ref.watch(permissionsRepositoryProvider),
          ),
        ),
        deviceProvider.overrideWith((ref) => _TestDeviceNotifier(initial)),
        automationPipelinesSummaryProvider.overrideWith((ref) async => []),
        alertProvider.overrideWith(
          (ref) => AlertNotifier(ref.watch(alertRepositoryProvider)),
        ),
      ],
      child: const MaterialApp(
        home: Scaffold(body: DeviceListScreen()),
      ),
    );
  }

  testWidgets('DeviceListScreen renders device list with status badges',
      (tester) async {
    await useLargeSurface(tester);
    await tester.pumpWidget(
      buildTestApp(DeviceListState(devices: sampleDevices)),
    );
    await tester.pumpAndSettle();

    expect(find.text('Field Drone'), findsOneWidget);
    expect(find.text('Warehouse Robot'), findsOneWidget);
    expect(find.text('LoRa Gateway'), findsOneWidget);
    expect(find.text('Cyberdeck Node'), findsOneWidget);
    expect(find.text('Temp Sensor'), findsOneWidget);
    expect(find.byKey(CompactDeviceTable.tableKey), findsOneWidget);
    expect(find.byType(DeviceStatusBadge), findsNWidgets(5));
    expect(find.text('Last seen'), findsOneWidget);
  });

  testWidgets('DeviceListScreen filters devices by status', (tester) async {
    await useLargeSurface(tester);
    await tester.pumpWidget(
      buildTestApp(DeviceListState(devices: sampleDevices)),
    );
    await tester.pumpAndSettle();

    Future<void> tapStatusFilter(String label) async {
      await tester.tap(
        find.descendant(
          of: find.byKey(DeviceStatusFilterBar.filterBarKey),
          matching: find.text(label),
        ),
      );
    }

    await tapStatusFilter('Offline');
    await tester.pumpAndSettle();

    expect(find.text('Warehouse Robot'), findsOneWidget);
    expect(find.text('Field Drone'), findsNothing);
    expect(find.text('LoRa Gateway'), findsNothing);

    await tapStatusFilter('Pending');
    await tester.pumpAndSettle();

    expect(find.text('LoRa Gateway'), findsOneWidget);
    expect(find.text('Cyberdeck Node'), findsOneWidget);
    expect(find.text('Warehouse Robot'), findsNothing);

    await tapStatusFilter('Online');
    await tester.pumpAndSettle();

    expect(find.text('Field Drone'), findsOneWidget);
    expect(find.text('Temp Sensor'), findsOneWidget);
    expect(find.text('LoRa Gateway'), findsNothing);
  });

  testWidgets('DeviceListScreen filters devices by category', (tester) async {
    await useLargeSurface(tester);
    await tester.pumpWidget(
      buildTestApp(DeviceListState(devices: sampleDevices)),
    );
    await tester.pumpAndSettle();

    await tester.tap(find.textContaining('Field Sensors (LoRa)'));
    await tester.pumpAndSettle();

    expect(find.text('LoRa Gateway'), findsOneWidget);
    expect(find.text('Field Drone'), findsNothing);

    await tester.tap(find.textContaining('Agriculture & Aquaculture'));
    await tester.pumpAndSettle();

    expect(find.text('Temp Sensor'), findsOneWidget);
    expect(find.text('LoRa Gateway'), findsNothing);
  });

  testWidgets('DeviceListScreen opens IoT glossary dialog', (tester) async {
    await useLargeSurface(tester);
    await tester.pumpWidget(
      buildTestApp(DeviceListState(devices: sampleDevices)),
    );
    await tester.pumpAndSettle();

    await tester.tap(find.byKey(const Key('device-iot-glossary-button')));
    await tester.pumpAndSettle();

    expect(find.text('Kamus Istilah IoT'), findsWidgets);
    expect(find.text('MAVLink'), findsOneWidget);
    expect(find.text('Geofence'), findsOneWidget);
  });

  testWidgets('DeviceListScreen scrolls on small viewport without overflow',
      (tester) async {
    await tester.binding.setSurfaceSize(const Size(390, 640));
    addTearDown(() => tester.binding.setSurfaceSize(null));

    await tester.pumpWidget(
      buildTestApp(DeviceListState(devices: sampleDevices)),
    );
    await tester.pumpAndSettle();

    expect(tester.takeException(), isNull);
    expect(find.byType(CustomScrollView), findsOneWidget);

    await tester.drag(find.byType(CustomScrollView), const Offset(0, -240));
    await tester.pumpAndSettle();

    expect(tester.takeException(), isNull);
    expect(find.text('Field Drone'), findsOneWidget);
  });

  testWidgets('DeviceListScreen shows register button and opens dialog',
      (tester) async {
    await useLargeSurface(tester);
    await tester.pumpWidget(
      buildTestApp(DeviceListState(devices: sampleDevices)),
    );
    await tester.pumpAndSettle();

    expect(find.text('Register New Device'), findsOneWidget);

    await tester.tap(find.text('Register New Device').first);
    await tester.pumpAndSettle();

    expect(find.text('Device registration'), findsOneWidget);
    expect(find.text('Bulk register'), findsOneWidget);
    expect(find.text('Device name'), findsOneWidget);
    expect(find.text('Device type'), findsOneWidget);
    expect(find.text('Register'), findsOneWidget);
  });
}
