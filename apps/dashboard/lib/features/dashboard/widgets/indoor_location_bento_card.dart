import 'package:flutter/material.dart';

import '../../../core/theme/tactical_theme.dart';
import '../../devices/models/device_models.dart';

/// Bento placement card for stationary / indoor devices without GPS.
class IndoorLocationBentoCard extends StatelessWidget {
  const IndoorLocationBentoCard({
    super.key,
    required this.device,
    this.height = 320,
  });

  final Device device;
  final double height;

  static const indoorLocationKey = Key('indoor-location-bento');

  String get _roomLabel {
    final name = device.name;
    final parts = name.split(RegExp(r'\s+'));
    final first = parts.isNotEmpty ? parts.first : null;
    if (first != null && first.length >= 3) return first;
    return 'Building floor plan';
  }

  @override
  Widget build(BuildContext context) {
    final type = DeviceType.fromApiValue(device.deviceType);
    final isSmartHome = type == DeviceType.smartHome;

    return SizedBox(
      key: indoorLocationKey,
      height: height,
      child: Container(
        decoration: BoxDecoration(
          color: TacticalColors.surfaceElevated,
          borderRadius: BorderRadius.circular(BentoTokens.radius),
          border: Border.all(color: TacticalColors.border.withOpacity( 0.7)),
        ),
        padding: const EdgeInsets.all(24),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            Row(
              children: [
                Container(
                  width: 48,
                  height: 48,
                  decoration: BoxDecoration(
                    color: BentoTokens.accentSoftBlue.withOpacity( 0.18),
                    borderRadius: BorderRadius.circular(16),
                  ),
                  child: Icon(
                    isSmartHome ? Icons.meeting_room_outlined : Icons.domain_outlined,
                    color: BentoTokens.accentSoftBlue,
                  ),
                ),
                const SizedBox(width: 16),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        'Indoor Location',
                        style: Theme.of(context).textTheme.titleMedium,
                      ),
                      const SizedBox(height: 4),
                      Text(
                        'Room anchor · $_roomLabel',
                        style: Theme.of(context).textTheme.bodySmall,
                      ),
                    ],
                  ),
                ),
              ],
            ),
            const SizedBox(height: 20),
            Expanded(
              child: Container(
                decoration: BoxDecoration(
                  gradient: LinearGradient(
                    begin: Alignment.topLeft,
                    end: Alignment.bottomRight,
                    colors: [
                      TacticalColors.surface,
                      BentoTokens.accentLavender.withOpacity( 0.08),
                    ],
                  ),
                  borderRadius: BorderRadius.circular(20),
                  border: Border.all(color: TacticalColors.border.withOpacity( 0.5)),
                ),
                child: Stack(
                  children: [
                    Positioned(
                      left: 28,
                      top: 28,
                      child: _AnchorDot(label: 'Anchor', color: BentoTokens.accentLime),
                    ),
                    Positioned(
                      right: 36,
                      bottom: 32,
                      child: Icon(
                        Icons.grid_view_rounded,
                        size: 64,
                        color: TacticalColors.textSecondary.withOpacity( 0.25),
                      ),
                    ),
                    Center(
                      child: Text(
                        device.name,
                        textAlign: TextAlign.center,
                        style: Theme.of(context).textTheme.titleSmall?.copyWith(
                              color: TacticalColors.textPrimary,
                            ),
                      ),
                    ),
                  ],
                ),
              ),
            ),
            const SizedBox(height: 12),
            Text(
              'No outdoor GPS — position is fixed to this indoor zone.',
              style: Theme.of(context).textTheme.bodySmall,
              textAlign: TextAlign.center,
            ),
          ],
        ),
      ),
    );
  }
}

class _AnchorDot extends StatelessWidget {
  const _AnchorDot({required this.label, required this.color});

  final String label;
  final Color color;

  @override
  Widget build(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Container(
          width: 14,
          height: 14,
          decoration: BoxDecoration(
            shape: BoxShape.circle,
            color: color,
            border: Border.all(color: TacticalColors.background, width: 2),
          ),
        ),
        const SizedBox(height: 6),
        Text(label, style: Theme.of(context).textTheme.bodySmall),
      ],
    );
  }
}
