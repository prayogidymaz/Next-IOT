import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../devices/models/device_models.dart';
import '../../devices/providers/device_provider.dart';
import '../../rules/models/rule_models.dart';
import '../../rules/providers/rule_provider.dart';
import '../providers/alert_provider.dart';

Future<void> showCreateRuleDialog(BuildContext context, WidgetRef ref) async {
  await showDialog<void>(
    context: context,
    builder: (context) => const CreateRuleDialog(),
  );
}

class CreateRuleDialog extends ConsumerStatefulWidget {
  const CreateRuleDialog({super.key});

  @override
  ConsumerState<CreateRuleDialog> createState() => _CreateRuleDialogState();
}

class _CreateRuleDialogState extends ConsumerState<CreateRuleDialog> {
  final _formKey = GlobalKey<FormState>();
  final _nameController = TextEditingController();
  final _metricController = TextEditingController(text: 'temperature');
  final _thresholdController = TextEditingController(text: '45');

  String? _deviceId;
  RuleOperator _operator = RuleOperator.gt;
  NotificationChannel _channel = NotificationChannel.telegram;

  @override
  void dispose() {
    _nameController.dispose();
    _metricController.dispose();
    _thresholdController.dispose();
    super.dispose();
  }

  Future<void> _submit() async {
    if (!_formKey.currentState!.validate() || _deviceId == null) return;

    final threshold = double.parse(_thresholdController.text.trim());
    final success = await ref.read(ruleProvider.notifier).createRule(
          CreateRuleRequest(
            deviceId: _deviceId!,
            name: _nameController.text.trim(),
            metric: _metricController.text.trim(),
            operator: _operator.apiValue,
            threshold: threshold,
            actionType: _channel.actionType,
          ),
        );

    if (!mounted) return;
    if (success) {
      await ref.read(alertProvider.notifier).loadAlerts();
      Navigator.of(context).pop();
    }
  }

  @override
  Widget build(BuildContext context) {
    final devices = ref.watch(deviceProvider).devices;
    final isSaving = ref.watch(ruleProvider.select((s) => s.isSaving));
    final error = ref.watch(ruleProvider.select((s) => s.error));

    if (_deviceId == null && devices.isNotEmpty) {
      _deviceId = devices.first.id;
    }

    return AlertDialog(
      title: const Text('Create New Rule'),
      content: SizedBox(
        width: 420,
        child: Form(
          key: _formKey,
          child: SingleChildScrollView(
            child: Column(
              mainAxisSize: MainAxisSize.min,
              children: [
                DropdownButtonFormField<String>(
                  value: _deviceId,
                  decoration: const InputDecoration(
                    labelText: 'Device',
                    border: OutlineInputBorder(),
                  ),
                  items: devices
                      .map(
                        (Device d) => DropdownMenuItem(value: d.id, child: Text(d.name)),
                      )
                      .toList(),
                  onChanged: isSaving ? null : (v) => setState(() => _deviceId = v),
                  validator: (v) => v == null ? 'Select a device' : null,
                ),
                const SizedBox(height: 12),
                TextFormField(
                  controller: _nameController,
                  decoration: const InputDecoration(labelText: 'Rule name', border: OutlineInputBorder()),
                  validator: (v) => v == null || v.trim().isEmpty ? 'Name required' : null,
                ),
                const SizedBox(height: 12),
                TextFormField(
                  controller: _metricController,
                  decoration: const InputDecoration(labelText: 'Metric', border: OutlineInputBorder()),
                  validator: (v) => v == null || v.trim().isEmpty ? 'Metric required' : null,
                ),
                const SizedBox(height: 12),
                DropdownButtonFormField<RuleOperator>(
                  value: _operator,
                  decoration: const InputDecoration(labelText: 'Operator', border: OutlineInputBorder()),
                  items: RuleOperator.values
                      .map((op) => DropdownMenuItem(value: op, child: Text('${op.label} (${op.apiValue})')))
                      .toList(),
                  onChanged: isSaving ? null : (v) => setState(() => _operator = v ?? RuleOperator.gt),
                ),
                const SizedBox(height: 12),
                TextFormField(
                  controller: _thresholdController,
                  decoration: const InputDecoration(labelText: 'Threshold', border: OutlineInputBorder()),
                  keyboardType: const TextInputType.numberWithOptions(decimal: true),
                  validator: (v) {
                    if (v == null || double.tryParse(v.trim()) == null) return 'Valid number required';
                    return null;
                  },
                ),
                const SizedBox(height: 12),
                DropdownButtonFormField<NotificationChannel>(
                  value: _channel,
                  decoration: const InputDecoration(labelText: 'Channel', border: OutlineInputBorder()),
                  items: NotificationChannel.values
                      .map((c) => DropdownMenuItem(value: c, child: Text(c.label)))
                      .toList(),
                  onChanged: isSaving ? null : (v) => setState(() => _channel = v ?? NotificationChannel.telegram),
                ),
                if (error != null) ...[
                  const SizedBox(height: 12),
                  Text(error, style: TextStyle(color: Theme.of(context).colorScheme.error)),
                ],
              ],
            ),
          ),
        ),
      ),
      actions: [
        TextButton(onPressed: isSaving ? null : () => Navigator.pop(context), child: const Text('Cancel')),
        FilledButton(
          onPressed: isSaving ? null : _submit,
          child: isSaving
              ? const SizedBox(width: 18, height: 18, child: CircularProgressIndicator(strokeWidth: 2))
              : const Text('Create Rule'),
        ),
      ],
    );
  }
}
