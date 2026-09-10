import 'dart:async';

import 'package:dio/dio.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../core/theme/tactical_theme.dart';
import '../../../core/widgets/pill_tab_bar.dart';
import '../../../core/widgets/tactical_card.dart';
import '../../rules/models/rule_models.dart';
import '../../rules/providers/rule_provider.dart';
import '../data/notification_repository.dart';
import '../models/alert_models.dart';
import '../providers/alert_provider.dart';
import '../widgets/create_rule_dialog.dart';
import '../widgets/severity_badge.dart';

final notificationRepositoryProvider = Provider<NotificationRepository>((ref) => NotificationRepository());

class AlertsScreen extends ConsumerStatefulWidget {
  const AlertsScreen({super.key});

  @override
  ConsumerState<AlertsScreen> createState() => _AlertsScreenState();
}

class _AlertsScreenState extends ConsumerState<AlertsScreen> {
  Timer? _refreshTimer;
  bool _isTestingTelegram = false;
  String? _telegramTestMessage;

  @override
  void initState() {
    super.initState();
    Future.microtask(_loadAll);
    _refreshTimer = Timer.periodic(const Duration(seconds: 20), (_) => _loadAll());
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
    ]);
  }

  Future<void> _sendTestTelegram() async {
    setState(() {
      _isTestingTelegram = true;
      _telegramTestMessage = null;
    });
    try {
      final result = await ref.read(notificationRepositoryProvider).sendTest(
            channels: const ['telegram'],
          );
      final success = result.telegramSuccess;
      setState(() {
        _telegramTestMessage = success
            ? 'Telegram test alert sent successfully.'
            : (result.telegramError ?? 'Telegram dispatch failed.');
      });
    } catch (e) {
      setState(() {
        _telegramTestMessage = _mapTelegramError(e);
      });
    } finally {
      if (mounted) setState(() => _isTestingTelegram = false);
    }
  }

  String _mapTelegramError(Object e) {
    if (e is DioException) {
      if (e.response?.statusCode == 403) return 'Insufficient permissions (tenant_admin required).';
      if (e.response?.statusCode == 401) return 'Session expired. Please log in again.';
    }
    return 'Failed to send test alert. Check backend Telegram config.';
  }

  @override
  Widget build(BuildContext context) {
    final alertState = ref.watch(alertProvider);
    final ruleState = ref.watch(ruleProvider);

    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        Wrap(
          spacing: 10,
          runSpacing: 10,
          crossAxisAlignment: WrapCrossAlignment.center,
          children: [
            Text('ALERTS & RULES', style: Theme.of(context).textTheme.titleLarge),
            OutlinedButton.icon(
              onPressed: _isTestingTelegram ? null : _sendTestTelegram,
              icon: _isTestingTelegram
                  ? const SizedBox(
                      width: 16,
                      height: 16,
                      child: CircularProgressIndicator(strokeWidth: 2),
                    )
                  : const Icon(Icons.send_outlined, size: 18),
              label: const Text('Send Test Telegram Alert'),
            ),
            FilledButton.icon(
              onPressed: ruleState.isSaving ? null : () => showCreateRuleDialog(context, ref),
              icon: const Icon(Icons.add_alert),
              label: const Text('Create New Rule'),
            ),
          ],
        ),
        if (_telegramTestMessage != null) ...[
          const SizedBox(height: 10),
          _FeedbackBanner(message: _telegramTestMessage!),
        ],
        const SizedBox(height: 16),
        PillTabBar<bool>(
          tabs: const [
            PillTab(value: true, label: 'Active Alerts', icon: Icons.warning_amber),
            PillTab(value: false, label: 'History', icon: Icons.history),
          ],
          selected: alertState.showActiveOnly,
          onSelected: ref.read(alertProvider.notifier).setShowActiveOnly,
        ),
        const SizedBox(height: 16),
        Expanded(
          child: RefreshIndicator(
            onRefresh: _loadAll,
            child: ListView(
              children: [
                if (alertState.isLoading && alertState.displayedAlerts.isEmpty)
                  const Center(child: Padding(padding: EdgeInsets.all(32), child: CircularProgressIndicator()))
                else if (alertState.error != null && alertState.displayedAlerts.isEmpty)
                  _ErrorText(message: alertState.error!)
                else if (alertState.displayedAlerts.isEmpty)
                  Padding(
                    padding: const EdgeInsets.all(16),
                    child: Text(
                      alertState.showActiveOnly ? 'No active alerts.' : 'No alert history.',
                    ),
                  )
                else
                  ...alertState.displayedAlerts.map((a) => _AlertTile(alert: a)),
                const SizedBox(height: 24),
                Text('Configured Rules', style: Theme.of(context).textTheme.titleMedium),
                const SizedBox(height: 8),
                if (ruleState.isLoading && ruleState.rules.isEmpty)
                  const Center(child: CircularProgressIndicator())
                else if (ruleState.rules.isEmpty)
                  const Padding(
                    padding: EdgeInsets.all(16),
                    child: Text('No rules configured yet.'),
                  )
                else
                  ...ruleState.rules.map((rule) => _RuleTile(rule: rule)),
              ],
            ),
          ),
        ),
      ],
    );
  }
}

