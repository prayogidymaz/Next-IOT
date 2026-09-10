import 'dart:async';

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../features/alerts/providers/alert_provider.dart';
import '../theme/tactical_theme.dart';
import 'glowing_led_badge.dart';
import 'hardware_gateway_indicator.dart';

class TacticalStatusBar extends ConsumerStatefulWidget {
  const TacticalStatusBar({super.key});

  @override
  ConsumerState<TacticalStatusBar> createState() => _TacticalStatusBarState();
}

class _TacticalStatusBarState extends ConsumerState<TacticalStatusBar> {
  Timer? _clockTimer;
  DateTime _utcNow = DateTime.now().toUtc();

  @override
  void initState() {
    super.initState();
    _clockTimer = Timer.periodic(const Duration(seconds: 1), (_) {
      if (mounted) setState(() => _utcNow = DateTime.now().toUtc());
    });
  }

  @override
  void dispose() {
    _clockTimer?.cancel();
    super.dispose();
  }

  String _formatUtc(DateTime dt) {
    final h = dt.hour.toString().padLeft(2, '0');
    final m = dt.minute.toString().padLeft(2, '0');
    final s = dt.second.toString().padLeft(2, '0');
    return '$h:$m:$s UTC';
  }

  @override
  Widget build(BuildContext context) {
    final alertState = ref.watch(alertProvider);
    final activeCount = alertState.activeCount;
    final width = MediaQuery.sizeOf(context).width;
    final compact = width < 1024;

    return Container(
      constraints: BoxConstraints(minHeight: compact ? 56 : 48),
      padding: EdgeInsets.symmetric(horizontal: compact ? 12 : 20, vertical: compact ? 6 : 0),
      decoration: const BoxDecoration(
        color: TacticalColors.surface,
        border: Border(bottom: BorderSide(color: TacticalColors.border)),
      ),
      child: compact
          ? Column(
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                Row(
                  children: [
                    Icon(Icons.shield_outlined, size: 16, color: TacticalColors.borderNeon.withOpacity(0.9)),
                    const SizedBox(width: 6),
                    Expanded(
                      child: Text(
                        'TACTICAL CONTROL',
                        style: Theme.of(context).textTheme.labelLarge?.copyWith(
                              color: TacticalColors.borderNeon,
                              fontSize: 11,
                            ),
                      ),
                    ),
                    _StatusItem(icon: Icons.schedule, label: _formatUtc(_utcNow)),
                  ],
                ),
                const SizedBox(height: 6),
                Row(
                  children: [
                    const Expanded(child: HardwareGatewayIndicator(compact: true)),
                    const SizedBox(width: 8),
                    _AlertCountBadge(count: activeCount),
                  ],
                ),
              ],
            )
          : Row(
              children: [
                Icon(Icons.shield_outlined, size: 18, color: TacticalColors.borderNeon.withOpacity(0.9)),
                const SizedBox(width: 8),
                Text(
                  'TACTICAL CONTROL CENTER',
                  style: Theme.of(context).textTheme.labelLarge?.copyWith(
                        color: TacticalColors.borderNeon,
                        fontSize: 12,
                      ),
                ),
                const Spacer(),
                const HardwareGatewayIndicator(),
                const SizedBox(width: 16),
                _StatusItem(icon: Icons.schedule, label: _formatUtc(_utcNow)),
                const SizedBox(width: 20),
                _AlertCountBadge(count: activeCount),
                const SizedBox(width: 20),
                const GlowingLedBadge(
                  label: 'SYSTEM OK',
                  color: TacticalColors.success,
                  pulse: true,
                ),
              ],
            ),
    );
  }
}

class _StatusItem extends StatelessWidget {
  const _StatusItem({required this.icon, required this.label});

  final IconData icon;
  final String label;

  @override
  Widget build(BuildContext context) {
    return Row(
      mainAxisSize: MainAxisSize.min,
      children: [
        Icon(icon, size: 14, color: TacticalColors.textSecondary),
        const SizedBox(width: 6),
        Text(label, style: Theme.of(context).textTheme.bodySmall),
      ],
    );
  }
}

class _AlertCountBadge extends StatelessWidget {
  const _AlertCountBadge({required this.count});

  final int count;

  @override
  Widget build(BuildContext context) {
    final color = count > 0 ? TacticalColors.critical : TacticalColors.textSecondary;

    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
      decoration: BoxDecoration(
        color: count > 0 ? TacticalColors.critical.withOpacity(0.15) : TacticalColors.background,
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: color.withOpacity(0.5)),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Icon(Icons.notifications_active_outlined, size: 14, color: color),
          const SizedBox(width: 6),
          Text(
            '$count ACTIVE',
            style: TextStyle(
              color: color,
              fontSize: 11,
              fontWeight: FontWeight.w700,
              letterSpacing: 0.5,
            ),
          ),
        ],
      ),
    );
  }
}
