import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../core/theme/tactical_theme.dart';
import '../../../core/widgets/glowing_led_badge.dart';
import '../providers/system_health_provider.dart';

/// Top-bar readiness chips for DB, cache, and message broker.
class SystemHealthIndicator extends ConsumerWidget {
  const SystemHealthIndicator({super.key, this.compact = false});

  final bool compact;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final health = ref.watch(systemHealthProvider);

    return health.when(
      loading: () => const GlowingLedBadge(
        label: 'SYS …',
        color: TacticalColors.textSecondary,
        pulse: false,
      ),
      error: (_, __) => const GlowingLedBadge(
        label: 'SYS DOWN',
        color: TacticalColors.critical,
        pulse: true,
      ),
      data: (snap) {
        if (compact) {
          return GlowingLedBadge(
            label: snap.isReady ? 'SYS OK' : 'SYS WARN',
            color: snap.isReady ? TacticalColors.success : TacticalColors.warning,
            pulse: snap.isReady,
          );
        }
        return Row(
          mainAxisSize: MainAxisSize.min,
          children: [
            _Chip(
              label: 'DB',
              ok: snap.componentOk(snap.database),
            ),
            const SizedBox(width: 8),
            _Chip(
              label: 'CACHE',
              ok: snap.componentOk(snap.redisCache),
            ),
            const SizedBox(width: 8),
            _Chip(
              label: 'BROKER',
              ok: snap.componentOk(snap.mqttBroker),
            ),
          ],
        );
      },
    );
  }
}

class _Chip extends StatelessWidget {
  const _Chip({required this.label, required this.ok});

  final String label;
  final bool ok;

  @override
  Widget build(BuildContext context) {
    final color = ok ? TacticalColors.success : TacticalColors.critical;
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
      decoration: BoxDecoration(
        color: color.withOpacity(0.12),
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: color.withOpacity(0.45)),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Icon(Icons.circle, size: 8, color: color),
          const SizedBox(width: 4),
          Text(
            label,
            style: TextStyle(
              color: color,
              fontSize: 10,
              fontWeight: FontWeight.w700,
              letterSpacing: 0.6,
            ),
          ),
        ],
      ),
    );
  }
}