class _FeedbackBanner extends StatelessWidget {
  const _FeedbackBanner({required this.message});

  final String message;

  @override
  Widget build(BuildContext context) {
    final isSuccess = message.toLowerCase().contains('success');
    final color = isSuccess ? TacticalColors.success : TacticalColors.warning;

    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 10),
      decoration: BoxDecoration(
        color: color.withOpacity(0.12),
        borderRadius: BorderRadius.circular(8),
        border: Border.all(color: color.withOpacity(0.4)),
      ),
      child: Row(
        children: [
          Icon(isSuccess ? Icons.check_circle_outline : Icons.info_outline, color: color, size: 18),
          const SizedBox(width: 10),
          Expanded(child: Text(message, style: TextStyle(color: color, fontSize: 13))),
        ],
      ),
    );
  }
}

class _AlertTile extends StatelessWidget {
  const _AlertTile({required this.alert});

  final DeviceAlert alert;

  Color get _accent {
    switch (alert.severity) {
      case AlertSeverity.critical:
        return TacticalColors.critical;
      case AlertSeverity.warning:
        return TacticalColors.warning;
      case AlertSeverity.info:
        return TacticalColors.info;
    }
  }

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 10),
      child: TacticalCard(
        accentColor: _accent,
        child: Row(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            SeverityBadge(severity: alert.severity),
            const SizedBox(width: 14),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    alert.metric ?? alert.event,
                    style: Theme.of(context).textTheme.titleMedium,
                  ),
                  const SizedBox(height: 4),
                  Text(alert.summary, style: Theme.of(context).textTheme.bodySmall),
                  const SizedBox(height: 4),
                  Text(
                    'Device: ${_shortId(alert.deviceId)} · Channel: ${alert.notificationChannel ?? alert.actionType ?? '—'}',
                    style: Theme.of(context).textTheme.bodySmall,
                  ),
                ],
              ),
            ),
            Icon(
              alert.isActive ? Icons.circle : Icons.check_circle_outline,
              color: alert.isActive ? TacticalColors.critical : TacticalColors.textSecondary,
              size: alert.isActive ? 12 : 18,
            ),
          ],
        ),
      ),
    );
  }
}

class _RuleTile extends ConsumerWidget {
  const _RuleTile({required this.rule});

  final AlertRule rule;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 10),
      child: TacticalCard(
        accentColor: TacticalColors.borderNeon,
        child: Row(
          children: [
            Icon(Icons.rule_folder_outlined, color: TacticalColors.borderNeon.withOpacity(0.8)),
            const SizedBox(width: 14),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(rule.name, style: Theme.of(context).textTheme.titleMedium),
                  const SizedBox(height: 4),
                  Text(
                    '${rule.metric} ${rule.operator} ${rule.threshold} · ${rule.channel.label}',
                    style: Theme.of(context).textTheme.bodySmall,
                  ),
                ],
              ),
            ),
            IconButton(
              tooltip: 'Delete rule',
              icon: Icon(Icons.delete_outline, color: TacticalColors.critical.withOpacity(0.85)),
              onPressed: () => ref.read(ruleProvider.notifier).deleteRule(rule.id),
            ),
          ],
        ),
      ),
    );
  }
}

String _shortId(String id) {
  if (id.length <= 8) return id;
  return '${id.substring(0, 8)}…';
}

class _ErrorText extends StatelessWidget {
  const _ErrorText({required this.message});

  final String message;

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.all(16),
      child: Text(message, style: const TextStyle(color: TacticalColors.critical)),
    );
  }
}
