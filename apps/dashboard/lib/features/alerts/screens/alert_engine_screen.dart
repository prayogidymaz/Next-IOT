import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../../core/theme/tactical_theme.dart';
import '../../../core/widgets/tactical_shell.dart';
import '../../../routing/navigation_config.dart';
import '../../auth/providers/auth_provider.dart';
import '../widgets/active_alerts_banner.dart';
import 'alerts_screen.dart';

/// Full-page Alert & Notification Engine at `/alerts`.
class AlertEngineScreen extends ConsumerWidget {
  const AlertEngineScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final auth = ref.watch(authProvider);
    final user = auth.user!;

    return TacticalShell(
      section: TacticalNavSection.alerts,
      onSectionChanged: (section) {
        switch (section) {
          case TacticalNavSection.devices:
            context.go(AppRoutes.dashboard);
          case TacticalNavSection.mapView:
            context.go('${AppRoutes.dashboard}?tab=map');
          case TacticalNavSection.alerts:
            break;
        }
      },
      onOpenStudio: () => context.go(AppRoutes.studio),
      subtitle:
          '${user.email} · ${user.role} · tenant ${_shortTenant(user.tenantId)}',
      actions: [
        IconButton(
          tooltip: 'Logout',
          icon: const Icon(Icons.logout, color: TacticalColors.textSecondary),
          onPressed: () => ref.read(authProvider.notifier).logout(),
        ),
      ],
      body: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          const ActiveAlertsBanner(),
          Expanded(
            child: Padding(
              padding: const EdgeInsets.fromLTRB(24, 16, 24, 24),
              child: AlertsScreen(),
            ),
          ),
        ],
      ),
    );
  }
}

String _shortTenant(String id) {
  if (id.length <= 8) return id;
  return '${id.substring(0, 8)}…';
}
