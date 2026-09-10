import 'package:flutter/material.dart';

import '../theme/tactical_theme.dart';

class TacticalCard extends StatelessWidget {
  const TacticalCard({
    super.key,
    required this.child,
    this.padding = const EdgeInsets.all(16),
    this.accentColor,
    this.onTap,
  });

  final Widget child;
  final EdgeInsetsGeometry padding;
  final Color? accentColor;
  final VoidCallback? onTap;

  @override
  Widget build(BuildContext context) {
    final accent = accentColor ?? TacticalColors.borderNeon;

    final card = Card(
      clipBehavior: Clip.antiAlias,
      child: Container(
        decoration: BoxDecoration(
          gradient: LinearGradient(
            begin: Alignment.topLeft,
            end: Alignment.bottomRight,
            colors: [
              TacticalColors.surfaceElevated,
              TacticalColors.surfaceElevated.withOpacity(0.85),
            ],
          ),
          border: Border(
            left: BorderSide(color: accent.withOpacity(0.6), width: 3),
          ),
          boxShadow: [
            BoxShadow(
              color: accent.withOpacity(0.08),
              blurRadius: 12,
              offset: const Offset(0, 4),
            ),
          ],
        ),
        child: Padding(padding: padding, child: child),
      ),
    );

    if (onTap == null) return card;
    return InkWell(onTap: onTap, child: card);
  }
}
