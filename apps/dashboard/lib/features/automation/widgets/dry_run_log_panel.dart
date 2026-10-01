import 'package:flutter/material.dart';

import '../../../core/theme/tactical_theme.dart';
import '../models/automation_pipeline_models.dart';

class DryRunLogPanel extends StatelessWidget {
  const DryRunLogPanel({
    super.key,
    this.result,
    this.isTesting = false,
    this.onClose,
    this.sidebar = false,
  });

  final PipelineTestRunResult? result;
  final bool isTesting;
  final VoidCallback? onClose;
  final bool sidebar;

  @override
  Widget build(BuildContext context) {
    if (sidebar) {
      return Material(
        key: const Key('dry-run-log-sidebar'),
        color: TacticalColors.surface,
        elevation: 8,
        child: DecoratedBox(
          decoration: const BoxDecoration(
            border: Border(left: BorderSide(color: TacticalColors.border)),
          ),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              _SidebarHeader(
                result: result,
                isTesting: isTesting,
                onClose: onClose,
              ),
              const Divider(height: 1, color: TacticalColors.border),
              Expanded(child: _LogBody(result: result, isTesting: isTesting)),
            ],
          ),
        ),
      );
    }

    return SizedBox(
      height: result == null ? 160 : 200,
      child: DecoratedBox(
        decoration: const BoxDecoration(
          color: TacticalColors.surface,
          border: Border(top: BorderSide(color: TacticalColors.border)),
        ),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            if (result != null)
              _SidebarHeader(result: result, isTesting: isTesting),
            if (result != null)
              const Divider(height: 1, color: TacticalColors.border),
            Expanded(child: _LogBody(result: result, isTesting: isTesting)),
          ],
        ),
      ),
    );
  }
}

class _SidebarHeader extends StatelessWidget {
  const _SidebarHeader({
    required this.result,
    required this.isTesting,
    this.onClose,
  });

  final PipelineTestRunResult? result;
  final bool isTesting;
  final VoidCallback? onClose;

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.fromLTRB(16, 14, 8, 12),
      child: Row(
        children: [
          Icon(
            isTesting
                ? Icons.hourglass_top
                : result?.executed == true
                    ? Icons.check_circle
                    : Icons.info_outline,
            size: 18,
            color: isTesting
                ? TacticalColors.cyan
                : result?.executed == true
                    ? TacticalColors.success
                    : TacticalColors.warning,
          ),
          const SizedBox(width: 8),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  'Dry-Run Execution Log',
                  style: Theme.of(context).textTheme.titleSmall,
                ),
                if (result != null)
                  Text(
                    '${result!.pipelineName} · ${result!.eventType}',
                    style: Theme.of(context).textTheme.bodySmall,
                  ),
              ],
            ),
          ),
          if (result != null)
            Text(
              result!.executed ? 'EXECUTED' : 'NO MATCH',
              style: TextStyle(
                color: result!.executed
                    ? TacticalColors.success
                    : TacticalColors.warning,
                fontWeight: FontWeight.w700,
                fontSize: 11,
                letterSpacing: 0.8,
              ),
            ),
          if (onClose != null)
            IconButton(
              tooltip: 'Close',
              onPressed: onClose,
              icon: const Icon(Icons.close, size: 20),
            ),
        ],
      ),
    );
  }
}

class _LogBody extends StatelessWidget {
  const _LogBody({required this.result, required this.isTesting});

  final PipelineTestRunResult? result;
  final bool isTesting;

  @override
  Widget build(BuildContext context) {
    if (isTesting) {
      return const Center(
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            CircularProgressIndicator(strokeWidth: 2),
            SizedBox(height: 12),
            Text(
              'Running dry-run simulation…',
              style: TextStyle(color: TacticalColors.textSecondary),
            ),
          ],
        ),
      );
    }

    if (result == null) {
      return const Padding(
        padding: EdgeInsets.all(16),
        child: Text(
          'Dry-run execution log will appear here.',
          style: TextStyle(color: TacticalColors.textSecondary),
        ),
      );
    }

    return ListView.separated(
      padding: const EdgeInsets.all(12),
      itemCount: result!.steps.length,
      separatorBuilder: (_, __) => const SizedBox(height: 8),
      itemBuilder: (context, index) {
        final step = result!.steps[index];
        return _StepTile(step: step, index: index + 1);
      },
    );
  }
}

class _StepTile extends StatelessWidget {
  const _StepTile({required this.step, required this.index});

  final PipelineExecutionStepModel step;
  final int index;

  @override
  Widget build(BuildContext context) {
    final color =
        step.matched ? TacticalColors.success : TacticalColors.textSecondary;
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 10),
      decoration: BoxDecoration(
        color: TacticalColors.background,
        borderRadius: BorderRadius.circular(8),
        border: Border.all(color: TacticalColors.border),
      ),
      child: Row(
        children: [
          CircleAvatar(
            radius: 12,
            backgroundColor: color.withOpacity(0.15),
            child: Text('$index', style: TextStyle(fontSize: 11, color: color)),
          ),
          const SizedBox(width: 12),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  '${step.nodeType} · ${step.subtype}',
                  style: Theme.of(context).textTheme.bodySmall?.copyWith(
                        color: TacticalColors.textPrimary,
                        fontWeight: FontWeight.w600,
                      ),
                ),
                Text(
                  'node ${step.nodeId} · ${step.matched ? "matched" : "skipped"}',
                  style: Theme.of(context).textTheme.bodySmall,
                ),
              ],
            ),
          ),
          Icon(
            step.matched ? Icons.check : Icons.remove,
            size: 18,
            color: color,
          ),
        ],
      ),
    );
  }
}
