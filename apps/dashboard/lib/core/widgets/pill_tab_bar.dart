import 'package:flutter/material.dart';

import '../theme/tactical_theme.dart';

class PillTab<T> {
  const PillTab({required this.value, required this.label, this.icon});

  final T value;
  final String label;
  final IconData? icon;
}

class PillTabBar<T> extends StatelessWidget {
  const PillTabBar({
    super.key,
    required this.tabs,
    required this.selected,
    required this.onSelected,
  });

  final List<PillTab<T>> tabs;
  final T selected;
  final ValueChanged<T> onSelected;

  @override
  Widget build(BuildContext context) {
    return Wrap(
      spacing: 8,
      runSpacing: 8,
      children: tabs.map((tab) {
        final isSelected = tab.value == selected;
        return Material(
          color: Colors.transparent,
          child: InkWell(
            onTap: () => onSelected(tab.value),
            borderRadius: BorderRadius.circular(BentoTokens.radiusPill),
            child: AnimatedContainer(
              duration: const Duration(milliseconds: 200),
              padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 10),
              decoration: BoxDecoration(
                color: isSelected
                    ? TacticalColors.success.withOpacity( 0.14)
                    : TacticalColors.surfaceElevated,
                borderRadius: BorderRadius.circular(BentoTokens.radiusPill),
                border: Border.all(
                  color: isSelected
                      ? TacticalColors.success.withOpacity( 0.55)
                      : TacticalColors.border,
                  width: isSelected ? 2 : 1,
                ),
              ),
              child: Row(
                mainAxisSize: MainAxisSize.min,
                children: [
                  if (tab.icon != null) ...[
                    Icon(
                      tab.icon,
                      size: 16,
                      color: isSelected
                          ? TacticalColors.success
                          : TacticalColors.textSecondary,
                    ),
                    const SizedBox(width: 6),
                  ],
                  Text(
                    tab.label,
                    style: TextStyle(
                      color: isSelected
                          ? TacticalColors.success
                          : TacticalColors.textSecondary,
                      fontWeight:
                          isSelected ? FontWeight.w700 : FontWeight.w500,
                      fontSize: 13,
                    ),
                  ),
                ],
              ),
            ),
          ),
        );
      }).toList(),
    );
  }
}
