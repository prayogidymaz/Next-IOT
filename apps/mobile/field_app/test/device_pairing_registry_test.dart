import 'package:flutter_test/flutter_test.dart';
import 'package:next_iot_field_app/core/pairing/device_pairing_registry.dart';

// FleetDeviceRecord is exported via device_pairing_registry.dart

void main() {
  test('pairs BLE MAC and field slug from fleet metadata', () {
    final registry = DevicePairingRegistry.fromFleetDevices([
      FleetDeviceRecord(
        id: '00000000-0000-0000-0000-000000000099',
        name: 'Biofloc Node A',
        metadata: const {
          'ble_mac': 'AA:BB:CC:11:22:33',
          'field_slug': 'esp32-pond-a',
        },
      ),
    ]);

    expect(
      registry.resolve(bleMac: 'AA:BB:CC:11:22:33'),
      '00000000-0000-0000-0000-000000000099',
    );
    expect(
      registry.resolve(localSlug: 'esp32-pond-a'),
      '00000000-0000-0000-0000-000000000099',
    );
    expect(
      registry.resolve(mdnsHost: 'esp32-pond-a.local'),
      '00000000-0000-0000-0000-000000000099',
    );
  });
}
