import 'package:flutter/material.dart';

import '../theme/tactical_theme.dart';

class TacticalCard extends StatelessWidget {
  const TacticalCard({
    super.key,
    required this.child,
    this.padding = const EdgeInsets.all(22),
    this.accentColor,
    this.onTap,
  });

  final Widget child;
  final EdgeInsetsGeometry padding;
  final Color? accentColor;
  final VoidCallback? onTap;

  @override
  Widget build(BuildContext context) {
    final card = Card(
      clipBehavior: Clip.antiAlias,
      color: TacticalColors.surfaceElevated,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(BentoTokens.radius),
        side: BorderSide(
          color: (accentColor ?? TacticalColors.border).withOpacity( 0.55),
        ),
      ),
      child: Padding(padding: padding, child: child),
    );

    if (onTap == null) return card;
    return Material(
      color: Colors.transparent,
      child: InkWell(
        onTap: onTap,
        borderRadius: BorderRadius.circular(BentoTokens.radius),
        child: card,
      ),
    );
  }
}
