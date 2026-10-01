import 'package:fl_chart/fl_chart.dart';
import 'package:flutter/material.dart';
import 'package:intl/intl.dart';

import '../../../core/theme/tactical_theme.dart';
import '../models/telemetry_analytics_models.dart';

class TelemetryTimeseriesChart extends StatelessWidget {
  const TelemetryTimeseriesChart({
    super.key,
    required this.seriesList,
    this.height = 260,
  });

  final List<MetricTimeSeries> seriesList;
  final double height;

  static const _palette = [
    TacticalColors.cyan,
    TacticalColors.success,
    TacticalColors.warning,
    TacticalColors.info,
  ];

  @override
  Widget build(BuildContext context) {
    final active =
        seriesList.where((s) => s.points.isNotEmpty).toList(growable: false);
    if (active.isEmpty) {
      return SizedBox(
        height: height,
        child: const Center(child: Text('No bucketed data for selected metrics')),
      );
    }

    final maxLen = active.map((s) => s.points.length).reduce((a, b) => a > b ? a : b);
    double minY = double.infinity;
    double maxY = -double.infinity;
    for (final s in active) {
      for (final p in s.points) {
        final v = p.avg ?? p.max ?? p.min;
        if (v == null) continue;
        minY = v < minY ? v : minY;
        maxY = v > maxY ? v : maxY;
      }
    }
    if (!minY.isFinite || !maxY.isFinite) {
      minY = 0;
      maxY = 1;
    }
    final pad = ((maxY - minY).abs() * 0.12).clamp(0.5, 999.0);

    final bars = <LineChartBarData>[];
    for (var i = 0; i < active.length; i++) {
      final s = active[i];
      final spots = <FlSpot>[];
      for (var j = 0; j < s.points.length; j++) {
        final v = s.points[j].avg ?? s.points[j].max ?? s.points[j].min ?? 0;
        spots.add(FlSpot(j.toDouble(), v));
      }
      final color = _palette[i % _palette.length];
      bars.add(
        LineChartBarData(
          spots: spots,
          isCurved: true,
          color: color,
          barWidth: 2.4,
          dotData: const FlDotData(show: false),
          belowBarData: BarAreaData(show: false),
        ),
      );
    }

    final refPoints = active.first.points;

    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        Wrap(
          spacing: 12,
          children: [
            for (var i = 0; i < active.length; i++)
              Row(
                mainAxisSize: MainAxisSize.min,
                children: [
                  Container(
                    width: 10,
                    height: 10,
                    decoration: BoxDecoration(
                      color: _palette[i % _palette.length],
                      shape: BoxShape.circle,
                    ),
                  ),
                  const SizedBox(width: 6),
                  Text(active[i].metric),
                ],
              ),
          ],
        ),
        const SizedBox(height: 8),
        SizedBox(
          height: height,
          child: LineChart(
            LineChartData(
              minY: minY - pad,
              maxY: maxY + pad,
              lineTouchData: LineTouchData(
                touchTooltipData: LineTouchTooltipData(
                  getTooltipItems: (spots) => spots
                      .map(
                        (s) => LineTooltipItem(
                          active[s.barIndex].metric +
                              '\n${s.y.toStringAsFixed(2)}',
                          const TextStyle(color: Colors.white, fontSize: 11),
                        ),
                      )
                      .toList(),
                ),
              ),
              gridData: FlGridData(show: true, drawVerticalLine: false),
              titlesData: FlTitlesData(
                topTitles: const AxisTitles(sideTitles: SideTitles(showTitles: false)),
                rightTitles: const AxisTitles(sideTitles: SideTitles(showTitles: false)),
                leftTitles: AxisTitles(
                  sideTitles: SideTitles(
                    showTitles: true,
                    reservedSize: 42,
                    getTitlesWidget: (value, meta) => Text(
                      value.toStringAsFixed(0),
                      style: const TextStyle(fontSize: 10),
                    ),
                  ),
                ),
                bottomTitles: AxisTitles(
                  sideTitles: SideTitles(
                    showTitles: true,
                    reservedSize: 28,
                    interval: (maxLen / 4).clamp(1, maxLen).toDouble(),
                    getTitlesWidget: (value, meta) {
                      final index = value.toInt();
                      if (index < 0 || index >= refPoints.length) {
                        return const SizedBox.shrink();
                      }
                      final label = DateFormat('MM/dd HH:mm')
                          .format(refPoints[index].bucketStart.toLocal());
                      return Padding(
                        padding: const EdgeInsets.only(top: 6),
                        child: Text(label, style: const TextStyle(fontSize: 9)),
                      );
                    },
                  ),
                ),
              ),
              borderData: FlBorderData(show: true),
              lineBarsData: bars,
            ),
          ),
        ),
      ],
    );
  }
}
