import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:next_iot_dashboard/features/map/models/weather_vector_models.dart';
import 'package:next_iot_dashboard/features/map/widgets/flight_safety_weather_card.dart';
import 'package:next_iot_dashboard/features/map/widgets/wind_vector_overlay.dart';

void main() {
  final sampleData = WeatherVectorData(
    lat: -6.2088,
    lon: 106.8456,
    radiusM: 1500,
    windSpeedMs: 12.5,
    windDirectionDeg: 90,
    visibilityM: 5000,
    rainRateMmH: 2.0,
    flightSafetyStatus: FlightSafetyStatus.caution,
    vectors: const [
      WindVectorPoint(lat: -6.2088, lon: 106.8456, windSpeedMs: 12.5, windDirectionDeg: 90),
      WindVectorPoint(lat: -6.2095, lon: 106.8465, windSpeedMs: 16.0, windDirectionDeg: 180),
    ],
  );

  test('WindVectorOverlay.buildMapLayers returns polyline and marker layers', () {
    final layers = WindVectorOverlay.buildMapLayers(sampleData.vectors);
    expect(layers.length, greaterThanOrEqualTo(2));
  });

  test('WindVectorOverlay.buildMapLayers empty for no vectors', () {
    expect(WindVectorOverlay.buildMapLayers(const []), isEmpty);
  });

  testWidgets('FlightSafetyWeatherCard shows caution status', (tester) async {
    await tester.pumpWidget(
      MaterialApp(
        home: Scaffold(
          body: FlightSafetyWeatherCard(data: sampleData),
        ),
      ),
    );
    await tester.pump();

    expect(find.text('FLIGHT SAFETY & WEATHER'), findsOneWidget);
    expect(find.text('CAUTION'), findsOneWidget);
    expect(find.textContaining('12.5 m/s'), findsOneWidget);
  });

  testWidgets('FlightSafetyWeatherCard shows no-fly hazard styling', (tester) async {
    final noFly = WeatherVectorData(
      lat: -6.2,
      lon: 106.8,
      radiusM: 1000,
      windSpeedMs: 18,
      windDirectionDeg: 45,
      visibilityM: 2000,
      rainRateMmH: 12,
      flightSafetyStatus: FlightSafetyStatus.noFly,
      vectors: const [],
    );

    await tester.pumpWidget(
      MaterialApp(
        home: Scaffold(
          body: FlightSafetyWeatherCard(data: noFly, compact: true),
        ),
      ),
    );
    await tester.pump();

    expect(find.text('NO-FLY HAZARD'), findsOneWidget);
    expect(find.byIcon(Icons.block), findsOneWidget);
  });
}
