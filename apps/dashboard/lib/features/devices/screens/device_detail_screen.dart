import 'dart:async';

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../core/theme/tactical_theme.dart';
import '../../../core/widgets/pill_tab_bar.dart';
import '../../../core/widgets/tactical_card.dart';
import '../../map/widgets/device_map_view.dart';
import '../../telemetry/models/telemetry_models.dart';
import '../../telemetry/providers/telemetry_analytics_provider.dart';
import '../../telemetry/providers/telemetry_provider.dart';
import '../../telemetry/widgets/metric_gauge_card.dart';
import '../../telemetry/widgets/tactical_indicator.dart';
import '../../telemetry/widgets/telemetry_analytics_card.dart';
import '../../telemetry/widgets/telemetry_export_dialog.dart';
import '../../telemetry/widgets/telemetry_line_chart.dart';
import '../models/device_models.dart';
import '../widgets/device_status_badge.dart';

class DeviceDetailScreen extends ConsumerStatefulWidget {
  const DeviceDetailScreen({
    super.key,
    required this.deviceId,
    this.device,
  });

  final String deviceId;
  final Device? device;

  @override
  ConsumerState<DeviceDetailScreen> createState() => _DeviceDetailScreenState();
}

class _DeviceDetailScreenState extends ConsumerState<DeviceDetailScreen> {
  Timer? _refreshTimer;

  @override
  void initState() {
    super.initState();
    Future.microtask(() => ref.read(telemetryProvider(widget.deviceId).notifier).load());
    _refreshTimer = Timer.periodic(const Duration(seconds: 15), (_) {
      ref.read(telemetryProvider(widget.deviceId).notifier).load();
    });
  }

  @override
  void dispose() {
    _refreshTimer?.cancel();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final telemetry = ref.watch(telemetryProvider(widget.deviceId));
    final device = widget.device;
    final title = device?.name ?? 'Device ${widget.deviceId.substring(0, 8)}';

    return Scaffold(
      backgroundColor: TacticalColors.background,
      appBar: AppBar(
        title: Text(title.toUpperCase()),
        actions: [
          IconButton(
            tooltip: 'Export Data',
            icon: const Icon(Icons.download),
            onPressed: () => TelemetryExportDialog.show(
              context,
              deviceId: widget.deviceId,
              deviceName: device?.name,
            ),
          ),
          if (device != null)
            Padding(
              padding: const EdgeInsets.only(right: 16),
              child: Center(child: DeviceStatusBadge(status: device.connectionStatus)),
            ),
        ],
      ),
      body: RefreshIndicator(
        onRefresh: () => ref.read(telemetryProvider(widget.deviceId).notifier).load(),
        child: ListView(
          padding: const EdgeInsets.all(20),
          children: [
            TacticalIndicator(
              latest: telemetry.latest,
              deviceName: title,
              deviceStatusLabel: device?.connectionStatus.label ?? 'UNKNOWN',
            ),
            if (device != null) ...[
              const SizedBox(height: 16),
              TacticalCard(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text('MAP TRACKING', style: Theme.of(context).textTheme.titleMedium),
                    const SizedBox(height: 12),
                    DeviceMapView(
                      device: device,
                      telemetry: telemetry.latest,
                      height: 340,
                    ),
                  ],
                ),
              ),
            ],
            const SizedBox(height: 16),
            if (telemetry.isLoading && telemetry.latest == null)
              const Center(child: Padding(padding: EdgeInsets.all(32), child: CircularProgressIndicator()))
            else if (telemetry.error != null && telemetry.latest == null)
              _ErrorBanner(
                message: telemetry.error!,
                onRetry: () => ref.read(telemetryProvider(widget.deviceId).notifier).load(),
              )
            else ...[
              _LiveMetricsSection(latest: telemetry.latest),
              const SizedBox(height: 16),
              _HistorySection(deviceId: widget.deviceId, state: telemetry),
            ],
          ],
        ),
      ),
    );
  }
}

class _LiveMetricsSection extends StatelessWidget {
  const _LiveMetricsSection({required this.latest});

  final TelemetryLatest? latest;

