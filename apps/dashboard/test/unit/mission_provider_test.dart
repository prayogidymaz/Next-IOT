import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:latlong2/latlong.dart';
import 'package:mocktail/mocktail.dart';
import 'package:next_iot_dashboard/features/mission/data/command_repository.dart';
import 'package:next_iot_dashboard/features/mission/models/mission_models.dart';
import 'package:next_iot_dashboard/features/mission/providers/mission_provider.dart';

class _MockCommandRepository extends Mock implements CommandRepository {}

void main() {
  late _MockCommandRepository repo;

  setUpAll(() {
    registerFallbackValue(DeviceCommandType.rtl);
  });

  setUp(() {
    repo = _MockCommandRepository();
  });

  test('addWaypoint assigns sequential labels', () {
    final container = ProviderContainer(
      overrides: [commandRepositoryProvider.overrideWithValue(repo)],
    );
    addTearDown(container.dispose);

    final notifier = container.read(missionPlannerProvider.notifier);
    notifier.togglePlannerMode();
    notifier.addWaypoint(const LatLng(-6.2088, 106.8456));
    notifier.addWaypoint(const LatLng(-6.2100, 106.8500));

    final waypoints = container.read(missionPlannerProvider).waypoints;
    expect(waypoints, hasLength(2));
    expect(waypoints[0].label, 'P1');
    expect(waypoints[1].label, 'P2');
  });

  test('dispatchMission sends GO_TO_MISSION payload', () async {
    when(
      () => repo.dispatchCommand(
        deviceId: any(named: 'deviceId'),
        commandType: any(named: 'commandType'),
        params: any(named: 'params'),
      ),
    ).thenAnswer(
      (_) async => const DeviceCommandResult(
        id: 'cmd-1',
        commandType: 'GO_TO_MISSION',
        status: 'dispatched',
      ),
    );

    final container = ProviderContainer(
      overrides: [commandRepositoryProvider.overrideWithValue(repo)],
    );
    addTearDown(container.dispose);

    final notifier = container.read(missionPlannerProvider.notifier);
    notifier.togglePlannerMode();
    notifier.setTargetDevice('dev-1');
    notifier.addWaypoint(const LatLng(-6.2, 106.8));
    await notifier.dispatchMission();

    verify(
      () => repo.dispatchCommand(
        deviceId: 'dev-1',
        commandType: DeviceCommandType.goToMission,
        params: any(
          named: 'params',
          that: predicate<Map<String, dynamic>>(
            (p) => p['altitude_m'] == 60 && (p['waypoints'] as List).length == 1,
          ),
        ),
      ),
    ).called(1);
  });

  test('emergencyRtl sends RTL command', () async {
    when(
      () => repo.dispatchCommand(
        deviceId: any(named: 'deviceId'),
        commandType: DeviceCommandType.rtl,
        params: any(named: 'params'),
      ),
    ).thenAnswer(
      (_) async => const DeviceCommandResult(
        id: 'cmd-2',
        commandType: 'RTL',
        status: 'dispatched',
      ),
    );

    final container = ProviderContainer(
      overrides: [commandRepositoryProvider.overrideWithValue(repo)],
    );
    addTearDown(container.dispose);

    final notifier = container.read(missionPlannerProvider.notifier);
    notifier.setTargetDevice('dev-1');
    await notifier.emergencyRtl();

    verify(
      () => repo.dispatchCommand(
        deviceId: 'dev-1',
        commandType: DeviceCommandType.rtl,
        params: {},
      ),
    ).called(1);
  });
}
