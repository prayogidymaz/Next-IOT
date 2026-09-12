import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../core/theme/tactical_theme.dart';
import '../models/sar_incident_models.dart';
import '../providers/sar_incident_provider.dart';

class SarIncidentResponsePanel extends ConsumerWidget {
  const SarIncidentResponsePanel({
    super.key,
    required this.selectedDeviceId,
    this.onCenterIncident,
  });

  final String? selectedDeviceId;
  final void Function(SarIncident incident)? onCenterIncident;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final state = ref.watch(sarIncidentProvider);
    final notifier = ref.read(sarIncidentProvider.notifier);
    final active = state.activeIncidents;

    return Container(
      width: 340,
      constraints: const BoxConstraints(maxHeight: 420),
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: TacticalColors.surface.withOpacity(0.95),
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: TacticalColors.critical.withOpacity(0.6), width: 1.5),
        boxShadow: [
          BoxShadow(
            color: TacticalColors.critical.withOpacity(0.2),
            blurRadius: 16,
          ),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              const Icon(Icons.emergency, color: TacticalColors.critical, size: 18),
              const SizedBox(width: 8),
              Expanded(
                child: Text(
                  'SAR INCIDENT RESPONSE',
                  style: Theme.of(context).textTheme.labelMedium?.copyWith(
                        color: TacticalColors.critical,
                        fontWeight: FontWeight.w800,
                        letterSpacing: 0.6,
                      ),
                ),
              ),
              IconButton(
                visualDensity: VisualDensity.compact,
                icon: const Icon(Icons.close, size: 18),
                onPressed: () => notifier.togglePanel(),
              ),
            ],
          ),
          if (state.error != null) ...[
            const SizedBox(height: 6),
            Text(state.error!, style: const TextStyle(color: TacticalColors.warning, fontSize: 11)),
          ],
          const SizedBox(height: 8),
          if (state.isLoading)
            const Center(child: Padding(padding: EdgeInsets.all(16), child: CircularProgressIndicator(strokeWidth: 2)))
          else if (active.isEmpty)
            Text(
              'No active SAR incidents.',
              style: Theme.of(context).textTheme.bodySmall?.copyWith(color: TacticalColors.textSecondary),
            )
          else
            Flexible(
              child: ListView.separated(
                shrinkWrap: true,
                itemCount: active.length,
                separatorBuilder: (_, __) => const SizedBox(height: 8),
                itemBuilder: (context, index) {
                  final incident = active[index];
                  return _IncidentCard(
                    incident: incident,
                    selectedDeviceId: selectedDeviceId,
                    onAssign: selectedDeviceId != null
                        ? () => notifier.assignDrone(incident.id, selectedDeviceId!)
                        : null,
                    onDispatchGrid: () => notifier.dispatchSarGrid(incident.id),
                    onResolve: () => notifier.resolveIncident(incident.id),
                    onCenter: onCenterIncident != null ? () => onCenterIncident!(incident) : null,
                  );
                },
              ),
            ),
        ],
      ),
    );
  }
}

String _shortId(String value) {
  if (value.length <= 8) return value;
  return '${value.substring(0, 8)}…';
}

class _IncidentCard extends StatelessWidget {
  const _IncidentCard({
    required this.incident,
    required this.selectedDeviceId,
    this.onAssign,
    this.onDispatchGrid,
    this.onResolve,
    this.onCenter,
  });

  final SarIncident incident;
  final String? selectedDeviceId;
  final VoidCallback? onAssign;
  final VoidCallback? onDispatchGrid;
  final VoidCallback? onResolve;
  final VoidCallback? onCenter;

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(10),
      decoration: BoxDecoration(
        color: TacticalColors.surfaceElevated.withOpacity(0.7),
        borderRadius: BorderRadius.circular(8),
        border: Border.all(color: TacticalColors.critical.withOpacity(0.35)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            incident.incidentType.label.toUpperCase(),
            style: const TextStyle(
              color: TacticalColors.critical,
              fontWeight: FontWeight.w800,
              fontSize: 11,
              letterSpacing: 0.5,
            ),
          ),
          if (incident.message != null) ...[
            const SizedBox(height: 4),
            Text(incident.message!, style: Theme.of(context).textTheme.bodySmall),
          ],
          const SizedBox(height: 4),
          Text(
            'Target: ${incident.targetLat.toStringAsFixed(5)}, ${incident.targetLon.toStringAsFixed(5)}',
            style: Theme.of(context).textTheme.labelSmall?.copyWith(color: TacticalColors.textSecondary),
          ),
          if (incident.assignedDeviceId != null) ...[
            const SizedBox(height: 2),
            Text(
              'Assigned: ${_shortId(incident.assignedDeviceId!)}',
              style: Theme.of(context).textTheme.labelSmall?.copyWith(color: TacticalColors.cyan),
            ),
          ],
          const SizedBox(height: 8),
          Wrap(
            spacing: 6,
            runSpacing: 6,
            children: [
              if (onCenter != null)
                _ActionChip(label: 'Center', icon: Icons.my_location, onTap: onCenter!),
              if (onAssign != null)
                _ActionChip(label: 'Assign Drone', icon: Icons.flight, onTap: onAssign!),
              if (onDispatchGrid != null)
                _ActionChip(label: 'SAR Grid', icon: Icons.grid_on, onTap: onDispatchGrid!),
              if (onResolve != null)
                _ActionChip(label: 'Resolve', icon: Icons.check_circle, onTap: onResolve!, accent: TacticalColors.success),
            ],
          ),
        ],
      ),
    );
  }
}

class _ActionChip extends StatelessWidget {
  const _ActionChip({
    required this.label,
    required this.icon,
    required this.onTap,
    this.accent,
  });

  final String label;
  final IconData icon;
  final VoidCallback onTap;
  final Color? accent;

  @override
  Widget build(BuildContext context) {
    final color = accent ?? TacticalColors.cyan;
    return ActionChip(
      label: Text(label, style: TextStyle(fontSize: 10, color: color)),
      avatar: Icon(icon, size: 14, color: color),
      onPressed: onTap,
      backgroundColor: color.withOpacity(0.12),
      side: BorderSide(color: color.withOpacity(0.4)),
    );
  }
}
