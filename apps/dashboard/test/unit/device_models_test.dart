import 'package:flutter_test/flutter_test.dart';
import 'package:next_iot_dashboard/features/devices/models/device_models.dart';

void main() {
  group('Device.fromJson', () {
    test('parses API response', () {
      final device = Device.fromJson({
        'id': 'd1',
        'tenant_id': 't1',
        'name': 'Drone Alpha',
        'device_type': 'drone',
        'status': 'online',
        'last_seen_at': '2026-09-10T10:00:00Z',
        'metadata': [],
        'created_at': '2026-09-10T08:00:00Z',
      });

      expect(device.name, 'Drone Alpha');
      expect(device.deviceTypeLabel, 'Drone');
      expect(device.connectionStatus, DeviceConnectionStatus.online);
    });
  });

  group('DeviceConnectionStatus.fromApiStatus', () {
    test('maps lifecycle statuses to UI badges', () {
      expect(
        DeviceConnectionStatus.fromApiStatus('online'),
        DeviceConnectionStatus.online,
      );
      expect(
        DeviceConnectionStatus.fromApiStatus('offline'),
        DeviceConnectionStatus.offline,
      );
      expect(
        DeviceConnectionStatus.fromApiStatus('pending'),
        DeviceConnectionStatus.pending,
      );
      expect(
        DeviceConnectionStatus.fromApiStatus('provisioned'),
        DeviceConnectionStatus.pending,
      );
    });
  });

  group('filterDevices', () {
    final createdAt = DateTime(2026, 9, 10);
    final devices = [
      Device(
        id: '1',
        tenantId: 't',
        name: 'Online Node',
        deviceType: 'sensor',
        status: 'online',
        createdAt: createdAt,
      ),
      Device(
        id: '2',
        tenantId: 't',
        name: 'Offline Node',
        deviceType: 'robot',
        status: 'offline',
        createdAt: createdAt,
      ),
      Device(
        id: '3',
        tenantId: 't',
        name: 'Pending Node',
        deviceType: 'drone',
        status: 'pending',
        createdAt: createdAt,
      ),
    ];

    test('returns all devices for all filter', () {
      expect(filterDevices(devices, DeviceStatusFilter.all), devices);
    });

    test('filters online devices', () {
      final filtered = filterDevices(devices, DeviceStatusFilter.online);
      expect(filtered, hasLength(1));
      expect(filtered.first.name, 'Online Node');
    });

    test('filters offline devices', () {
      final filtered = filterDevices(devices, DeviceStatusFilter.offline);
      expect(filtered, hasLength(1));
      expect(filtered.first.name, 'Offline Node');
    });

    test('filters pending devices', () {
      final filtered = filterDevices(devices, DeviceStatusFilter.pending);
      expect(filtered, hasLength(1));
      expect(filtered.first.name, 'Pending Node');
    });

    test('filters devices by category', () {
      final filtered = filterDevices(
        devices,
        DeviceStatusFilter.all,
        category: DeviceCategoryFilter.droneUnmanned,
      );
      expect(filtered, hasLength(2));
      expect(filtered.map((d) => d.name), containsAll(['Offline Node', 'Pending Node']));

      final lora = filterDevices(
        devices,
        DeviceStatusFilter.all,
        category: DeviceCategoryFilter.fieldSensorsLora,
      );
      expect(lora, isEmpty);

      final sensors = filterDevices(
        devices,
        DeviceStatusFilter.all,
        category: DeviceCategoryFilter.agricultureAquaculture,
      );
      expect(sensors, hasLength(1));
      expect(sensors.first.name, 'Online Node');
    });

    test('filters smart home category by device type and category', () {
      final smartHome = Device(
        id: '4',
        tenantId: 't',
        name: 'Relay Node',
        deviceType: 'smart_home',
        deviceCategory: DeviceCategoryApi.smartHome,
        status: 'online',
        createdAt: createdAt,
      );
      final withSeeds = [...devices, smartHome];
      final filtered = filterDevices(
        withSeeds,
        DeviceStatusFilter.all,
        category: DeviceCategoryFilter.smartHomeBuilding,
      );
      expect(filtered, hasLength(1));
      expect(filtered.first.name, 'Relay Node');
    });

    test('combines status and category filters', () {
      final filtered = filterDevices(
        devices,
        DeviceStatusFilter.online,
        category: DeviceCategoryFilter.agricultureAquaculture,
      );
      expect(filtered, hasLength(1));
      expect(filtered.first.name, 'Online Node');
    });
  });

  group('formatLastSeen', () {
    test('returns Never seen when null', () {
      expect(formatLastSeen(null), 'Never seen');
    });

    test('returns relative time', () {
      final now = DateTime(2026, 9, 10, 12, 0);
      final lastSeen = DateTime(2026, 9, 10, 11, 30);
      expect(formatLastSeen(lastSeen, now: now), '30 min ago');
    });
  });
}
