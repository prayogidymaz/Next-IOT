import '../models/device_models.dart';

/// Demo Smart Home & Building devices shown when the category filter is active.
List<Device> smartHomeSeedDevices({DateTime? now}) {
  final createdAt = now ?? DateTime(2026, 9, 10, 8);
  return [
    Device(
      id: 'seed-smart-relay-1',
      tenantId: 'demo-tenant',
      name: 'Lobby Relay Switch',
      deviceType: DeviceType.smartHome.apiValue,
      deviceCategory: DeviceCategoryApi.smartHome,
      status: 'online',
      lastSeenAt: createdAt.add(const Duration(minutes: 2)),
      createdAt: createdAt,
    ),
    Device(
      id: 'seed-smart-lock-1',
      tenantId: 'demo-tenant',
      name: 'Front Door Smart Lock',
      deviceType: DeviceType.smartHome.apiValue,
      deviceCategory: DeviceCategoryApi.smartHome,
      status: 'online',
      lastSeenAt: createdAt.add(const Duration(minutes: 5)),
      createdAt: createdAt,
    ),
    Device(
      id: 'seed-smart-hvac-1',
      tenantId: 'demo-tenant',
      name: 'HVAC Zone Controller',
      deviceType: DeviceType.smartHome.apiValue,
      deviceCategory: DeviceCategoryApi.smartHome,
      status: 'offline',
      lastSeenAt: createdAt.subtract(const Duration(hours: 3)),
      createdAt: createdAt,
    ),
    Device(
      id: 'seed-smart-pir-1',
      tenantId: 'demo-tenant',
      name: 'Corridor PIR Motion',
      deviceType: DeviceType.smartHome.apiValue,
      deviceCategory: DeviceCategoryApi.smartHome,
      status: 'online',
      lastSeenAt: createdAt.add(const Duration(minutes: 1)),
      createdAt: createdAt,
    ),
    Device(
      id: 'seed-smart-meter-1',
      tenantId: 'demo-tenant',
      name: 'Main Panel Power Meter',
      deviceType: DeviceType.smartHome.apiValue,
      deviceCategory: DeviceCategoryApi.smartHome,
      status: 'pending',
      createdAt: createdAt,
    ),
  ];
}

List<Device> mergeSmartHomeSeed(List<Device> devices) {
  final existingIds = devices.map((d) => d.id).toSet();
  return [
    ...devices,
    ...smartHomeSeedDevices().where((d) => !existingIds.contains(d.id)),
  ];
}
