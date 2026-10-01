import 'package:flutter/material.dart';

import '../../../core/theme/tactical_theme.dart';

/// Shared compact bento shell — fixed padding, subtle border, no full-page stretch.
class BentoCompactSurface extends StatelessWidget {
  const BentoCompactSurface({
    super.key,
    required this.child,
    this.height,
    this.padding = const EdgeInsets.all(14),
    this.accentColor,
  });

  final Widget child;
  final double? height;
  final EdgeInsetsGeometry padding;
  final Color? accentColor;

  @override
  Widget build(BuildContext context) {
    final borderColor =
        (accentColor ?? TacticalColors.border).withOpacity(0.55);
    return SizedBox(
      height: height,
      child: DecoratedBox(
        decoration: BoxDecoration(
          color: TacticalColors.surfaceElevated,
          borderRadius: BorderRadius.circular(BentoTokens.radius),
          border: Border.all(color: borderColor),
        ),
        child: Padding(padding: padding, child: child),
      ),
    );
  }
}
