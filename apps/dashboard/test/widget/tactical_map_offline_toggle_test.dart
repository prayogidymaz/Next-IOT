import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:next_iot_dashboard/features/devices/data/device_repository.dart';
import 'package:next_iot_dashboard/features/devices/models/device_models.dart';
import 'package:next_iot_dashboard/features/devices/providers/device_provider.dart';
import 'package:next_iot_dashboard/features/map/config/tile_url_resolver.dart';
import 'package:next_iot_dashboard/features/map/models/device_map_models.dart';
import 'package:next_iot_dashboard/features/map/providers/map_provider.dart';
import 'package:next_iot_dashboard/features/map/providers/map_tile_provider.dart';
import 'package:next_iot_dashboard/features/map/screens/tactical_map_screen.dart';
import 'package:next_iot_dashboard/features/map/utils/gps_utils.dart';

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

class _TestTileModeNotifier extends MapTileModeNotifier {
  _TestTileModeNotifier(MapTileMode initial) : super() {
    state = initial;
  }

  @override
  Future<void> toggle() async {
    state = state == MapTileMode.online ? MapTileMode.offline : MapTileMode.online;
  }
}

void main() {
  final device = Device(
    id: 'd1',
    tenantId: 't1',
    name: 'Demo Sensor Node',
    deviceType: 'sensor',
    status: 'online',
    createdAt: DateTime(2026, 9, 10),
  );

  final marker = DeviceMapMarker(
    device: device,
    fix: const DeviceGpsFix(
      latitude: kDefaultMapLatitude,
      longitude: kDefaultMapLongitude,
      altitudeM: 60,
    ),
    battery: 90,
  );

  testWidgets('TacticalMapScreen shows offline map mode toggle', (tester) async {
    await tester.pumpWidget(
      ProviderScope(
        overrides: [
          deviceProvider.overrideWith((ref) => _TestDeviceNotifier(DeviceListState(devices: [device]))),
          tacticalMapProvider.overrideWith((ref) => _TestMapNotifier(ref, TacticalMapState(markers: [marker]))),
          mapTileModeProvider.overrideWith((ref) => _TestTileModeNotifier(MapTileMode.online)),
        ],
        child: const MaterialApp(home: Scaffold(body: TacticalMapScreen())),
      ),
    );
    await tester.pump();

    expect(find.text('Online Map'), findsOneWidget);

    await tester.pumpWidget(const SizedBox.shrink());
    await tester.pump();
  });

  testWidgets('Offline map toggle switches chip label', (tester) async {
    late _TestTileModeNotifier tileNotifier;

    await tester.pumpWidget(
      ProviderScope(
        overrides: [
          deviceProvider.overrideWith((ref) => _TestDeviceNotifier(DeviceListState(devices: [device]))),
          tacticalMapProvider.overrideWith((ref) => _TestMapNotifier(ref, TacticalMapState(markers: [marker]))),
          mapTileModeProvider.overrideWith((ref) {
            tileNotifier = _TestTileModeNotifier(MapTileMode.online);
            return tileNotifier;
          }),
        ],
        child: const MaterialApp(home: Scaffold(body: TacticalMapScreen())),
      ),
    );
    await tester.pump();

    await tileNotifier.toggle();
    await tester.pump();

    expect(find.text('Offline Map'), findsOneWidget);

    await tester.pumpWidget(const SizedBox.shrink());
    await tester.pump();
  });
}
