import 'package:flutter/material.dart';

import '../../../core/theme/tactical_theme.dart';
import '../../devices/models/device_models.dart';

enum MapMarkerStatus { online, offline, pending, alert }

extension MapMarkerStatusX on MapMarkerStatus {
  Color get color {
    switch (this) {
      case MapMarkerStatus.online:
        return TacticalColors.borderNeon;
      case MapMarkerStatus.offline:
        return TacticalColors.critical;
      case MapMarkerStatus.pending:
        return TacticalColors.warning;
      case MapMarkerStatus.alert:
        return TacticalColors.critical;
    }
  }

  bool get pulse =>
      this == MapMarkerStatus.online || this == MapMarkerStatus.alert;
}

class DeviceGpsFix {
  const DeviceGpsFix({
    required this.latitude,
    required this.longitude,
    this.altitudeM,
    this.speed,
  });

  final double latitude;
  final double longitude;
  final double? altitudeM;
  final double? speed;

  DeviceGpsFix copyWith({
    double? latitude,
    double? longitude,
    double? altitudeM,
    double? speed,
  }) {
    return DeviceGpsFix(
      latitude: latitude ?? this.latitude,
      longitude: longitude ?? this.longitude,
      altitudeM: altitudeM ?? this.altitudeM,
      speed: speed ?? this.speed,
    );
  }
}

class DeviceMapMarker {
  const DeviceMapMarker({
    required this.device,
    required this.fix,
    this.battery,
    this.roll,
    this.pitch,
    this.yaw,
    this.speed,
    this.hasActiveAlert = false,
    this.recordedAt,
    this.doMgL,
    this.ph,
    this.rssi,
  });

  final Device device;
  final DeviceGpsFix fix;
  final double? battery;
  final double? roll;
  final double? pitch;
  final double? yaw;
  final double? speed;
  final bool hasActiveAlert;
  final DateTime? recordedAt;
  final double? doMgL;
  final double? ph;
  final double? rssi;

  DeviceMapMarker copyWith({
    Device? device,
    DeviceGpsFix? fix,
    double? battery,
    double? roll,
    double? pitch,
    double? yaw,
    double? speed,
    bool? hasActiveAlert,
    DateTime? recordedAt,
    double? doMgL,
    double? ph,
    double? rssi,
  }) {
    return DeviceMapMarker(
      device: device ?? this.device,
      fix: fix ?? this.fix,
      battery: battery ?? this.battery,
      roll: roll ?? this.roll,
      pitch: pitch ?? this.pitch,
      yaw: yaw ?? this.yaw,
      speed: speed ?? this.speed,
      hasActiveAlert: hasActiveAlert ?? this.hasActiveAlert,
      recordedAt: recordedAt ?? this.recordedAt,
      doMgL: doMgL ?? this.doMgL,
      ph: ph ?? this.ph,
      rssi: rssi ?? this.rssi,
    );
  }

  MapMarkerStatus get status => resolveMarkerStatusFromDevice(
        connectionStatus: device.connectionStatus,
        hasActiveAlert: hasActiveAlert,
      );
}

MapMarkerStatus resolveMarkerStatusFromDevice({
  required DeviceConnectionStatus connectionStatus,
  required bool hasActiveAlert,
}) {
  if (hasActiveAlert) return MapMarkerStatus.alert;
  switch (connectionStatus) {
    case DeviceConnectionStatus.online:
      return MapMarkerStatus.online;
    case DeviceConnectionStatus.offline:
      return MapMarkerStatus.offline;
    case DeviceConnectionStatus.pending:
      return MapMarkerStatus.pending;
  }
}
