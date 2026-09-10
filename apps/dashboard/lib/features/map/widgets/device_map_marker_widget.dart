import 'package:flutter/material.dart';

import '../../devices/models/device_models.dart';
import '../models/device_map_models.dart';

class DeviceMapMarkerWidget extends StatelessWidget {
  const DeviceMapMarkerWidget({
    super.key,
    required this.marker,
    required this.isSelected,
    required this.onTap,
    this.compact = false,
  });

  final DeviceMapMarker marker;
  final bool isSelected;
  final VoidCallback onTap;
  final bool compact;

  IconData get _icon {
    switch (DeviceType.fromApiValue(marker.device.deviceType)) {
      case DeviceType.drone:
        return Icons.flight;
      case DeviceType.cyberdeck:
        return Icons.terminal;
      case DeviceType.robot:
        return Icons.smart_toy;
      case DeviceType.lorawan:
        return Icons.cell_tower;
      case DeviceType.sensor:
      case null:
        return Icons.sensors;
    }
  }

  @override
  Widget build(BuildContext context) {
    final color = marker.status.color;
    final size = isSelected ? 40.0 : 32.0;

    return GestureDetector(
      onTap: onTap,
      child: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          Container(
            width: size,
            height: size,
            decoration: BoxDecoration(
              shape: BoxShape.circle,
              color: color.withOpacity(0.2),
              border: Border.all(color: color, width: isSelected ? 3 : 2),
              boxShadow: [
                BoxShadow(
                  color: color.withOpacity(marker.status.pulse ? 0.55 : 0.35),
                  blurRadius: isSelected ? 14 : 10,
                  spreadRadius: marker.status.pulse ? 2 : 1,
                ),
              ],
            ),
            child: Icon(_icon, color: color, size: isSelected ? 20 : 16),
          ),
          if (!compact) ...[
            const SizedBox(height: 4),
            Container(
              constraints: const BoxConstraints(maxWidth: 72),
              padding: const EdgeInsets.symmetric(horizontal: 4, vertical: 2),
              decoration: BoxDecoration(
                color: Colors.black.withOpacity(0.65),
                borderRadius: BorderRadius.circular(4),
                border: Border.all(color: color.withOpacity(0.5)),
              ),
              child: Text(
                marker.device.name,
                maxLines: 1,
                overflow: TextOverflow.ellipsis,
                textAlign: TextAlign.center,
                style: TextStyle(
                  color: color,
                  fontSize: 9,
                  fontWeight: FontWeight.w700,
                ),
              ),
            ),
          ],
        ],
      ),
    );
  }
}
