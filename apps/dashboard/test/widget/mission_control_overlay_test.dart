import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:next_iot_dashboard/features/devices/data/device_repository.dart';
import 'package:next_iot_dashboard/features/mission/data/command_repository.dart';
import 'package:next_iot_dashboard/features/devices/models/device_models.dart';
import 'package:next_iot_dashboard/features/devices/providers/device_provider.dart';
import 'package:next_iot_dashboard/features/mission/providers/mission_provider.dart';
import 'package:next_iot_dashboard/features/mission/widgets/mission_control_overlay.dart';

class _TestDeviceNotifier extends DeviceNotifier {
  _TestDeviceNotifier(DeviceListState initial) : super(DeviceRepository()) {
    state = initial;
  }

  @override
  Future<void> loadDevices() async {}
}

class _TestMissionNotifier extends MissionPlannerNotifier {
  _TestMissionNotifier(MissionPlannerState initial) : super(CommandRepository()) {
    state = initial;
  }
}

void main() {
  final device = Device(
    id: 'dev-1',
    tenantId: 't1',
    name: 'Field Drone',
    deviceType: 'drone',
    status: 'offline',
    createdAt: DateTime(2026, 9, 10),
  );

  testWidgets('MissionControlOverlay shows altitude slider and dispatch buttons', (tester) async {
    await tester.pumpWidget(
      ProviderScope(
        overrides: [
          deviceProvider.overrideWith((ref) => _TestDeviceNotifier(DeviceListState(devices: [device]))),
          missionPlannerProvider.overrideWith(
            (ref) => _TestMissionNotifier(
              const MissionPlannerState(plannerMode: true, targetDeviceId: 'dev-1'),
            ),
          ),
        ],
        child: const MaterialApp(
          home: Scaffold(
            body: Stack(children: [MissionControlOverlay()]),
          ),
        ),
      ),
    );
    await tester.pump();

    expect(find.text('MISSION CONTROL'), findsOneWidget);
    expect(find.text('Dispatch Mission to Drone'), findsOneWidget);
    expect(find.text('Emergency RTL'), findsOneWidget);
    expect(find.byType(Slider), findsOneWidget);
  });
}