  @override
  Widget build(BuildContext context) {
    final metrics = latest?.metrics ?? {};
    if (metrics.isEmpty) {
      return const Text('No live metrics available.');
    }

    final gaugeDefs = resolveGaugeMetrics(metrics);

    return TacticalCard(
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text('LIVE GAUGES', style: Theme.of(context).textTheme.titleMedium),
          const SizedBox(height: 12),
          Wrap(
            spacing: 12,
            runSpacing: 12,
            children: gaugeDefs.map((def) {
              return SizedBox(
                width: 160,
                child: MetricGaugeCard(
                  definition: def,
                  value: metrics[def.key]!,
                ),
              );
            }).toList(),
          ),
        ],
      ),
    );
  }
}

class _HistorySection extends ConsumerStatefulWidget {
  const _HistorySection({required this.deviceId, required this.state});

  final String deviceId;
  final TelemetryState state;

  @override
  ConsumerState<_HistorySection> createState() => _HistorySectionState();
}

class _HistorySectionState extends ConsumerState<_HistorySection> {
  @override
  void initState() {
    super.initState();
    Future.microtask(
      () => ref.read(telemetryAnalyticsProvider(widget.deviceId).notifier).loadForTimeRange(widget.state.timeRange),
    );
  }

  @override
  void didUpdateWidget(covariant _HistorySection oldWidget) {
    super.didUpdateWidget(oldWidget);
    if (oldWidget.state.timeRange != widget.state.timeRange) {
      ref.read(telemetryAnalyticsProvider(widget.deviceId).notifier).loadForTimeRange(widget.state.timeRange);
    }
  }

  @override
  Widget build(BuildContext context) {
    final deviceId = widget.deviceId;
    final state = widget.state;
    final notifier = ref.read(telemetryProvider(deviceId).notifier);
    final analytics = ref.watch(telemetryAnalyticsProvider(deviceId));
    final chartDef = MetricDefinition.lookup(state.selectedChartMetric) ??
        MetricDefinition.custom(state.selectedChartMetric);

    return TacticalCard(
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text('TELEMETRY LOG PANEL', style: Theme.of(context).textTheme.titleMedium),
          const SizedBox(height: 12),
          TelemetryAnalyticsCard(
            analytics: analytics.data,
            isLoading: analytics.isLoading,
          ),
          const SizedBox(height: 12),
          PillTabBar<TelemetryTimeRange>(
            tabs: TelemetryTimeRange.values
                .map((r) => PillTab(value: r, label: r.label))
                .toList(),
            selected: state.timeRange,
            onSelected: (range) {
              notifier.setTimeRange(range);
              ref.read(telemetryAnalyticsProvider(deviceId).notifier).loadForTimeRange(range);
            },
          ),
          const SizedBox(height: 12),
          if (state.chartMetricOptions.isNotEmpty)
            DropdownButtonFormField<String>(
              value: state.selectedChartMetric,
              decoration: const InputDecoration(
                labelText: 'Chart metric',
              ),
              dropdownColor: TacticalColors.surfaceElevated,
              items: state.chartMetricOptions
                  .map((key) => DropdownMenuItem(
                        value: key,
                        child: Text(MetricDefinition.lookup(key)?.label ?? key),
                      ))
                  .toList(),
              onChanged: (value) {
                if (value != null) notifier.setChartMetric(value);
              },
            ),
          const SizedBox(height: 12),
          if (state.isLoading && state.history.isEmpty)
            const Center(child: CircularProgressIndicator())
          else
            TelemetryLineChart(
              history: state.chronologicalHistory,
              metricKey: state.selectedChartMetric,
              metricLabel: chartDef.label,
              unit: chartDef.unit,
            ),
        ],
      ),
    );
  }
}

class _ErrorBanner extends StatelessWidget {
  const _ErrorBanner({required this.message, required this.onRetry});

  final String message;
  final VoidCallback onRetry;

  @override
  Widget build(BuildContext context) {
    return TacticalCard(
      accentColor: TacticalColors.critical,
      child: Column(
        children: [
          Text(message, textAlign: TextAlign.center),
          const SizedBox(height: 12),
          FilledButton(onPressed: onRetry, child: const Text('Retry')),
        ],
      ),
    );
  }
}
