import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../core/theme/tactical_theme.dart';
import '../models/mission_models.dart';
import '../providers/mission_provider.dart';

enum FailSafeAction { returnToHome, emergencyLand }

Future<void> showEmergencyFailSafeDialog(BuildContext context, WidgetRef ref) async {
  await showDialog<void>(
    context: context,
    barrierDismissible: false,
    builder: (_) => const EmergencyFailSafeDialog(),
  );
}

class EmergencyFailSafeDialog extends ConsumerStatefulWidget {
  const EmergencyFailSafeDialog({super.key});

  @override
  ConsumerState<EmergencyFailSafeDialog> createState() => _EmergencyFailSafeDialogState();
}

class _EmergencyFailSafeDialogState extends ConsumerState<EmergencyFailSafeDialog> {
  FailSafeAction _selected = FailSafeAction.returnToHome;
  bool _isDispatching = false;

  Future<void> _confirm() async {
    final deviceId = ref.read(missionPlannerProvider).targetDeviceId;
    if (deviceId == null) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('Select a target device first.')),
        );
      }
      return;
    }

    setState(() => _isDispatching = true);
    final repository = ref.read(commandRepositoryProvider);
    final commandType = _selected == FailSafeAction.returnToHome
        ? DeviceCommandType.returnToHome
        : DeviceCommandType.emergencyLand;
    final label = _selected == FailSafeAction.returnToHome ? 'RETURN TO HOME' : 'EMERGENCY LAND';

    try {
      await repository.dispatchCommand(
        deviceId: deviceId,
        commandType: commandType,
        params: {
          'priority': 'critical',
          'fail_safe': true,
          'reason': 'Manual tactical fail-safe trigger',
        },
      );
      if (mounted) {
        Navigator.of(context).pop();
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('$label command dispatched.')),
        );
      }
    } catch (_) {
      if (mounted) {
        setState(() => _isDispatching = false);
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('Fail-safe dispatch failed.')),
        );
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return AlertDialog(
      backgroundColor: TacticalColors.surface,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(12),
        side: BorderSide(color: TacticalColors.critical.withOpacity(0.6)),
      ),
      title: Row(
        children: [
          Icon(Icons.emergency, color: TacticalColors.critical, size: 22),
          const SizedBox(width: 8),
          Text(
            'EMERGENCY FAIL-SAFE',
            style: Theme.of(context).textTheme.titleSmall?.copyWith(
                  color: TacticalColors.critical,
                  fontWeight: FontWeight.w800,
                ),
          ),
        ],
      ),
      content: Column(
        mainAxisSize: MainAxisSize.min,
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          const Text(
            'Confirm tactical emergency action. This dispatches a high-priority command to the selected drone.',
            style: TextStyle(color: TacticalColors.textSecondary, fontSize: 12),
          ),
          const SizedBox(height: 16),
          RadioListTile<FailSafeAction>(
            dense: true,
            contentPadding: EdgeInsets.zero,
            title: const Text('Return to Home (RTH)', style: TextStyle(fontSize: 13)),
            subtitle: const Text('Recall drone to home position', style: TextStyle(fontSize: 11)),
            value: FailSafeAction.returnToHome,
            groupValue: _selected,
            activeColor: TacticalColors.warning,
            onChanged: _isDispatching ? null : (v) => setState(() => _selected = v!),
          ),
          RadioListTile<FailSafeAction>(
            dense: true,
            contentPadding: EdgeInsets.zero,
            title: const Text('Emergency Land', style: TextStyle(fontSize: 13)),
            subtitle: const Text('Immediate landing at current position', style: TextStyle(fontSize: 11)),
            value: FailSafeAction.emergencyLand,
            groupValue: _selected,
            activeColor: TacticalColors.critical,
            onChanged: _isDispatching ? null : (v) => setState(() => _selected = v!),
          ),
        ],
      ),
      actions: [
        TextButton(
          onPressed: _isDispatching ? null : () => Navigator.of(context).pop(),
          child: const Text('Cancel'),
        ),
        FilledButton.icon(
          style: FilledButton.styleFrom(backgroundColor: TacticalColors.critical),
          onPressed: _isDispatching ? null : _confirm,
          icon: _isDispatching
              ? const SizedBox(
                  width: 16,
                  height: 16,
                  child: CircularProgressIndicator(strokeWidth: 2, color: Colors.white),
                )
              : const Icon(Icons.send, size: 18),
          label: Text(_isDispatching ? 'DISPATCHING...' : 'CONFIRM FAIL-SAFE'),
        ),
      ],
    );
  }
}
