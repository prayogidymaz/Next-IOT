import 'dart:async';

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../core/rbac/app_permissions.dart';
import '../../../core/theme/tactical_theme.dart';
import '../../../core/widgets/permission_guard.dart';
import '../../devices/providers/device_provider.dart';
import '../../rules/providers/rule_provider.dart';
import '../providers/alert_provider.dart';
import '../widgets/alert_rules_table.dart';
import '../widgets/create_rule_dialog.dart';
import '../widgets/live_activity_feed.dart';
import '../widgets/notification_channels_panel.dart';

class AlertsScreen extends ConsumerStatefulWidget {
  const AlertsScreen({super.key});

  @override
  ConsumerState<AlertsScreen> createState() => _AlertsScreenState();
}

class _AlertsScreenState extends ConsumerState<AlertsScreen> {
  Timer? _refreshTimer;

  @override
  void initState() {
    super.initState();
    Future.microtask(_loadAll);
    _refreshTimer =
        Timer.periodic(const Duration(seconds: 20), (_) => _loadAll());
  }

  @override
  void dispose() {
    _refreshTimer?.cancel();
    super.dispose();
  }

  Future<void> _loadAll() async {
    await Future.wait([
      ref.read(alertProvider.notifier).loadAlerts(),
      ref.read(ruleProvider.notifier).loadRules(),
      ref.read(deviceProvider.notifier).loadDevices(),
    ]);
  }

  Widget _header(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        Wrap(
          spacing: 10,
          runSpacing: 10,
          crossAxisAlignment: WrapCrossAlignment.center,
          children: [
            Text(
              'ALERT & NOTIFICATION ENGINE',
              style: Theme.of(context).textTheme.titleLarge,
            ),
            PermissionGuard(
              permission: AppPermissions.alertsManage,
              child: FilledButton.icon(
                onPressed: ref.watch(ruleProvider.select((s) => s.isSaving))
                    ? null
                    : () => showCreateRuleDialog(context, ref),
                icon: const Icon(Icons.add_alert),
                label: const Text('Create New Alert Rule'),
              ),
            ),
          ],
        ),
        const SizedBox(height: 8),
        Text(
          'Manage rule triggers, notification channels, and live alert activity.',
          style: Theme.of(context).textTheme.bodySmall?.copyWith(
                color: TacticalColors.textSecondary,
              ),
        ),
      ],
    );
  }

  Widget _wideLayout() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        _header(context),
        const SizedBox(height: 20),
        Expanded(
          child: Row(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: const [
              Expanded(
                flex: 3,
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.stretch,
                  children: [
                    Flexible(
                      child: SingleChildScrollView(
                        child: NotificationChannelsPanel(),
                      ),
                    ),
                    SizedBox(height: 16),
                    Expanded(child: AlertRulesTable(expanded: true)),
                  ],
                ),
              ),
              SizedBox(width: 16),
              Expanded(flex: 2, child: LiveActivityFeed()),
            ],
          ),
        ),
      ],
    );
  }

  Widget _narrowLayout() {
    return ListView(
      padding: const EdgeInsets.only(bottom: 80),
      children: [
        _header(context),
        const SizedBox(height: 20),
        const NotificationChannelsPanel(),
        const SizedBox(height: 16),
        const AlertRulesTable(),
        const SizedBox(height: 16),
        const SizedBox(height: 420, child: LiveActivityFeed()),
      ],
    );
  }

  @override
  Widget build(BuildContext context) {
    final useSideBySide = MediaQuery.sizeOf(context).width >= 1100;

    return RefreshIndicator(
      onRefresh: _loadAll,
      child: useSideBySide
          ? _wideLayout()
          : _narrowLayout(),
    );
  }
}
