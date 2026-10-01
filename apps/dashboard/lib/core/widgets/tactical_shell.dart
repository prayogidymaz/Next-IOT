import 'package:flutter/material.dart';

import '../../features/onboarding/models/domain_navigation_profile.dart';
import '../theme/tactical_theme.dart';
import 'app_sidebar.dart';
import 'tactical_status_bar.dart';

enum TacticalNavSection { devices, mapView, alerts }

class TacticalShell extends StatelessWidget {
  const TacticalShell({
    super.key,
    required this.section,
    required this.onSectionChanged,
    required this.onOpenStudio,
    required this.body,
    this.actions,
    this.subtitle,
    this.showContentHeader = true,
    this.navTabs,
    this.navigationProfile,
  });

  final TacticalNavSection section;
  final ValueChanged<TacticalNavSection> onSectionChanged;
  final VoidCallback onOpenStudio;
  final Widget body;
  final List<Widget>? actions;
  final String? subtitle;
  final bool showContentHeader;
  final List<DomainNavTab>? navTabs;
  final DomainNavigationProfile? navigationProfile;

  List<DomainNavTab> get _tabs =>
      navTabs ??
      const [
        DomainNavTab(
          section: TacticalNavSection.devices,
          label: 'Devices',
          icon: Icons.radar_outlined,
          selectedIcon: Icons.radar,
        ),
        DomainNavTab(
          section: TacticalNavSection.mapView,
          label: 'Map',
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

  int get _selectedIndex {
    final index = _tabs.indexWhere((t) => t.section == section);
    return index >= 0 ? index : 0;
  }

  @override
  Widget build(BuildContext context) {
    final width = MediaQuery.sizeOf(context).width;
    final useBottomNav = width < 900;

    return Scaffold(
      body: Column(
        children: [
          const TacticalStatusBar(),
          Expanded(
            child: useBottomNav
                ? Column(
                    crossAxisAlignment: CrossAxisAlignment.stretch,
                    children: [
                      if (showContentHeader)
                        _ContentHeader(
                          subtitle: subtitle,
                          actions: actions,
                          compact: true,
                        ),
                      Expanded(child: body),
                    ],
                  )
                : Row(
                    crossAxisAlignment: CrossAxisAlignment.stretch,
                    children: [
                      AppSidebar(
                        section: section,
                        onSectionChanged: onSectionChanged,
                        onOpenStudio: onOpenStudio,
                        navigationProfile: navigationProfile,
                        navTabs: _tabs,
                      ),
                      Expanded(
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.stretch,
                          children: [
                            if (showContentHeader)
                              _ContentHeader(
                                subtitle: subtitle,
                                actions: actions,
                              ),
                            Expanded(child: body),
                          ],
                        ),
                      ),
                    ],
                  ),
          ),
        ],
      ),
      bottomNavigationBar: useBottomNav
          ? NavigationBar(
              selectedIndex: _selectedIndex,
              onDestinationSelected: (i) {
                if (i >= 0 && i < _tabs.length) {
                  onSectionChanged(_tabs[i].section);
                }
              },
              destinations: [
                for (final tab in _tabs)
                  NavigationDestination(
                    icon: Icon(tab.icon),
                    selectedIcon: Icon(tab.selectedIcon),
                    label: tab.label,
                  ),
              ],
            )
          : null,
    );
  }
}

class _ContentHeader extends StatelessWidget {
  const _ContentHeader({this.subtitle, this.actions, this.compact = false});

  final String? subtitle;
  final List<Widget>? actions;
  final bool compact;

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: EdgeInsets.fromLTRB(compact ? 12 : 24, compact ? 10 : 16,
          compact ? 12 : 24, compact ? 6 : 8),
      decoration: const BoxDecoration(
        border: Border(bottom: BorderSide(color: TacticalColors.border)),
      ),
      child: Row(
        children: [
          if (subtitle != null)
            Expanded(
              child: Text(
                subtitle!,
                style: Theme.of(context).textTheme.bodySmall,
                overflow: TextOverflow.ellipsis,
              ),
            ),
          if (actions != null) ...actions!,
        ],
      ),
    );
  }
}
