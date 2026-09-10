import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../core/theme/tactical_theme.dart';
import '../../devices/providers/device_provider.dart';
import '../providers/mission_provider.dart';

class MissionControlOverlay extends ConsumerWidget {
  const MissionControlOverlay({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final mission = ref.watch(missionPlannerProvider);
    final notifier = ref.read(missionPlannerProvider.notifier);
    final devices = ref.watch(deviceProvider).devices;

    if (!mission.plannerMode) return const SizedBox.shrink();

    final size = MediaQuery.sizeOf(context);
    final compact = size.width < 1024;
    final panelWidth = compact ? size.width - 24 : 320.0;

    return Positioned(
      top: compact ? null : 12,
      left: 12,
      right: compact ? 12 : null,
      bottom: compact ? 12 : null,
      width: compact ? null : panelWidth,
      child: Material(
        color: TacticalColors.surface.withOpacity(0.94),
        elevation: 8,
        borderRadius: BorderRadius.circular(12),
        child: Container(
          padding: const EdgeInsets.all(14),
          decoration: BoxDecoration(
            borderRadius: BorderRadius.circular(12),
            border: Border.all(color: TacticalColors.borderNeon.withOpacity(0.45)),
          ),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            mainAxisSize: MainAxisSize.min,
            children: [
              Text('MISSION CONTROL', style: Theme.of(context).textTheme.titleSmall),
              const SizedBox(height: 10),
              if (devices.isEmpty)
                const Text('No devices available.')
              else
                DropdownButtonFormField<String>(
                  isExpanded: true,
                  value: mission.targetDeviceId,
                  dropdownColor: TacticalColors.surfaceElevated,
                  decoration: const InputDecoration(labelText: 'Target device'),
                  items: devices
                      .map(
                        (d) => DropdownMenuItem(
                          value: d.id,
                          child: Text('${d.name} (${d.connectionStatus.label})'),
                        ),
                      )
                      .toList(),
                  onChanged: (value) => notifier.setTargetDevice(value),
                ),
              const SizedBox(height: 12),
              Row(
                children: [
                  Text('Altitude', style: Theme.of(context).textTheme.bodySmall),
                  const Spacer(),
                  Text(
                    '${mission.altitudeM.round()} m',
                    style: const TextStyle(
                      color: TacticalColors.borderNeon,
                      fontWeight: FontWeight.w700,
                    ),
                  ),
                ],
              ),
              Slider(
                min: MissionPlannerState.minAltitude,
                max: MissionPlannerState.maxAltitude,
                divisions: 30,
                value: mission.altitudeM,
                label: '${mission.altitudeM.round()} m',
                onChanged: notifier.setAltitude,
              ),
              Text('Waypoints (${mission.waypoints.length})', style: Theme.of(context).textTheme.bodySmall),
              const SizedBox(height: 6),
              if (mission.waypoints.isEmpty)
                const Text('Tap map to add P1, P2, P3…')
              else
                ConstrainedBox(
                  constraints: const BoxConstraints(maxHeight: 140),
                  child: ListView.builder(
                    shrinkWrap: true,
                    itemCount: mission.waypoints.length,
                    itemBuilder: (context, index) {
                      final wp = mission.waypoints[index];
                      return ListTile(
                        dense: true,
                        contentPadding: EdgeInsets.zero,
                        leading: Text(wp.label, style: const TextStyle(color: TacticalColors.warning)),
                        title: Text(
                          '${wp.latitude.toStringAsFixed(5)}, ${wp.longitude.toStringAsFixed(5)}',
                          style: Theme.of(context).textTheme.bodySmall,
                        ),
                        trailing: Row(
                          mainAxisSize: MainAxisSize.min,
                          children: [
                            IconButton(
                              icon: const Icon(Icons.arrow_upward, size: 16),
                              onPressed: () => notifier.moveWaypointUp(wp.id),
                            ),
                            IconButton(
                              icon: const Icon(Icons.arrow_downward, size: 16),
                              onPressed: () => notifier.moveWaypointDown(wp.id),
                            ),
                            IconButton(
                              icon: const Icon(Icons.delete_outline, size: 16, color: TacticalColors.critical),
                              onPressed: () => notifier.removeWaypoint(wp.id),
                            ),
                          ],
                        ),
                      );
                    },
                  ),
                ),
              const SizedBox(height: 10),
              FilledButton.icon(
                onPressed: mission.isDispatching ? null : () => notifier.dispatchMission(),
                icon: const Icon(Icons.flight_takeoff, size: 18),
                label: const Text('Dispatch Mission to Drone'),
              ),
              const SizedBox(height: 8),
              OutlinedButton.icon(
                onPressed: mission.isDispatching ? null : () => notifier.emergencyRtl(),
                icon: const Icon(Icons.home, size: 18, color: TacticalColors.critical),
                label: const Text('Emergency RTL', style: TextStyle(color: TacticalColors.critical)),
                style: OutlinedButton.styleFrom(
                  side: const BorderSide(color: TacticalColors.critical),
                ),
              ),
              if (mission.feedback != null) ...[
                const SizedBox(height: 8),
                Text(
                  mission.feedback!,
                  style: TextStyle(
                    color: mission.feedback!.toLowerCase().contains('fail')
                        ? TacticalColors.critical
                        : TacticalColors.success,
                    fontSize: 12,
                  ),
                ),
              ],
            ],
          ),
        ),
      ),
    );
  }
}
