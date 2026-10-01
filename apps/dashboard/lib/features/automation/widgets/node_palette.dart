import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../core/theme/tactical_theme.dart';
import '../models/automation_pipeline_models.dart';
import '../providers/palette_placement_provider.dart';

class NodePalette extends StatelessWidget {
  const NodePalette({super.key});

  @override
  Widget build(BuildContext context) {
    return Container(
      width: 240,
      decoration: const BoxDecoration(
        color: TacticalColors.surface,
        border: Border(right: BorderSide(color: TacticalColors.border)),
      ),
      child: ListView(
        padding: const EdgeInsets.all(16),
        children: [
          Text('NODE PALETTE', style: Theme.of(context).textTheme.labelLarge),
          const SizedBox(height: 4),
          Text(
            'Click item to select · click canvas to place',
            style: Theme.of(context).textTheme.bodySmall,
          ),
          const SizedBox(height: 16),
          _Section(
            title: 'TRIGGER',
            color: TacticalColors.info,
            items: TriggerSubtype.values
                .map((s) => _PaletteTile(
                      label: s.label,
                      icon: Icons.flash_on,
                      color: TacticalColors.info,
                      data: PalettePlacementData(
                        type: PipelineNodeType.trigger,
                        subtype: s.apiValue,
                      ),
                    ))
                .toList(),
          ),
          const SizedBox(height: 16),
          _Section(
            title: 'CONDITION',
            color: TacticalColors.warning,
            items: ConditionSubtype.values
                .map((s) => _PaletteTile(
                      label: s.label,
                      icon: Icons.filter_alt,
                      color: TacticalColors.warning,
                      data: PalettePlacementData(
                        type: PipelineNodeType.condition,
                        subtype: s.apiValue,
                      ),
                    ))
                .toList(),
          ),
          const SizedBox(height: 16),
          _Section(
            title: 'ACTION',
            color: TacticalColors.success,
            items: ActionSubtype.values
                .map((s) => _PaletteTile(
                      label: s.label,
                      icon: Icons.play_circle,
                      color: TacticalColors.success,
                      data: PalettePlacementData(
                        type: PipelineNodeType.action,
                        subtype: s.apiValue,
                      ),
                    ))
                .toList(),
          ),
        ],
      ),
    );
  }
}

class _Section extends StatelessWidget {
  const _Section({
    required this.title,
    required this.color,
    required this.items,
  });

  final String title;
  final Color color;
  final List<Widget> items;

  @override
  Widget build(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        Row(
          children: [
            Container(
                width: 8,
                height: 8,
                decoration:
                    BoxDecoration(color: color, shape: BoxShape.circle)),
            const SizedBox(width: 8),
            Text(title,
                style: Theme.of(context)
                    .textTheme
                    .titleSmall
                    ?.copyWith(color: color)),
          ],
        ),
        const SizedBox(height: 8),
        ...items,
      ],
    );
  }
}

class _PaletteTile extends ConsumerWidget {
  const _PaletteTile({
    required this.label,
    required this.icon,
    required this.color,
    required this.data,
  });

  final String label;
  final IconData icon;
  final Color color;
  final PalettePlacementData data;

  void _select(WidgetRef ref) {
    // ignore: avoid_print
    print('SELECTED NODE: ${data.subtype}');
    ref.read(palettePlacementProvider.notifier).selectPlacement(data, label);
  }

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final placement = ref.watch(palettePlacementProvider);
    final isSelected = placement.isActive &&
        placement.activePlacement?.subtype == data.subtype &&
        placement.label == label;

    return Padding(
      padding: const EdgeInsets.only(bottom: 8),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.center,
        children: [
          Expanded(
            child: Material(
              color: Colors.transparent,
              child: InkWell(
                borderRadius: BorderRadius.circular(8),
                onTap: () => _select(ref),
                child: _TileBody(
                    label: label,
                    icon: icon,
                    color: color,
                    selected: isSelected),
              ),
            ),
          ),
          const SizedBox(width: 6),
          Material(
            color: Colors.transparent,
            child: InkWell(
              borderRadius: BorderRadius.circular(8),
              onTap: () => _select(ref),
              child: Tooltip(
                message: 'Select for placement',
                child: _SelectHandle(color: color, selected: isSelected),
              ),
            ),
          ),
        ],
      ),
    );
  }
}

class _SelectHandle extends StatelessWidget {
  const _SelectHandle({required this.color, this.selected = false});

  final Color color;
  final bool selected;

  @override
  Widget build(BuildContext context) {
    return Container(
      width: 28,
      height: 40,
      alignment: Alignment.center,
      decoration: BoxDecoration(
        color: selected ? color.withOpacity(0.2) : TacticalColors.background,
        borderRadius: BorderRadius.circular(8),
        border: Border.all(
            color: color.withOpacity(selected ? 0.9 : 0.45),
            width: selected ? 2 : 1),
      ),
      child: Icon(Icons.add_circle_outline, size: 18, color: color),
    );
  }
}

class _TileBody extends StatelessWidget {
  const _TileBody({
    required this.label,
    required this.icon,
    required this.color,
    this.selected = false,
    this.elevated = false,
  });

  final String label;
  final IconData icon;
  final Color color;
  final bool selected;
  final bool elevated;

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 10),
      decoration: BoxDecoration(
        color: elevated
            ? TacticalColors.surfaceElevated
            : selected
                ? color.withOpacity(0.12)
                : TacticalColors.background,
        borderRadius: BorderRadius.circular(8),
        border: Border.all(
            color: color.withOpacity(selected ? 0.9 : 0.5),
            width: selected ? 2 : 1),
      ),
      child: Row(
        children: [
          Icon(icon, size: 18, color: color),
          const SizedBox(width: 10),
          Expanded(
              child: Text(label, style: Theme.of(context).textTheme.bodySmall)),
        ],
      ),
    );
  }
}
