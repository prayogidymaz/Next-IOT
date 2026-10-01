import 'package:flutter/material.dart';

import '../../../core/theme/tactical_theme.dart';
import '../../devices/models/device_models.dart';
import 'bento_compact_surface.dart';

/// Compact smart-home controls for dashboard grid (demo state from device list context).
class CompactSmartHomeControlCard extends StatefulWidget {
  const CompactSmartHomeControlCard({super.key, required this.devices});

  final List<Device> devices;

  @override
  State<CompactSmartHomeControlCard> createState() =>
      _CompactSmartHomeControlCardState();
}

class _CompactSmartHomeControlCardState
    extends State<CompactSmartHomeControlCard> {
  bool _relayOn = true;

  @override
  Widget build(BuildContext context) {
    final smartCount = widget.devices
        .where(
          (d) => DeviceType.fromApiValue(d.deviceType) == DeviceType.smartHome,
        )
        .length;
    final onlineSmart = widget.devices
        .where(
          (d) =>
              DeviceType.fromApiValue(d.deviceType) == DeviceType.smartHome &&
              d.connectionStatus == DeviceConnectionStatus.online,
        )
        .length;

    return BentoCompactSurface(
      height: 132,
      accentColor: BentoTokens.accentLavender,
      child: Row(
        children: [
          Expanded(
            flex: 3,
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text('Smart home',
                    style: Theme.of(context).textTheme.titleSmall),
                const SizedBox(height: 6),
                Text(
                  '$onlineSmart / ${smartCount == 0 ? '—' : smartCount} nodes live',
                  style: Theme.of(context).textTheme.bodySmall,
                ),
                const Spacer(),
                Row(
                  children: [
                    Text('Relay', style: Theme.of(context).textTheme.bodySmall),
                    const SizedBox(width: 8),
                    Switch.adaptive(
                      value: _relayOn,
                      activeColor: BentoTokens.accentLime,
                      onChanged: smartCount == 0
                          ? null
                          : (v) => setState(() => _relayOn = v),
                    ),
                  ],
                ),
              ],
            ),
          ),
          const SizedBox(width: 12),
          Expanded(
            flex: 2,
            child: Container(
              padding: const EdgeInsets.all(12),
              decoration: BoxDecoration(
                color: BentoTokens.accentLavender.withOpacity(0.12),
                borderRadius: BorderRadius.circular(18),
                border: Border.all(
                  color: BentoTokens.accentLavender.withOpacity(0.35),
                ),
              ),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  Text('HVAC', style: Theme.of(context).textTheme.bodySmall),
                  Text(
                    smartCount == 0 ? '—°' : '23.5°',
                    style: Theme.of(context).textTheme.headlineSmall?.copyWith(
                          fontWeight: FontWeight.w800,
                          color: BentoTokens.accentLavender,
                          height: 1,
                        ),
                  ),
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }
}
