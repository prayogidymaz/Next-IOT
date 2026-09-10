import 'package:flutter/material.dart';

import '../../../core/theme/tactical_theme.dart';
import '../../../core/widgets/glowing_led_badge.dart';
import '../models/alert_models.dart';

class SeverityBadge extends StatelessWidget {
  const SeverityBadge({super.key, required this.severity});

  final AlertSeverity severity;

  Color get _color => switch (severity) {
        AlertSeverity.critical => TacticalColors.critical,
        AlertSeverity.warning => TacticalColors.warning,
        AlertSeverity.info => TacticalColors.info,
      };

  @override
  Widget build(BuildContext context) {
    return GlowingLedBadge(
      label: severity.label,
      color: _color,
      pulse: severity == AlertSeverity.critical,
    );
  }
}
