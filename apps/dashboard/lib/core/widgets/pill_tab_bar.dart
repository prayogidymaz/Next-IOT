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
            borderRadius: BorderRadius.circular(24),
            child: AnimatedContainer(
              duration: const Duration(milliseconds: 200),
              padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 10),
              decoration: BoxDecoration(
                color: isSelected ? TacticalColors.cyan.withOpacity(0.15) : TacticalColors.surface,
                borderRadius: BorderRadius.circular(24),
                border: Border.all(
                  color: isSelected ? TacticalColors.borderNeon : TacticalColors.border,
                  width: isSelected ? 1.5 : 1,
                ),
                boxShadow: isSelected
                    ? [BoxShadow(color: TacticalColors.cyanGlow, blurRadius: 8)]
                    : null,
              ),
              child: Row(
                mainAxisSize: MainAxisSize.min,
                children: [
                  if (tab.icon != null) ...[
                    Icon(
                      tab.icon,
                      size: 16,
                      color: isSelected ? TacticalColors.borderNeon : TacticalColors.textSecondary,
                    ),
                    const SizedBox(width: 6),
                  ],
                  Text(
                    tab.label,
                    style: TextStyle(
                      color: isSelected ? TacticalColors.borderNeon : TacticalColors.textSecondary,
                      fontWeight: isSelected ? FontWeight.w700 : FontWeight.w500,
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
