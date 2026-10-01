import 'package:flutter/material.dart';

enum DeviceConnectionStatus {
  online,
  offline,
  pending;

  static DeviceConnectionStatus fromApiStatus(String status) {
    switch (status) {
      case 'online':
        return DeviceConnectionStatus.online;
      case 'offline':
      case 'deactivated':
        return DeviceConnectionStatus.offline;
      case 'pending':
      case 'provisioned':
      default:
        return DeviceConnectionStatus.pending;
    }
  }

  String get label {
    switch (this) {
      case DeviceConnectionStatus.online:
        return 'Online';
      case DeviceConnectionStatus.offline:
        return 'Offline';
      case DeviceConnectionStatus.pending:
        return 'Pending';
    }
  }
}

/// Backend `device_category` taxonomy values.
abstract final class DeviceCategoryApi {
  static const smartHome = 'SMART_HOME';
  static const droneUnmanned = 'DRONE_UNMANNED';
  static const agricultureAquaculture = 'AGRICULTURE_AQUACULTURE';
  static const fieldSensorsLora = 'FIELD_SENSORS_LORA';
  static const industrialTelemetry = 'INDUSTRIAL_TELEMETRY';
  static const smartAssetFleet = 'SMART_ASSET_FLEET';
}

enum DeviceType {
  drone('drone', 'Drone'),
  robot('robot', 'Robot'),
  lorawan('lorawan', 'LoRaWAN'),
  cyberdeck('cyberdeck', 'Cyberdeck'),
  sensor('sensor', 'Sensor'),
  smartHome('smart_home', 'Smart Home');

  const DeviceType(this.apiValue, this.label);

  final String apiValue;
  final String label;

  static DeviceType? fromApiValue(String value) {
    for (final type in DeviceType.values) {
      if (type.apiValue == value) return type;
    }
    return null;
  }
}

class Device {
  const Device({
    required this.id,
    required this.tenantId,
    required this.name,
    required this.deviceType,
    required this.status,
    this.deviceCategory,
    this.lastSeenAt,
    required this.createdAt,
  });

  final String id;
  final String tenantId;
  final String name;
  final String deviceType;
  final String? deviceCategory;
  final String status;
  final DateTime? lastSeenAt;
  final DateTime createdAt;

  DeviceConnectionStatus get connectionStatus =>
      DeviceConnectionStatus.fromApiStatus(status);

  String get deviceTypeLabel =>
      DeviceType.fromApiValue(deviceType)?.label ?? deviceType;

  factory Device.fromJson(Map<String, dynamic> json) => Device(
        id: json['id'] as String,
        tenantId: json['tenant_id'] as String,
        name: json['name'] as String,
        deviceType: json['device_type'] as String,
        deviceCategory: json['device_category'] as String?,
        status: json['status'] as String,
        lastSeenAt: json['last_seen_at'] != null
            ? DateTime.parse(json['last_seen_at'] as String)
            : null,
        createdAt: DateTime.parse(json['created_at'] as String),
      );
}

class RegisterDeviceRequest {
  const RegisterDeviceRequest({
    required this.name,
    required this.deviceType,
    this.deviceCategory,
  });

  final String name;
  final String deviceType;
  final String? deviceCategory;

  Map<String, dynamic> toJson() => {
        'name': name,
        'device_type': deviceType,
        if (deviceCategory != null) 'device_category': deviceCategory,
      };
}

class RegisterDeviceResult {
  const RegisterDeviceResult({
    required this.device,
    required this.provisioningToken,
    required this.provisioningExpiresInHours,
  });

  final Device device;
  final String provisioningToken;
  final int provisioningExpiresInHours;

  factory RegisterDeviceResult.fromJson(Map<String, dynamic> json) {
    return RegisterDeviceResult(
      device: Device.fromJson(json['device'] as Map<String, dynamic>),
      provisioningToken: json['provisioning_token'] as String,
      provisioningExpiresInHours: json['provisioning_expires_in_hours'] as int,
    );
  }
}

enum DeviceStatusFilter { all, online, offline, pending }

extension DeviceStatusFilterX on DeviceStatusFilter {
  String get label {
    switch (this) {
      case DeviceStatusFilter.all:
        return 'All';
      case DeviceStatusFilter.online:
        return 'Online';
      case DeviceStatusFilter.offline:
        return 'Offline';
      case DeviceStatusFilter.pending:
        return 'Pending';
    }
  }

  bool matches(Device device) {
    switch (this) {
      case DeviceStatusFilter.all:
        return true;
      case DeviceStatusFilter.online:
        return device.connectionStatus == DeviceConnectionStatus.online;
      case DeviceStatusFilter.offline:
        return device.connectionStatus == DeviceConnectionStatus.offline;
      case DeviceStatusFilter.pending:
        return device.connectionStatus == DeviceConnectionStatus.pending;
    }
  }
}

enum DeviceCategoryFilter {
  all,
  droneUnmanned,
  agricultureAquaculture,
  fieldSensorsLora,
  industrialTelemetry,
  smartAssetFleet,
  smartHomeBuilding;

