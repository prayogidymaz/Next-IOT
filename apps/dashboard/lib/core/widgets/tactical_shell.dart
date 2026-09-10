import 'package:flutter/material.dart';

import '../theme/tactical_theme.dart';
import 'tactical_status_bar.dart';

enum TacticalNavSection { devices, mapView, alerts }

class TacticalShell extends StatelessWidget {
  const TacticalShell({
    super.key,
    required this.section,
    required this.onSectionChanged,
    required this.body,
    this.actions,
    this.subtitle,
  });

  final TacticalNavSection section;
  final ValueChanged<TacticalNavSection> onSectionChanged;
  final Widget body;
  final List<Widget>? actions;
  final String? subtitle;

  int get _selectedIndex {
    switch (section) {
      case TacticalNavSection.devices:
        return 0;
      case TacticalNavSection.mapView:
        return 1;
      case TacticalNavSection.alerts:
        return 2;
    }
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
                      _ContentHeader(subtitle: subtitle, actions: actions, compact: true),
                      Expanded(child: body),
                    ],
                  )
                : Row(
                    crossAxisAlignment: CrossAxisAlignment.stretch,
                    children: [
                      _TacticalNavRail(
                        selectedIndex: _selectedIndex,
                        onSectionChanged: onSectionChanged,
                      ),
                      Expanded(
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.stretch,
                          children: [
                            _ContentHeader(subtitle: subtitle, actions: actions),
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
                final next = switch (i) {
                  0 => TacticalNavSection.devices,
                  1 => TacticalNavSection.mapView,
                  _ => TacticalNavSection.alerts,
                };
                onSectionChanged(next);
              },
              destinations: const [
                NavigationDestination(icon: Icon(Icons.radar_outlined), selectedIcon: Icon(Icons.radar), label: 'Devices'),
                NavigationDestination(icon: Icon(Icons.map_outlined), selectedIcon: Icon(Icons.map), label: 'Map'),
                NavigationDestination(icon: Icon(Icons.crisis_alert_outlined), selectedIcon: Icon(Icons.crisis_alert), label: 'Alerts'),
              ],
            )
          : null,
    );
  }
}

class _TacticalNavRail extends StatelessWidget {
  const _TacticalNavRail({
    required this.selectedIndex,
    required this.onSectionChanged,
  });

  final int selectedIndex;
  final ValueChanged<TacticalNavSection> onSectionChanged;

  @override
  Widget build(BuildContext context) {
    return Container(
      width: 88,
      decoration: const BoxDecoration(
        color: TacticalColors.surface,
        border: Border(right: BorderSide(color: TacticalColors.border)),
      ),
      child: NavigationRail(
        selectedIndex: selectedIndex,
        extended: false,
        labelType: NavigationRailLabelType.all,
        backgroundColor: Colors.transparent,
        destinations: const [
          NavigationRailDestination(
            icon: Icon(Icons.radar_outlined),
            selectedIcon: Icon(Icons.radar),
            label: Text('Devices'),
          ),
          NavigationRailDestination(
            icon: Icon(Icons.map_outlined),
            selectedIcon: Icon(Icons.map),
            label: Text('Map View'),
          ),
          NavigationRailDestination(
            icon: Icon(Icons.crisis_alert_outlined),
            selectedIcon: Icon(Icons.crisis_alert),
            label: Text('Alerts'),
          ),
        ],
        onDestinationSelected: (i) {
          final section = switch (i) {
            0 => TacticalNavSection.devices,
            1 => TacticalNavSection.mapView,
            _ => TacticalNavSection.alerts,
          };
          onSectionChanged(section);
        },
      ),
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
      padding: EdgeInsets.fromLTRB(compact ? 12 : 24, compact ? 10 : 16, compact ? 12 : 24, compact ? 6 : 8),
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
