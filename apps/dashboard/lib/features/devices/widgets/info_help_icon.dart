import 'package:flutter/material.dart';

import '../../../core/theme/tactical_theme.dart';

/// Small (?) icon with hover tooltip and optional tap popover.
class InfoHelpIcon extends StatelessWidget {
  const InfoHelpIcon({
    super.key,
    required this.message,
    this.size = 16,
    this.title,
  });

  final String message;
  final double size;
  final String? title;

  void _showPopover(BuildContext context) {
    showDialog<void>(
      context: context,
      builder: (ctx) => AlertDialog(
        backgroundColor: TacticalColors.surface,
        title: Text(title ?? 'Penjelasan'),
        content: SingleChildScrollView(
          child: Text(
            message,
            style: Theme.of(ctx).textTheme.bodyMedium,
          ),
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(ctx),
            child: const Text('Mengerti'),
          ),
        ],
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Tooltip(
      message: message,
      preferBelow: false,
      waitDuration: const Duration(milliseconds: 300),
      child: InkWell(
        onTap: () => _showPopover(context),
        borderRadius: BorderRadius.circular(12),
        child: Padding(
          padding: const EdgeInsets.all(2),
          child: Icon(
            Icons.help_outline,
            size: size,
            color: TacticalColors.textSecondary,
          ),
        ),
      ),
    );
  }
}