  String get label {
    switch (this) {
      case DeviceCategoryFilter.all:
        return 'All Categories';
      case DeviceCategoryFilter.droneUnmanned:
        return 'Drone & Unmanned';
      case DeviceCategoryFilter.agricultureAquaculture:
        return 'Agriculture & Aquaculture';
      case DeviceCategoryFilter.fieldSensorsLora:
        return 'Field Sensors (LoRa)';
      case DeviceCategoryFilter.industrialTelemetry:
        return 'Industrial Telemetry';
      case DeviceCategoryFilter.smartAssetFleet:
        return 'Smart Asset & Fleet';
      case DeviceCategoryFilter.smartHomeBuilding:
        return 'Smart Home & Building';
    }
  }

  String get emoji {
    switch (this) {
      case DeviceCategoryFilter.all:
        return '📋';
      case DeviceCategoryFilter.droneUnmanned:
        return '🚁';
      case DeviceCategoryFilter.agricultureAquaculture:
        return '🌱';
      case DeviceCategoryFilter.fieldSensorsLora:
        return '📡';
      case DeviceCategoryFilter.industrialTelemetry:
        return '🏭';
      case DeviceCategoryFilter.smartAssetFleet:
        return '🚜';
      case DeviceCategoryFilter.smartHomeBuilding:
        return '🏠';
    }
  }

  IconData? get chipIcon {
    if (this == DeviceCategoryFilter.smartHomeBuilding) {
      return Icons.home_work_outlined;
    }
    return null;
  }

  String get chipLabel => '$emoji $label';

  String get helpText {
    switch (this) {
      case DeviceCategoryFilter.all:
        return 'Tampilkan semua perangkat tanpa memfilter kategori operasional.';
      case DeviceCategoryFilter.droneUnmanned:
        return 'Perangkat pesawat/robot tanpa awak untuk patroli, inspeksi, '
            'dan pemantauan dari udara atau area sulit dijangkau.';
      case DeviceCategoryFilter.agricultureAquaculture:
        return 'Sensor pertanian & budidaya perairan — suhu air, DO/oksigen '
            'terlarut, pH, kelembaban tanah, dan kualitas kolam.';
      case DeviceCategoryFilter.fieldSensorsLora:
        return 'Node sensor lapangan berjarak jauh via LoRa/LoRaWAN — '
            'hemat baterai, cocok untuk area tanpa jaringan Wi-Fi.';
      case DeviceCategoryFilter.industrialTelemetry:
        return 'Gateway & sensor industri (Modbus/RS485) untuk mesin pabrik, '
            'generator, tangki, dan aset kritikal.';
      case DeviceCategoryFilter.smartAssetFleet:
        return 'Kendaraan, armada, dan aset bergerak yang dilacak posisi, '
            'status operasi, dan kesehatan perangkat secara real-time.';
      case DeviceCategoryFilter.smartHomeBuilding:
        return 'Relay Switch, Smart Locks, HVAC Controller, PIR Sensors, '
            'Power Metering — telemetri relay_state, pir_motion, hvac_temp, lock_state.';
    }
  }

  bool matches(Device device) {
    if (this == DeviceCategoryFilter.all) return true;
    final type = DeviceType.fromApiValue(device.deviceType);
    final category = device.deviceCategory?.toUpperCase();
    return switch (this) {
      DeviceCategoryFilter.all => true,
      DeviceCategoryFilter.droneUnmanned =>
        category == DeviceCategoryApi.droneUnmanned ||
            type == DeviceType.drone ||
            type == DeviceType.robot,
      DeviceCategoryFilter.agricultureAquaculture =>
        category == DeviceCategoryApi.agricultureAquaculture ||
            type == DeviceType.sensor,
      DeviceCategoryFilter.fieldSensorsLora =>
        category == DeviceCategoryApi.fieldSensorsLora ||
            type == DeviceType.lorawan,
      DeviceCategoryFilter.industrialTelemetry =>
        category == DeviceCategoryApi.industrialTelemetry ||
            type == DeviceType.cyberdeck,
      DeviceCategoryFilter.smartAssetFleet =>
        category == DeviceCategoryApi.smartAssetFleet ||
            type == DeviceType.drone ||
            type == DeviceType.robot,
      DeviceCategoryFilter.smartHomeBuilding =>
        category == DeviceCategoryApi.smartHome ||
            type == DeviceType.smartHome,
    };
  }
}

List<Device> filterDevices(
  List<Device> devices,
  DeviceStatusFilter status, {
  DeviceCategoryFilter category = DeviceCategoryFilter.all,
}) {
  return devices
      .where((d) => status.matches(d) && category.matches(d))
      .toList();
}

String formatLastSeen(DateTime? lastSeenAt, {DateTime? now}) {
  if (lastSeenAt == null) return 'Never seen';

  final reference = now ?? DateTime.now();
  final diff = reference.difference(lastSeenAt.toLocal());

  if (diff.inSeconds < 60) return 'Just now';
  if (diff.inMinutes < 60) {
    final m = diff.inMinutes;
    return '$m min ago';
  }
  if (diff.inHours < 24) {
    final h = diff.inHours;
    return '$h hr ago';
  }
  if (diff.inDays < 7) {
    final d = diff.inDays;
    return '$d day${d == 1 ? '' : 's'} ago';
  }
  return '${lastSeenAt.toLocal()}'.split('.').first;
}
