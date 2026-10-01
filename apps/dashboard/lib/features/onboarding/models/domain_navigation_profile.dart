import 'package:flutter/material.dart';

import '../../../core/widgets/tactical_shell.dart';
import 'operational_domain.dart';

class DomainNavTab {
  const DomainNavTab({
    required this.section,
    required this.label,
    required this.icon,
    required this.selectedIcon,
  });

  final TacticalNavSection section;
  final String label;
  final IconData icon;
  final IconData selectedIcon;
}

class DomainNavigationProfile {
  const DomainNavigationProfile({
    required this.domain,
    required this.tabs,
    required this.shellSubtitle,
    required this.showCyberdeckShortcut,
    required this.showAutomationStudio,
    required this.primarySection,
  });

  final OperationalDomain domain;
  final List<DomainNavTab> tabs;
  final String shellSubtitle;
  final bool showCyberdeckShortcut;
  final bool showAutomationStudio;
  final TacticalNavSection primarySection;

  DomainNavTab tabFor(TacticalNavSection section) {
    return tabs.firstWhere(
      (t) => t.section == section,
      orElse: () => tabs.first,
    );
  }
}

DomainNavigationProfile navigationProfileFor({
  required OperationalDomain domain,
  required EnterpriseSegment segment,
}) {
  final segmentTag = segment.title;
  switch (domain) {
    case OperationalDomain.smartHome:
      return DomainNavigationProfile(
        domain: domain,
        primarySection: TacticalNavSection.devices,
        shellSubtitle: 'Smart Home · $segmentTag',
        showCyberdeckShortcut: false,
        showAutomationStudio: true,
        tabs: const [
          DomainNavTab(
            section: TacticalNavSection.devices,
            label: 'Rooms',
            icon: Icons.home_outlined,
            selectedIcon: Icons.home,
          ),
          DomainNavTab(
            section: TacticalNavSection.mapView,
            label: 'Floor Plan',
            icon: Icons.grid_view_outlined,
            selectedIcon: Icons.grid_view,
          ),
          DomainNavTab(
            section: TacticalNavSection.alerts,
            label: 'Scenes',
            icon: Icons.auto_awesome_outlined,
            selectedIcon: Icons.auto_awesome,
          ),
        ],
      );
    case OperationalDomain.smartFarming:
      return DomainNavigationProfile(
        domain: domain,
        primarySection: TacticalNavSection.mapView,
        shellSubtitle: 'Smart Farming · $segmentTag',
        showCyberdeckShortcut: false,
        showAutomationStudio: true,
        tabs: const [
          DomainNavTab(
            section: TacticalNavSection.devices,
            label: 'Fields',
            icon: Icons.agriculture_outlined,
            selectedIcon: Icons.agriculture,
          ),
          DomainNavTab(
            section: TacticalNavSection.mapView,
            label: 'Plots',
            icon: Icons.landscape_outlined,
            selectedIcon: Icons.landscape,
          ),
          DomainNavTab(
            section: TacticalNavSection.alerts,
            label: 'Crop Alerts',
            icon: Icons.wb_sunny_outlined,
            selectedIcon: Icons.wb_sunny,
          ),
        ],
      );
    case OperationalDomain.cyberdeckTactical:
      return DomainNavigationProfile(
        domain: domain,
        primarySection: TacticalNavSection.mapView,
        shellSubtitle: 'Cyberdeck Tactical · $segmentTag',
        showCyberdeckShortcut: true,
        showAutomationStudio: true,
        tabs: const [
          DomainNavTab(
            section: TacticalNavSection.devices,
            label: 'Nodes',
            icon: Icons.hub_outlined,
            selectedIcon: Icons.hub,
          ),
          DomainNavTab(
            section: TacticalNavSection.mapView,
            label: 'Mesh Map',
            icon: Icons.map_outlined,
            selectedIcon: Icons.map,
          ),
          DomainNavTab(
            section: TacticalNavSection.alerts,
            label: 'Ops Alerts',
            icon: Icons.crisis_alert_outlined,
            selectedIcon: Icons.crisis_alert,
          ),
        ],
      );
    case OperationalDomain.droneLogistics:
      return DomainNavigationProfile(
        domain: domain,
        primarySection: TacticalNavSection.mapView,
        shellSubtitle: 'Drone & Logistics · $segmentTag',
        showCyberdeckShortcut: false,
        showAutomationStudio: true,
        tabs: const [
          DomainNavTab(
            section: TacticalNavSection.devices,
            label: 'Fleet',
            icon: Icons.flight_outlined,
            selectedIcon: Icons.flight,
          ),
          DomainNavTab(
            section: TacticalNavSection.mapView,
            label: 'Airspace',
            icon: Icons.public_outlined,
            selectedIcon: Icons.public,
          ),
          DomainNavTab(
            section: TacticalNavSection.alerts,
            label: 'Mission Alerts',
            icon: Icons.local_shipping_outlined,
            selectedIcon: Icons.local_shipping,
          ),
        ],
      );
    case OperationalDomain.industrialRobotics:
      return DomainNavigationProfile(
        domain: domain,
        primarySection: TacticalNavSection.devices,
        shellSubtitle: 'Industrial Robotics · $segmentTag',
        showCyberdeckShortcut: false,
        showAutomationStudio: true,
        tabs: const [
          DomainNavTab(
            section: TacticalNavSection.devices,
            label: 'Lines',
            icon: Icons.precision_manufacturing_outlined,
            selectedIcon: Icons.precision_manufacturing,
          ),
          DomainNavTab(
            section: TacticalNavSection.mapView,
            label: 'Factory Map',
            icon: Icons.factory_outlined,
            selectedIcon: Icons.factory,
          ),
          DomainNavTab(
            section: TacticalNavSection.alerts,
            label: 'Safety',
            icon: Icons.health_and_safety_outlined,
            selectedIcon: Icons.health_and_safety,
          ),
        ],
      );
  }
}
