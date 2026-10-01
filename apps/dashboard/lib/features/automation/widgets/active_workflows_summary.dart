import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../../core/theme/tactical_theme.dart';
import '../../../routing/navigation_config.dart';
import '../../dashboard/widgets/bento_compact_surface.dart';
import '../providers/automation_summary_provider.dart';

/// Horizontal compact bento card for asymmetric dashboard grid.
class CompactActiveWorkflowsBento extends ConsumerWidget {
  const CompactActiveWorkflowsBento({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final summaryAsync = ref.watch(automationPipelinesSummaryProvider);

    return BentoCompactSurface(
      height: 132,
      key: const Key('active-workflows-summary'),
      child: summaryAsync.when(
        loading: () => const Center(
          child: SizedBox(
            width: 22,
            height: 22,
            child: CircularProgressIndicator(strokeWidth: 2),
          ),
        ),
        error: (error, _) => Text(
          'Workflows unavailable',
          style: Theme.of(context).textTheme.bodySmall,
        ),
        data: (pipelines) {
          final active =
              pipelines.where((pipeline) => pipeline.isActive).length;
          final subtitle = pipelines.isEmpty
              ? 'No pipelines yet.'
              : pipelines.length == 1
                  ? pipelines.first.name
                  : '${pipelines.first.name} +${pipelines.length - 1} more';

          return Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              Row(
                children: [
                  const Icon(Icons.account_tree_outlined,
                      size: 18, color: BentoTokens.accentSoftBlue),
                  const SizedBox(width: 8),
                  Expanded(
                    child: Text(
                      'Active workflows',
                      style: Theme.of(context).textTheme.titleSmall,
                      maxLines: 1,
                      overflow: TextOverflow.ellipsis,
                    ),
                  ),
                  _StatusPill(
                    label: '$active live',
                    color: TacticalColors.success,
                  ),
                  IconButton(
                    key: const Key('open-automation-studio'),
                    visualDensity: VisualDensity.compact,
                    padding: EdgeInsets.zero,
                    constraints:
                        const BoxConstraints(minWidth: 28, minHeight: 28),
                    onPressed: () => context.go(AppRoutes.studio),
                    icon: const Icon(Icons.open_in_new, size: 16),
                    tooltip: 'Automation Studio',
                  ),
                ],
              ),
              const SizedBox(height: 6),
              Text(
                subtitle,
                maxLines: 2,
                overflow: TextOverflow.ellipsis,
                style: Theme.of(context).textTheme.bodySmall,
              ),
            ],
          );
        },
      ),
    );
  }
}

class _StatusPill extends StatelessWidget {
  const _StatusPill({required this.label, required this.color});

  final String label;
  final Color color;

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
      decoration: BoxDecoration(
        color: color.withOpacity(0.12),
        borderRadius: BorderRadius.circular(BentoTokens.radiusPill),
        border: Border.all(color: color.withOpacity(0.35)),
      ),
      child: Text(
        label,
        style: Theme.of(context).textTheme.labelSmall?.copyWith(
              color: color,
              fontWeight: FontWeight.w700,
            ),
      ),
    );
  }
}

/// Lightweight dashboard summary — no canvas engine loaded.
class ActiveWorkflowsSummary extends ConsumerWidget {
  const ActiveWorkflowsSummary({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final summaryAsync = ref.watch(automationPipelinesSummaryProvider);

    return Card(
      key: const Key('active-workflows-summary'),
      margin: EdgeInsets.zero,
      color: TacticalColors.surfaceElevated,
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            Row(
              children: [
                const Icon(Icons.account_tree_outlined,
                    size: 20, color: TacticalColors.cyan),
                const SizedBox(width: 8),
                Text(
                  'Active Workflows',
                  style: Theme.of(context).textTheme.titleSmall,
                ),
                const Spacer(),
                TextButton.icon(
                  key: const Key('open-automation-studio'),
                  onPressed: () => context.go(AppRoutes.studio),
                  icon: const Icon(Icons.open_in_new, size: 16),
                  label: const Text('Automation Studio'),
                ),
              ],
            ),
            const SizedBox(height: 12),
            summaryAsync.when(
              loading: () => const LinearProgressIndicator(minHeight: 2),
              error: (error, _) => Text(
                'Could not load workflows: $error',
                style: Theme.of(context)
                    .textTheme
                    .bodySmall
                    ?.copyWith(color: TacticalColors.warning),
              ),
              data: (pipelines) {
                if (pipelines.isEmpty) {
                  return Text(
                    'No pipelines deployed yet. Open Automation Studio to design your first workflow.',
                    style: Theme.of(context).textTheme.bodySmall,
                  );
                }

                final active =
                    pipelines.where((pipeline) => pipeline.isActive).length;
                final paused = pipelines.length - active;

                return Column(
                  crossAxisAlignment: CrossAxisAlignment.stretch,
                  children: [
                    Wrap(
                      spacing: 12,
                      runSpacing: 8,
                      children: [
                        _MetricChip(
                          label: 'Active',
                          value: '$active',
                          color: TacticalColors.success,
                        ),
                        _MetricChip(
                          label: 'Paused',
                          value: '$paused',
                          color: TacticalColors.textSecondary,
                        ),
                        _MetricChip(
                          label: 'Total',
                          value: '${pipelines.length}',
                          color: TacticalColors.cyan,
                        ),
                      ],
                    ),
                    const SizedBox(height: 12),
                    ...pipelines.take(3).map(
                          (pipeline) => Padding(
                            padding: const EdgeInsets.only(bottom: 8),
                            child: Row(
                              children: [
                                Icon(
                                  pipeline.isActive
                                      ? Icons.play_circle_outline
                                      : Icons.pause_circle_outline,
                                  size: 16,
                                  color: pipeline.isActive
                                      ? TacticalColors.success
                                      : TacticalColors.textSecondary,
                                ),
                                const SizedBox(width: 8),
                                Expanded(
                                  child: Text(
                                    pipeline.name,
                                    style:
                                        Theme.of(context).textTheme.bodySmall,
                                    overflow: TextOverflow.ellipsis,
                                  ),
                                ),
                                Text(
                                  pipeline.isActive ? 'Active' : 'Paused',
                                  style: Theme.of(context)
                                      .textTheme
                                      .labelSmall
                                      ?.copyWith(
                                        color: pipeline.isActive
                                            ? TacticalColors.success
                                            : TacticalColors.textSecondary,
                                      ),
                                ),
                              ],
                            ),
                          ),
                        ),
                    if (pipelines.length > 3)
                      Text(
                        '+ ${pipelines.length - 3} more — open Studio for full editor & logs',
                        style: Theme.of(context).textTheme.bodySmall?.copyWith(
                              color: TacticalColors.textSecondary,
                            ),
                      ),
                  ],
                );
              },
            ),
          ],
        ),
      ),
    );
  }
}

class _MetricChip extends StatelessWidget {
  const _MetricChip({
    required this.label,
    required this.value,
    required this.color,
  });

  final String label;
  final String value;
  final Color color;

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 6),
      decoration: BoxDecoration(
        color: color.withOpacity(0.12),
        borderRadius: BorderRadius.circular(8),
        border: Border.all(color: color.withOpacity(0.35)),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Text(
            value,
            style: Theme.of(context).textTheme.titleSmall?.copyWith(
                  color: color,
                  fontWeight: FontWeight.w700,
                ),
          ),
          const SizedBox(width: 6),
          Text(label, style: Theme.of(context).textTheme.bodySmall),
        ],
      ),
    );
  }
}
