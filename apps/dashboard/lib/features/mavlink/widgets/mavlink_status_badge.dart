import 'package:flutter/material.dart';

import '../../../core/theme/tactical_theme.dart';

class MavlinkStatusBadge extends StatelessWidget {
  const MavlinkStatusBadge({
    super.key,
    required this.connected,
    this.protocolVersion = '2.0',
    this.compact = false,
  });

  final bool connected;
  final String protocolVersion;
  final bool compact;

  @override
  Widget build(BuildContext context) {
    final color = connected ? TacticalColors.success : TacticalColors.textSecondary;
    final label = connected ? 'MAVLink $protocolVersion Connected' : 'MAVLink Offline';

    return Container(
      padding: EdgeInsets.symmetric(horizontal: compact ? 6 : 8, vertical: compact ? 2 : 4),
      decoration: BoxDecoration(
        color: color.withOpacity(0.15),
        borderRadius: BorderRadius.circular(6),
        border: Border.all(color: color.withOpacity(0.65)),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Icon(
            connected ? Icons.link : Icons.link_off,
            size: compact ? 12 : 14,
            color: color,
          ),
          if (!compact) ...[
            const SizedBox(width: 4),
            Text(
              label,
              style: TextStyle(
                color: color,
                fontSize: 10,
                fontWeight: FontWeight.w800,
                letterSpacing: 0.4,
              ),
            ),
          ] else ...[
            const SizedBox(width: 4),
            Text(
              connected ? 'MAVLink 2.0' : 'MAVLink',
              style: TextStyle(color: color, fontSize: 9, fontWeight: FontWeight.w700),
            ),
          ],
        ],
      ),
    );
  }
}
