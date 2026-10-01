import 'dart:async';

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../../core/theme/tactical_theme.dart';
import '../../../core/widgets/tactical_shell.dart';
import '../../../routing/navigation_config.dart';
import '../../alerts/providers/alert_provider.dart';
import '../../alerts/widgets/active_alerts_banner.dart';
import '../../devices/screens/device_list_screen.dart';
import '../../map/screens/tactical_map_screen.dart';
import '../../onboarding/providers/domain_context_provider.dart';
import '../../onboarding/widgets/domain_context_banner.dart';
import '../providers/auth_provider.dart';

class HomeScreen extends ConsumerStatefulWidget {
  const HomeScreen({super.key, this.initialTab = 0});

  /// 0 = Devices, 1 = Map View
  final int initialTab;

  @override
  ConsumerState<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends ConsumerState<HomeScreen> {
  late TacticalNavSection _section;
  Timer? _alertPollTimer;

  @override
  void initState() {
    super.initState();
    final profile = ref.read(domainNavigationProfileProvider);
    _section = widget.initialTab == 1
        ? TacticalNavSection.mapView
        : (profile?.primarySection ?? _sectionFromTab(widget.initialTab));
    Future.microtask(() => ref.read(alertProvider.notifier).loadSummary());
    _alertPollTimer = Timer.periodic(const Duration(seconds: 30), (_) {
      ref.read(alertProvider.notifier).loadSummary();
    });
  }

  TacticalNavSection _sectionFromTab(int tab) {
    switch (tab) {
      case 1:
        return TacticalNavSection.mapView;
      default:
        return TacticalNavSection.devices;
    }
  }

  @override
  void dispose() {
    _alertPollTimer?.cancel();
    super.dispose();
  }

  Widget _buildSectionBody() {
    switch (_section) {
      case TacticalNavSection.devices:
        return const DeviceListScreen();
      case TacticalNavSection.mapView:
        return const TacticalMapScreen();
      case TacticalNavSection.alerts:
        return const SizedBox.shrink();
    }
  }

  @override
  Widget build(BuildContext context) {
    final auth = ref.watch(authProvider);
    final user = auth.user!;
    final navProfile = ref.watch(domainNavigationProfileProvider);
    final tabs = navProfile?.tabs;

    final isMapView = _section == TacticalNavSection.mapView;
    final domainSubtitle = navProfile?.shellSubtitle;

    return TacticalShell(
      section: _section,
      navTabs: tabs,
      navigationProfile: navProfile,
      onSectionChanged: (s) {
        if (s == TacticalNavSection.alerts) {
          context.go(AppRoutes.alerts);
          return;
        }
        setState(() => _section = s);
      },
      onOpenStudio: () => context.go(AppRoutes.studio),
      showContentHeader: !isMapView,
      subtitle: isMapView
          ? domainSubtitle
          : '${domainSubtitle ?? 'Next-IOT'} · ${user.email} · ${user.role}',
      actions: isMapView
          ? null
          : [
              IconButton(
                tooltip: 'Logout',
                icon: const Icon(Icons.logout,
                    color: TacticalColors.textSecondary),
                onPressed: () => ref.read(authProvider.notifier).logout(),
              ),
            ],
      body: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          if (navProfile != null) DomainContextBanner(profile: navProfile),
          const ActiveAlertsBanner(),
          Expanded(
            child: Padding(
              padding: const EdgeInsets.fromLTRB(24, 16, 24, 24),
              child: _buildSectionBody(),
            ),
          ),
        ],
      ),
    );
  }
}
