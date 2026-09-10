import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:next_iot_dashboard/features/map/models/signal_heatmap_models.dart';
import 'package:next_iot_dashboard/features/map/widgets/signal_heatmap_layer.dart';
import 'package:next_iot_dashboard/features/map/widgets/signal_heatmap_legend.dart';

void main() {
  final points = [
    SignalHeatmapPoint(
      lat: -6.2088,
      lon: 106.8456,
      rssi: -80,
      snr: 10,
      signalScore: 85,
      signalStrength: 'strong',
      recordedAt: DateTime(2026, 9, 10, 12),
    ),
    SignalHeatmapPoint(
      lat: -6.2095,
      lon: 106.8465,
      rssi: -95,
      snr: 7,
      signalScore: 60,
      signalStrength: 'marginal',
      recordedAt: DateTime(2026, 9, 10, 12, 5),
    ),
    SignalHeatmapPoint(
      lat: -6.2102,
      lon: 106.8472,
      rssi: -110,
      snr: 4,
      signalScore: 30,
      signalStrength: 'weak',
      recordedAt: DateTime(2026, 9, 10, 12, 10),
    ),
  ];

  testWidgets('SignalHeatmapLegend renders RSSI bands', (tester) async {
    await tester.pumpWidget(
      const MaterialApp(
        home: Scaffold(
          body: SignalHeatmapLegend(pointCount: 3, hours: 24),
        ),
      ),
    );
    await tester.pump();

    expect(find.text('RSSI / SNR LEGEND'), findsOneWidget);
    expect(find.textContaining('Strong'), findsOneWidget);
    expect(find.textContaining('Marginal'), findsOneWidget);
    expect(find.textContaining('Weak'), findsOneWidget);
    expect(find.text('3 samples · 24h window'), findsOneWidget);
  });

  test('SignalHeatmapLayer.buildMapLayers returns polyline and circle layers', () {
    final layers = SignalHeatmapLayer.buildMapLayers(points);
    expect(layers, hasLength(2));
  });

  test('SignalHeatmapLayer.buildMapLayers returns empty for no points', () {
    expect(SignalHeatmapLayer.buildMapLayers(const []), isEmpty);
  });
}
