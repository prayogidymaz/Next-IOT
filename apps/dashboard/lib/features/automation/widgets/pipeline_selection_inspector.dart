import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../core/theme/tactical_theme.dart';
import '../models/automation_pipeline_models.dart';
import '../providers/automation_builder_provider.dart';

/// Detail panel for the currently selected node or edge on the canvas.
class PipelineSelectionInspector extends ConsumerWidget {
  const PipelineSelectionInspector({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final state = ref.watch(automationBuilderProvider);
    final notifier = ref.read(automationBuilderProvider.notifier);

    final selectedEdge = state.selectedEdge;
    PipelineNodeModel? selectedNode;
    if (state.selectedNodeId != null) {
      for (final node in state.nodes) {
        if (node.id == state.selectedNodeId) {
          selectedNode = node;
          break;
        }
      }
    }

    if (selectedEdge == null && selectedNode == null) {
      return const SizedBox.shrink();
    }

    return Material(
      elevation: 6,
      color: TacticalColors.surfaceElevated.withOpacity(0.96),
      borderRadius: BorderRadius.circular(10),
      child: Container(
        key: const Key('pipeline-selection-inspector'),
        padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 10),
        decoration: BoxDecoration(
          borderRadius: BorderRadius.circular(10),
          border: Border.all(color: TacticalColors.borderNeon.withOpacity(0.45)),
        ),
        child: Row(
          children: [
            Icon(
              selectedEdge != null ? Icons.timeline : Icons.select_all,
              size: 18,
              color: TacticalColors.cyan,
            ),
            const SizedBox(width: 10),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                mainAxisSize: MainAxisSize.min,
                children: [
                  Text(
                    selectedEdge != null ? 'CONNECTION SELECTED' : 'NODE SELECTED',
                    style: Theme.of(context).textTheme.labelSmall?.copyWith(
                          color: TacticalColors.cyan,
                          letterSpacing: 0.6,
                        ),
                  ),
                  const SizedBox(height: 2),
                  Text(
                    selectedEdge != null
                        ? '${selectedEdge.fromNode} → ${selectedEdge.toNode}'
                        : '${selectedNode!.label} (${selectedNode.type.name})',
                    style: Theme.of(context).textTheme.bodySmall,
                  ),
                ],
              ),
            ),
            if (selectedEdge != null) ...[
              OutlinedButton.icon(
                key: const Key('pipeline-edge-disconnect-button'),
                onPressed: notifier.removeSelectedEdge,
                icon: const Icon(Icons.link_off, size: 16),
                label: const Text('Disconnect'),
              ),
              const SizedBox(width: 8),
            ],
            IconButton(
              tooltip: 'Clear selection',
              onPressed: notifier.deselectAll,
              icon: const Icon(Icons.close, size: 18),
            ),
          ],
        ),
      ),
    );
  }
}
