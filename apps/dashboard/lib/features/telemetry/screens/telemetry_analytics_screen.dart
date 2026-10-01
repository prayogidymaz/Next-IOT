import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../../core/theme/tactical_theme.dart';
import '../../../core/widgets/pill_tab_bar.dart';
import '../../../core/widgets/tactical_card.dart';
import '../../../core/widgets/tactical_shell.dart';
import '../../../routing/navigation_config.dart';
import '../../auth/providers/auth_provider.dart';
import '../../devices/providers/device_provider.dart';
import '../data/telemetry_repository.dart';
import '../models/telemetry_analytics_models.dart';
import '../models/telemetry_models.dart';
import '../providers/telemetry_analytics_provider.dart';
import '../providers/telemetry_provider.dart';
import '../widgets/telemetry_export_dialog.dart';
import '../widgets/telemetry_metric_summary_cards.dart';
import '../widgets/telemetry_timeseries_chart.dart';

class TelemetryAnalyticsScreen extends ConsumerStatefulWidget {
  const TelemetryAnalyticsScreen({super.key, this.initialDeviceId});

  final String? initialDeviceId;

  @override
  ConsumerState<TelemetryAnalyticsScreen> createState() =>
      _TelemetryAnalyticsScreenState();
}

class _TelemetryAnalyticsScreenState extends ConsumerState<TelemetryAnalyticsScreen> {
  String? _deviceId;
  String _primaryMetric = 'temperature';
  bool _exporting = false;

  @override
  void initState() {
    super.initState();
    _deviceId = widget.initialDeviceId;
    Future.microtask(() async {
      await ref.read(deviceProvider.notifier).loadDevices();
      if (_deviceId == null) {
        final devices = ref.read(deviceProvider).devices;
        if (devices.isNotEmpty) _deviceId = devices.first.id;
      }
      await _reload();
    });
  }

  Future<void> _reload() async {
    final id = _deviceId;
    if (id == null) return;
    await ref.read(telemetryAnalyticsProvider(id).notifier).load(
          metrics: [_primaryMetric],
        );
  }

  Future<void> _exportCsv() async {
    final id = _deviceId;
    if (id == null) return;
    setState(() => _exporting = true);
    try {
      final state = ref.read(telemetryAnalyticsProvider(id));
      final range = state.timeRange;
      final (start, end) = range.window(
        customStart: state.customStart,
        customEnd: state.customEnd,
      );
      await ref.read(telemetryRepositoryProvider).downloadExport(
            deviceId: id,
            format: TelemetryExportFormat.csv,
            startTime: start,
            endTime: end,
          );
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('CSV export saved')),
        );
      }
    } catch (_) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('CSV export failed')),
        );
      }
    } finally {
      if (mounted) setState(() => _exporting = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    final auth = ref.watch(authProvider);
    final devices = ref.watch(deviceProvider).devices;
    final deviceId = _deviceId;
    final analyticsState =
        deviceId != null ? ref.watch(telemetryAnalyticsProvider(deviceId)) : null;

    return TacticalShell(
      section: TacticalNavSection.devices,
      onSectionChanged: (s) {
        switch (s) {
          case TacticalNavSection.devices:
            context.go(AppRoutes.dashboard);
          case TacticalNavSection.mapView:
            context.go('${AppRoutes.dashboard}?tab=map');
          case TacticalNavSection.alerts:
            context.go(AppRoutes.alerts);
        }
      },
      onOpenStudio: () => context.go(AppRoutes.studio),
      subtitle: auth.user?.email,
      body: Padding(
        padding: const EdgeInsets.all(24),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            Text('Time-Series Analytics',
                style: Theme.of(context).textTheme.headlineSmall),
            const SizedBox(height: 16),
            if (devices.isEmpty)
              const Text('No devices available.')
            else ...[
              DropdownButtonFormField<String>(
                value: deviceId,
                decoration: const InputDecoration(labelText: 'Device'),
                items: devices
                    .map((d) => DropdownMenuItem(value: d.id, child: Text(d.name)))
                    .toList(),
                onChanged: (v) async {
                  setState(() => _deviceId = v);
                  await _reload();
                },
              ),
              const SizedBox(height: 12),
              if (analyticsState != null && deviceId != null)
                PillTabBar<TelemetryTimeRange>(
                  tabs: TelemetryTimeRange.values
                      .map((r) => PillTab(value: r, label: r.label))
                      .toList(),
                  selected: analyticsState.timeRange,
                  onSelected: (range) {
                    ref
                        .read(telemetryAnalyticsProvider(deviceId).notifier)
                        .loadForTimeRange(range);
                  },
                ),
              const SizedBox(height: 12),
              Row(
                children: [
                  FilledButton.icon(
                    onPressed: _exporting ? null : _exportCsv,
                    icon: _exporting
                        ? const SizedBox(
                            width: 16,
                            height: 16,
                            child: CircularProgressIndicator(strokeWidth: 2),
                          )
                        : const Icon(Icons.download_outlined, size: 18),
                    label: Text(_exporting ? 'Exporting CSV…' : 'Export CSV Data'),
                  ),
                  const SizedBox(width: 8),
                  OutlinedButton(
                    onPressed: deviceId == null
                        ? null
                        : () => TelemetryExportDialog.show(
                              context,
                              deviceId: deviceId,
                            ),
                    child: const Text('Advanced export'),
                  ),
                ],
              ),
              const SizedBox(height: 16),
              if (analyticsState?.isLoading == true)
                const Center(child: CircularProgressIndicator())
              else if (analyticsState?.data != null) ...[
                TelemetryMetricSummaryCards(
                  series: analyticsState!.data!.seriesFor(_primaryMetric),
                  metricKey: _primaryMetric,
                ),
                const SizedBox(height: 16),
                TacticalCard(
                  child: Padding(
                    padding: const EdgeInsets.all(12),
                    child: TelemetryTimeseriesChart(
                      seriesList: analyticsState.data!.series,
                    ),
                  ),
                ),
              ],
            ],
          ],
        ),
      ),
    );
  }
}
