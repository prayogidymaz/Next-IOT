import 'package:flutter/material.dart';

import '../../../core/theme/tactical_theme.dart';
import '../../../core/widgets/glowing_led_badge.dart';
import '../models/device_models.dart';

class DeviceStatusBadge extends StatelessWidget {
  const DeviceStatusBadge({super.key, required this.status});

  final DeviceConnectionStatus status;

  Color get _color => switch (status) {
        DeviceConnectionStatus.online => TacticalColors.success,
        DeviceConnectionStatus.offline => TacticalColors.critical,
        DeviceConnectionStatus.pending => TacticalColors.warning,
      };

  bool get _pulse => status == DeviceConnectionStatus.online;

  @override
  Widget build(BuildContext context) {
    return GlowingLedBadge(
      label: status.label,
      color: _color,
      pulse: _pulse,
    );
  }
}
