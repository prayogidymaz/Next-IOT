import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:mocktail/mocktail.dart';
import 'package:next_iot_dashboard/features/alerts/data/alert_repository.dart';
import 'package:next_iot_dashboard/features/alerts/providers/alert_provider.dart';
import 'package:next_iot_dashboard/features/devices/data/device_repository.dart';
import 'package:next_iot_dashboard/features/devices/models/device_models.dart';
import 'package:next_iot_dashboard/features/devices/providers/device_provider.dart';
import 'package:next_iot_dashboard/features/map/providers/map_provider.dart';
import 'package:next_iot_dashboard/features/telemetry/data/telemetry_repository.dart';
import 'package:next_iot_dashboard/features/telemetry/models/telemetry_models.dart';

class _MockTelemetryRepository extends Mock implements TelemetryRepository {}

class _FakeAlertNotifier extends AlertNotifier {
  _FakeAlertNotifier() : super(AlertRepository()) {
    state = const AlertListState();
  }
}

class _TestDeviceNotifier extends DeviceNotifier {
  _TestDeviceNotifier(DeviceListState initial) : super(DeviceRepository()) {
    state = initial;
  }

  @override
  Future<void> loadDevices() async {}
}

void main() {
  late _MockTelemetryRepository telemetryRepo;

  final offlineDevice = Device(
    id: 'dev-offline',
    tenantId: 't1',
    name: 'Demo Sensor Node',
    deviceType: 'sensor',
    status: 'offline',
    createdAt: DateTime(2026, 9, 10),
  );

  setUp(() {
    telemetryRepo = _MockTelemetryRepository();
  });

  test('loadMarkers registers offline device when telemetry has GPS from history fallback', () async {
    when(() => telemetryRepo.fetchResolvableLatest('dev-offline')).thenAnswer(
      (_) async => TelemetryLatest(
        deviceId: 'dev-offline',
        source: 'history',
        metrics: const {
          'latitude': -6.2088,
          'longitude': 106.8456,
          'battery': 91,
        },
      ),
    );

    final container = ProviderContainer(
      overrides: [
        telemetryRepositoryProvider.overrideWithValue(telemetryRepo),
        alertProvider.overrideWith((ref) => _FakeAlertNotifier()),
      ],
    );
    addTearDown(container.dispose);

    await container.read(tacticalMapProvider.notifier).loadMarkers(
          devicesOverride: [offlineDevice],
        );

    final markers = container.read(tacticalMapProvider).markers;
    expect(markers, hasLength(1));
    expect(markers.first.device.status, 'offline');
    expect(markers.first.fix.latitude, -6.2088);
    verify(() => telemetryRepo.fetchResolvableLatest('dev-offline')).called(1);
  });

  test('refreshMarkersSilent does not set loading state', () async {
    when(() => telemetryRepo.fetchResolvableLatest('dev-offline')).thenAnswer(
      (_) async => TelemetryLatest(
        deviceId: 'dev-offline',
        source: 'cache',
        metrics: const {
          'latitude': -6.2090,
          'longitude': 106.8460,
          'battery': 90,
        },
      ),
    );

    final container = ProviderContainer(
      overrides: [
        deviceProvider.overrideWith((ref) => _TestDeviceNotifier(DeviceListState(devices: [offlineDevice]))),
        telemetryRepositoryProvider.overrideWithValue(telemetryRepo),
        alertProvider.overrideWith((ref) => _FakeAlertNotifier()),
      ],
    );
    addTearDown(container.dispose);

    final notifier = container.read(tacticalMapProvider.notifier);
    await notifier.loadMarkers();
    expect(container.read(tacticalMapProvider).isLoading, isFalse);

    await notifier.refreshMarkersSilent();
    expect(container.read(tacticalMapProvider).isLoading, isFalse);
    expect(container.read(tacticalMapProvider).markers.first.fix.latitude, -6.2090);
    verify(() => telemetryRepo.fetchResolvableLatest('dev-offline')).called(2);
  });
}
