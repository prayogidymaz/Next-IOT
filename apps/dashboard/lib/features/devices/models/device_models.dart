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

enum DeviceType {
  drone('drone', 'Drone'),
  robot('robot', 'Robot'),
  lorawan('lorawan', 'LoRaWAN'),
  cyberdeck('cyberdeck', 'Cyberdeck'),
  sensor('sensor', 'Sensor');

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
    this.lastSeenAt,
    required this.createdAt,
  });

  final String id;
  final String tenantId;
  final String name;
  final String deviceType;
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
  });

  final String name;
  final String deviceType;

  Map<String, dynamic> toJson() => {
        'name': name,
        'device_type': deviceType,
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
      provisioningExpiresInHours:
          json['provisioning_expires_in_hours'] as int,
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

List<Device> filterDevices(List<Device> devices, DeviceStatusFilter filter) {
  return devices.where((d) => filter.matches(d)).toList();
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
