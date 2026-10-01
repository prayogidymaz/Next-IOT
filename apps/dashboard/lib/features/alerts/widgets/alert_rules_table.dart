import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../core/rbac/app_permissions.dart';
import '../../../core/theme/tactical_theme.dart';
import '../../../core/widgets/permission_guard.dart';
import '../../../core/widgets/tactical_card.dart';
import '../../devices/models/device_models.dart';
import '../../devices/providers/device_provider.dart';
import '../../rules/models/rule_models.dart';
import '../../rules/providers/rule_provider.dart';
import 'severity_badge.dart';

class AlertRulesTable extends ConsumerWidget {
  const AlertRulesTable({super.key, this.expanded = false});

  final bool expanded;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final ruleState = ref.watch(ruleProvider);
    final devices = ref.watch(deviceProvider).devices;
    final deviceById = {for (final d in devices) d.id: d};

    return TacticalCard(
      accentColor: BentoTokens.accentSoftBlue,
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          Text('Alert Rules',
              style: Theme.of(context).textTheme.titleMedium),
          const SizedBox(height: 12),
          if (expanded)
            Expanded(
              child: _RulesBody(
                ruleState: ruleState,
                deviceById: deviceById,
              ),
            )
          else
            SingleChildScrollView(
              child: _RulesBody(
                ruleState: ruleState,
                deviceById: deviceById,
              ),
            ),
        ],
      ),
    );
  }
}

class _RulesBody extends ConsumerWidget {
  const _RulesBody({
    required this.ruleState,
    required this.deviceById,
  });

  final RuleListState ruleState;
  final Map<String, Device> deviceById;

  String _deviceLabel(Device? device, String deviceId) {
    if (device == null) return _shortId(deviceId);
    return '${device.name} · ${device.deviceTypeLabel}';
  }

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    if (ruleState.isLoading && ruleState.rules.isEmpty) {
      return const Center(
        child: Padding(
          padding: EdgeInsets.all(24),
          child: CircularProgressIndicator(),
        ),
      );
    }
    if (ruleState.rules.isEmpty) {
      return Padding(
        padding: const EdgeInsets.symmetric(vertical: 20),
        child: Text(
          'No alert rules configured. Create one to start monitoring.',
          style: Theme.of(context)
              .textTheme
              .bodySmall
              ?.copyWith(color: TacticalColors.textSecondary),
        ),
      );
    }
    return LayoutBuilder(
      builder: (context, constraints) {
        final table = DataTable(
          headingRowColor: WidgetStateProperty.all(
            TacticalColors.background.withOpacity(0.6),
          ),
          columns: const [
            DataColumn(label: Text('Rule Name')),
            DataColumn(label: Text('Device / Category')),
            DataColumn(label: Text('Threshold Condition')),
            DataColumn(label: Text('Severity')),
            DataColumn(label: Text('Status')),
            DataColumn(label: Text('Actions')),
          ],
          rows: ruleState.rules
              .map(
                (rule) => DataRow(
                  cells: [
                    DataCell(Text(rule.displayName)),
                    DataCell(Text(_deviceLabel(
                      deviceById[rule.deviceId],
                      rule.deviceId,
                    ))),
                    DataCell(Text(rule.thresholdLabel)),
                    DataCell(SeverityBadge(
                        severity: rule.severity.toAlertSeverity)),
                    DataCell(_StatusChip(isActive: rule.isActive)),
                    DataCell(_RuleActions(rule: rule)),
                  ],
                ),
              )
              .toList(),
        );

        if (constraints.maxWidth < 720) {
          return ListView(
            shrinkWrap: true,
            physics: const NeverScrollableScrollPhysics(),
            children: ruleState.rules
                .map(
                  (rule) => _RuleCard(
                    rule: rule,
                    deviceLabel: _deviceLabel(
                      deviceById[rule.deviceId],
                      rule.deviceId,
                    ),
                  ),
                )
                .toList(),
          );
        }

        return SingleChildScrollView(
          scrollDirection: Axis.horizontal,
          child: ConstrainedBox(
            constraints: BoxConstraints(minWidth: constraints.maxWidth),
            child: table,
          ),
        );
      },
    );
  }
}


class _RuleCard extends ConsumerWidget {
  const _RuleCard({required this.rule, required this.deviceLabel});

  final AlertRule rule;
  final String deviceLabel;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    return Container(
      margin: const EdgeInsets.only(bottom: 10),
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        border: Border.all(color: TacticalColors.border),
        borderRadius: BorderRadius.circular(8),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Expanded(
                child: Text(rule.displayName,
                    style: Theme.of(context).textTheme.titleSmall),
              ),
              SeverityBadge(severity: rule.severity.toAlertSeverity),
            ],
          ),
          const SizedBox(height: 6),
          Text(deviceLabel, style: Theme.of(context).textTheme.bodySmall),
          Text(rule.thresholdLabel,
              style: Theme.of(context).textTheme.bodySmall),
          const SizedBox(height: 8),
          Row(
            children: [
              _StatusChip(isActive: rule.isActive),
              const Spacer(),
              _RuleActions(rule: rule),
            ],
          ),
        ],
      ),
    );
  }
}

class _StatusChip extends StatelessWidget {
  const _StatusChip({required this.isActive});

  final bool isActive;

  @override
  Widget build(BuildContext context) {
    final color = isActive ? TacticalColors.success : TacticalColors.textSecondary;
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
      decoration: BoxDecoration(
        color: color.withOpacity(0.12),
        borderRadius: BorderRadius.circular(999),
        border: Border.all(color: color.withOpacity(0.45)),
      ),
      child: Text(
        isActive ? 'Active' : 'Disabled',
        style: Theme.of(context).textTheme.labelSmall?.copyWith(color: color),
      ),
    );
  }
}

class _RuleActions extends ConsumerWidget {
  const _RuleActions({required this.rule});

  final AlertRule rule;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final isSaving = ref.watch(ruleProvider.select((s) => s.isSaving));
    return Row(
      mainAxisSize: MainAxisSize.min,
      children: [
        PermissionGuard(
          permission: AppPermissions.alertsManage,
          child: IconButton(
            tooltip: rule.isActive ? 'Disable rule' : 'Enable rule',
            icon: Icon(
              rule.isActive ? Icons.toggle_on : Icons.toggle_off_outlined,
              color: rule.isActive ? TacticalColors.success : TacticalColors.textSecondary,
            ),
            onPressed: isSaving
                ? null
                : () => ref.read(ruleProvider.notifier).toggleRuleActive(rule),
          ),
        ),
        PermissionGuard(
          permission: AppPermissions.alertsManage,
          child: IconButton(
            tooltip: 'Delete rule',
            icon: Icon(Icons.delete_outline,
                color: TacticalColors.critical.withOpacity(0.85)),
            onPressed: isSaving
                ? null
                : () => ref.read(ruleProvider.notifier).deleteRule(rule.id),
          ),
        ),
      ],
    );
  }
}

String _shortId(String id) {
  if (id.length <= 8) return id;
  return '${id.substring(0, 8)}…';
}
