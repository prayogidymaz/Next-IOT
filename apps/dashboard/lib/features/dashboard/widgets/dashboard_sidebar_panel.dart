import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:intl/intl.dart';

import '../../../core/theme/tactical_theme.dart';
import '../../alerts/providers/alert_provider.dart';
import '../../alerts/widgets/severity_badge.dart';
import '../../devices/widgets/device_iot_glossary_dialog.dart';
import '../../devices/widgets/register_device_dialog.dart';
import 'bento_compact_surface.dart';

class DashboardSidebarPanel extends ConsumerWidget {
  const DashboardSidebarPanel({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final alertState = ref.watch(alertProvider);
    final events = [
      ...alertState.activeAlerts,
      ...alertState.historyAlerts,
    ]..sort((a, b) {
        final ta = a.timestamp ?? DateTime.fromMillisecondsSinceEpoch(0);
        final tb = b.timestamp ?? DateTime.fromMillisecondsSinceEpoch(0);
        return tb.compareTo(ta);
      });
    final timeFmt = DateFormat('HH:mm');
    final now = DateTime.now();

    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        BentoCompactSurface(
          height: 118,
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text('Timeline', style: Theme.of(context).textTheme.titleSmall),
              const SizedBox(height: 8),
              Text(
                DateFormat('EEE, MMM d').format(now),
                style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                      color: TacticalColors.textPrimary,
                    ),
              ),
              const SizedBox(height: 8),
              Row(
                children: List.generate(5, (i) {
                  final day = now.subtract(Duration(days: 2 - i));
                  final isToday = day.day == now.day;
                  return Expanded(
                    child: Container(
                      margin: EdgeInsets.only(right: i == 4 ? 0 : 4),
                      padding: const EdgeInsets.symmetric(vertical: 6),
                      decoration: BoxDecoration(
                        color: isToday
                            ? TacticalColors.success.withOpacity(0.14)
                            : TacticalColors.surface,
                        borderRadius: BorderRadius.circular(10),
                        border: Border.all(
                          color: isToday
                              ? TacticalColors.success.withOpacity(0.4)
                              : TacticalColors.border,
                        ),
                      ),
                      child: Text(
                        DateFormat('d').format(day),
                        textAlign: TextAlign.center,
                        style: Theme.of(context).textTheme.labelSmall?.copyWith(
                              fontWeight:
                                  isToday ? FontWeight.w700 : FontWeight.w500,
                            ),
                      ),
                    ),
                  );
                }),
              ),
            ],
          ),
        ),
        const SizedBox(height: 10),
        BentoCompactSurface(
          height: 148,
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              Text('Quick actions',
                  style: Theme.of(context).textTheme.titleSmall),
              const SizedBox(height: 8),
              FilledButton.icon(
                style: FilledButton.styleFrom(
                  visualDensity: VisualDensity.compact,
                  padding: const EdgeInsets.symmetric(vertical: 10),
                ),
                onPressed: () => showRegisterDeviceDialog(context, ref),
                icon: const Icon(Icons.add_link, size: 18),
                label: const Text('Register device'),
              ),
              const SizedBox(height: 6),
              OutlinedButton.icon(
                key: const Key('device-iot-glossary-button'),
                style: OutlinedButton.styleFrom(
                  visualDensity: VisualDensity.compact,
                  padding: const EdgeInsets.symmetric(vertical: 10),
                ),
                onPressed: () => DeviceIotGlossaryDialog.show(context),
                icon: const Icon(Icons.menu_book_outlined, size: 16),
                label: const Text('Kamus Istilah IoT'),
              ),
            ],
          ),
        ),
        const SizedBox(height: 10),
        Expanded(
          child: BentoCompactSurface(
            padding: const EdgeInsets.all(12),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                Row(
                  children: [
                    Text('Alert feed',
                        style: Theme.of(context).textTheme.titleSmall),
                    const Spacer(),
                    if (alertState.activeCount > 0)
                      Container(
                        padding: const EdgeInsets.symmetric(
                            horizontal: 8, vertical: 3),
                        decoration: BoxDecoration(
                          color: TacticalColors.critical.withOpacity(0.12),
                          borderRadius:
                              BorderRadius.circular(BentoTokens.radiusPill),
                        ),
                        child: Text(
                          '${alertState.activeCount}',
                          style: Theme.of(context).textTheme.labelSmall?.copyWith(
                                color: TacticalColors.critical,
                                fontWeight: FontWeight.w700,
                              ),
                        ),
                      ),
                  ],
                ),
                const SizedBox(height: 8),
                Expanded(
                  child: events.isEmpty
                      ? Center(
                          child: Text(
                            'No recent alerts.',
                            style: Theme.of(context).textTheme.bodySmall,
                          ),
                        )
                      : ListView.separated(
                          itemCount: events.take(12).length,
                          separatorBuilder: (_, __) =>
                              const SizedBox(height: 6),
                          itemBuilder: (context, index) {
                            final e = events[index];
                            return Row(
                              crossAxisAlignment: CrossAxisAlignment.start,
                              children: [
                                SeverityBadge(severity: e.severity),
                                const SizedBox(width: 8),
                                Expanded(
                                  child: Column(
                                    crossAxisAlignment:
                                        CrossAxisAlignment.start,
                                    children: [
                                      Text(
                                        e.summary,
                                        maxLines: 2,
                                        overflow: TextOverflow.ellipsis,
                                        style: Theme.of(context)
                                            .textTheme
                                            .bodySmall
                                            ?.copyWith(
                                              color: TacticalColors.textPrimary,
                                            ),
                                      ),
                                      if (e.timestamp != null)
                                        Text(
                                          timeFmt.format(
                                              e.timestamp!.toLocal()),
                                          style: Theme.of(context)
                                              .textTheme
                                              .labelSmall,
                                        ),
                                    ],
                                  ),
                                ),
                              ],
                            );
                          },
                        ),
                ),
              ],
            ),
          ),
        ),
      ],
    );
  }
}
