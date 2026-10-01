import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../core/rbac/app_permissions.dart';
import '../../features/auth/providers/auth_provider.dart';
import '../../features/auth/providers/permissions_provider.dart';
import '../../features/onboarding/models/domain_navigation_profile.dart';
import '../../routing/navigation_config.dart';
import '../../routing/shell_navigation.dart';
import '../theme/tactical_theme.dart';
import 'tactical_shell.dart';

/// Left navigation rail for the dashboard shell (monitoring + operations).
class AppSidebar extends ConsumerWidget {
  const AppSidebar({
    super.key,
    required this.section,
    required this.onSectionChanged,
    required this.onOpenStudio,
    this.navigationProfile,
    this.navTabs,
  });

  final TacticalNavSection section;
  final ValueChanged<TacticalNavSection> onSectionChanged;
  final VoidCallback onOpenStudio;
  final DomainNavigationProfile? navigationProfile;
  final List<DomainNavTab>? navTabs;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final path = currentShellPath(context);
    final onAnalytics = path.startsWith(AppRoutes.analytics);
    final onSettings = path.startsWith(AppRoutes.settings);
    final onAudit = path.startsWith(AppRoutes.audit);
    final onCyberdeck = path.startsWith(AppRoutes.cyberdeck);
    final auth = ref.watch(authProvider);
    final canAudit = ref.watch(
      permissionsProvider.select(
        (s) => s.can(AppPermissions.auditRead, fallbackRole: auth.user?.role),
      ),
    );

    final tabs = navTabs ??
        const [
          DomainNavTab(
            section: TacticalNavSection.devices,
            label: 'Devices',
            icon: Icons.radar_outlined,
            selectedIcon: Icons.radar,
          ),
          DomainNavTab(
            section: TacticalNavSection.mapView,
            label: 'Map View',
            icon: Icons.map_outlined,
            selectedIcon: Icons.map,
          ),
          DomainNavTab(
            section: TacticalNavSection.alerts,
            label: 'Alerts',
            icon: Icons.crisis_alert_outlined,
            selectedIcon: Icons.crisis_alert,
          ),
        ];
    final showCyberdeck = navigationProfile?.showCyberdeckShortcut ?? true;
    final showStudio = navigationProfile?.showAutomationStudio ?? true;

    return Container(
      width: 88,
      decoration: const BoxDecoration(
        color: TacticalColors.surface,
        border: Border(right: BorderSide(color: TacticalColors.border)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          const SizedBox(height: 12),
          const _SectionLabel(text: 'MONITORING'),
          for (final tab in tabs)
            _SidebarItem(
              icon: tab.icon,
              selectedIcon: tab.selectedIcon,
              label: tab.label,
              selected: section == tab.section &&
                  !(tab.section == TacticalNavSection.devices && onAnalytics),
              onTap: () => onSectionChanged(tab.section),
            ),
          _SidebarItem(
            key: const Key('sidebar-analytics'),
            icon: Icons.insights_outlined,
            selectedIcon: Icons.insights,
            label: 'Analytics',
            selected: onAnalytics,
            onTap: () => openAnalytics(context),
          ),
          const Padding(
            padding: EdgeInsets.symmetric(horizontal: 12, vertical: 8),
            child: Divider(height: 1, color: TacticalColors.border),
          ),
          const _SectionLabel(text: 'OPERATIONS'),
          if (showStudio)
            _SidebarItem(
              key: const Key('sidebar-automation-studio'),
              icon: Icons.account_tree_outlined,
              selectedIcon: Icons.account_tree,
              label: 'Automation Studio',
              selected: path.startsWith(AppRoutes.studio),
              onTap: onOpenStudio,
            ),
          if (showCyberdeck)
            _SidebarItem(
              key: const Key('sidebar-cyberdeck'),
              icon: Icons.terminal_outlined,
              selectedIcon: Icons.terminal,
              label: 'Cyberdeck',
              selected: onCyberdeck,
              onTap: () => openCyberdeck(context),
            ),
          if (canAudit)
            _SidebarItem(
              key: const Key('sidebar-audit'),
              icon: Icons.fact_check_outlined,
              selectedIcon: Icons.fact_check,
              label: 'Audit Log',
              selected: onAudit,
              onTap: () => openAuditLog(context),
            ),
          const Spacer(),
          _SidebarItem(
            key: const Key('sidebar-settings'),
            icon: Icons.settings_outlined,
            selectedIcon: Icons.settings,
            label: 'Settings',
            selected: onSettings,
            onTap: () => openSettings(context),
          ),
          const SizedBox(height: 8),
        ],
      ),
    );
  }
}

class _SectionLabel extends StatelessWidget {
  const _SectionLabel({required this.text});

  final String text;

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.fromLTRB(8, 4, 8, 6),
      child: Text(
        text,
        textAlign: TextAlign.center,
        style: Theme.of(context).textTheme.labelSmall?.copyWith(
              color: TacticalColors.textSecondary,
              letterSpacing: 0.8,
              fontSize: 9,
            ),
      ),
    );
  }
}

class _SidebarItem extends StatelessWidget {
  const _SidebarItem({
    super.key,
    required this.icon,
    required this.selectedIcon,
    required this.label,
    required this.selected,
    required this.onTap,
  });

  final IconData icon;
  final IconData selectedIcon;
  final String label;
  final bool selected;
  final VoidCallback onTap;

  @override
  Widget build(BuildContext context) {
    final color = selected ? TacticalColors.cyan : TacticalColors.textSecondary;

    return Material(
      color:
          selected ? TacticalColors.cyan.withOpacity(0.08) : Colors.transparent,
      child: InkWell(
        onTap: onTap,
        child: Padding(
          padding: const EdgeInsets.symmetric(vertical: 10, horizontal: 4),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              Icon(selected ? selectedIcon : icon, color: color, size: 22),
              const SizedBox(height: 4),
              Text(
                label,
                textAlign: TextAlign.center,
                maxLines: 2,
                overflow: TextOverflow.ellipsis,
                style: Theme.of(context).textTheme.labelSmall?.copyWith(
                      color: color,
                      fontSize: 10,
                      height: 1.1,
                    ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
