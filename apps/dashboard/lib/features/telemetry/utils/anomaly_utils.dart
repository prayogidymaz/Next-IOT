import 'package:flutter/material.dart';

import '../../../core/theme/tactical_theme.dart';

Color anomalySeverityColor(String severity) {
  switch (severity) {
    case 'critical':
      return TacticalColors.critical;
    case 'warning':
      return TacticalColors.warning;
    default:
      return TacticalColors.info;
  }
}

String anomalyTypeLabel(String type) {
  switch (type) {
    case 'voltage_drop':
      return 'Voltage Drop';
    case 'battery_overheat':
      return 'Overheat';
    case 'signal_loss':
      return 'Signal Loss';
    case 'altitude_deviation':
      return 'Altitude Dev';
    case 'speed_deviation':
      return 'Speed Dev';
    case 'geofence_breach':
      return 'Geofence Breach';
    default:
      return type;
  }
}

bool anomalyHasLocation(Map<String, dynamic> metadata) {
  final lat = metadata['lat'];
  final lon = metadata['lon'];
  return lat != null && lon != null;
}

(bool, double, double)? anomalyLkp(Map<String, dynamic> metadata) {
  if (!anomalyHasLocation(metadata)) return null;
  return (true, (metadata['lat'] as num).toDouble(), (metadata['lon'] as num).toDouble());
}

IconData anomalyTypeIcon(String type) {
  switch (type) {
    case 'voltage_drop':
      return Icons.battery_alert;
    case 'battery_overheat':
      return Icons.thermostat;
    case 'signal_loss':
      return Icons.signal_cellular_off;
    case 'altitude_deviation':
      return Icons.height;
    case 'speed_deviation':
      return Icons.speed;
    case 'geofence_breach':
      return Icons.fence;
    default:
      return Icons.warning_amber;
  }
}
