import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../../core/theme/tactical_theme.dart';
import '../providers/alert_provider.dart';

class ActiveAlertsBanner extends ConsumerWidget {
  const ActiveAlertsBanner({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final alertState = ref.watch(alertProvider);
    if (alertState.activeCount == 0) return const SizedBox.shrink();

    return Container(
      margin: const EdgeInsets.fromLTRB(24, 12, 24, 0),
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
      decoration: BoxDecoration(
        color: TacticalColors.critical.withOpacity(0.12),
        borderRadius: BorderRadius.circular(8),
        border: Border.all(color: TacticalColors.critical.withOpacity(0.45)),
        boxShadow: [
          BoxShadow(color: TacticalColors.critical.withOpacity(0.15), blurRadius: 10),
        ],
      ),
      child: Row(
        children: [
          Icon(Icons.warning_amber_rounded, color: TacticalColors.critical),
          const SizedBox(width: 12),
          Expanded(
            child: Text(
              '${alertState.activeCount} active alert${alertState.activeCount == 1 ? '' : 's'} require attention',
              style: const TextStyle(
                color: TacticalColors.textPrimary,
                fontWeight: FontWeight.w600,
              ),
            ),
          ),
          TextButton(
            onPressed: () => context.go('/home?tab=alerts'),
            child: const Text('VIEW', style: TextStyle(color: TacticalColors.borderNeon)),
          ),
        ],
      ),
    );
  }
}
