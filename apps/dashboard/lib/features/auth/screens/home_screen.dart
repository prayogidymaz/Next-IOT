import 'dart:async';

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../core/theme/tactical_theme.dart';
import '../../../core/widgets/tactical_shell.dart';
import '../../alerts/providers/alert_provider.dart';
import '../../alerts/screens/alerts_screen.dart';
import '../../alerts/widgets/active_alerts_banner.dart';
import '../../devices/screens/device_list_screen.dart';
import '../../map/screens/tactical_map_screen.dart';
import '../providers/auth_provider.dart';

class HomeScreen extends ConsumerStatefulWidget {
  const HomeScreen({super.key, this.initialTab = 0});

  /// 0 = Devices, 1 = Map View, 2 = Alerts
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
    _section = _sectionFromTab(widget.initialTab);
    Future.microtask(() => ref.read(alertProvider.notifier).loadSummary());
    _alertPollTimer = Timer.periodic(const Duration(seconds: 30), (_) {
      ref.read(alertProvider.notifier).loadSummary();
    });
  }

  TacticalNavSection _sectionFromTab(int tab) {
    switch (tab) {
      case 1:
        return TacticalNavSection.mapView;
      case 2:
        return TacticalNavSection.alerts;
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
        return const AlertsScreen();
    }
  }

  @override
  Widget build(BuildContext context) {
    final auth = ref.watch(authProvider);
    final user = auth.user!;

    return TacticalShell(
      section: _section,
      onSectionChanged: (s) => setState(() => _section = s),
      subtitle: '${user.email} · ${user.role} · tenant ${_shortTenant(user.tenantId)}',
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
              child: _buildSectionBody(),
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
