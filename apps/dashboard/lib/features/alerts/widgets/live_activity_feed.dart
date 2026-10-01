import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:intl/intl.dart';

import '../../../core/theme/tactical_theme.dart';
import '../../../core/widgets/tactical_card.dart';
import '../models/alert_models.dart';
import '../providers/alert_provider.dart';
import 'severity_badge.dart';

class LiveActivityFeed extends ConsumerWidget {
  const LiveActivityFeed({super.key});

  List<DeviceAlert> _sortedEvents(WidgetRef ref) {
    final state = ref.watch(alertProvider);
    final merged = [...state.activeAlerts, ...state.historyAlerts];
    merged.sort((a, b) {
      final ta = a.timestamp ?? DateTime.fromMillisecondsSinceEpoch(0);
      final tb = b.timestamp ?? DateTime.fromMillisecondsSinceEpoch(0);
      return tb.compareTo(ta);
    });
    return merged;
  }

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final state = ref.watch(alertProvider);
    final events = _sortedEvents(ref);
    final timeFmt = DateFormat('HH:mm:ss · MMM d');

    return TacticalCard(
      accentColor: TacticalColors.warning,
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          Row(
            children: [
              const Icon(Icons.stream, color: TacticalColors.warning, size: 20),
              const SizedBox(width: 8),
              Expanded(
                child: Text('Live Activity Feed',
                    style: Theme.of(context).textTheme.titleMedium),
              ),
              if (state.activeCount > 0)
                Container(
                  padding:
                      const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                  decoration: BoxDecoration(
                    color: TacticalColors.critical.withOpacity(0.15),
                    borderRadius: BorderRadius.circular(999),
                    border: Border.all(
                        color: TacticalColors.critical.withOpacity(0.45)),
                  ),
                  child: Text(
                    '${state.activeCount} active',
                    style: Theme.of(context).textTheme.labelSmall?.copyWith(
                          color: TacticalColors.critical,
                          fontWeight: FontWeight.w700,
                        ),
                  ),
                ),
            ],
          ),
          const SizedBox(height: 12),
          if (state.isLoading && events.isEmpty)
            const Center(
              child: Padding(
                padding: EdgeInsets.all(24),
                child: CircularProgressIndicator(),
              ),
            )
          else if (events.isEmpty)
            Padding(
              padding: const EdgeInsets.symmetric(vertical: 24),
              child: Text(
                'No alert events yet. Rules will stream here when triggered.',
                style: Theme.of(context)
                    .textTheme
                    .bodySmall
                    ?.copyWith(color: TacticalColors.textSecondary),
              ),
            )
          else
            Expanded(
              child: ListView.separated(
                itemCount: events.length,
                separatorBuilder: (_, __) => const SizedBox(height: 8),
                itemBuilder: (context, index) {
                  final alert = events[index];
                  return _FeedItem(
                    alert: alert,
                    timeLabel: alert.timestamp != null
                        ? timeFmt.format(alert.timestamp!.toLocal())
                        : '—',
                  );
                },
              ),
            ),
        ],
      ),
    );
  }
}

class _FeedItem extends StatelessWidget {
  const _FeedItem({required this.alert, required this.timeLabel});

  final DeviceAlert alert;
  final String timeLabel;

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(10),
      decoration: BoxDecoration(
        color: TacticalColors.background.withOpacity(0.55),
        borderRadius: BorderRadius.circular(8),
        border: Border.all(color: TacticalColors.border),
      ),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          SeverityBadge(severity: alert.severity),
          const SizedBox(width: 10),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  alert.metric ?? alert.event,
                  style: Theme.of(context)
                      .textTheme
                      .bodyMedium
                      ?.copyWith(fontWeight: FontWeight.w600),
                ),
                const SizedBox(height: 2),
                Text(alert.summary,
                    style: Theme.of(context).textTheme.bodySmall),
                const SizedBox(height: 4),
                Text(
                  'Device ${_shortId(alert.deviceId)} · ${alert.notificationChannel ?? alert.actionType ?? '—'} · $timeLabel',
                  style: Theme.of(context).textTheme.bodySmall?.copyWith(
                        color: TacticalColors.textSecondary,
                        fontSize: 11,
                      ),
                ),
              ],
            ),
          ),
          Icon(
            alert.isActive ? Icons.fiber_manual_record : Icons.check,
            size: alert.isActive ? 10 : 16,
            color: alert.isActive
                ? TacticalColors.critical
                : TacticalColors.textSecondary,
          ),
        ],
      ),
    );
  }
}

String _shortId(String id) {
  if (id.length <= 8) return id;
  return '${id.substring(0, 8)}…';
}
