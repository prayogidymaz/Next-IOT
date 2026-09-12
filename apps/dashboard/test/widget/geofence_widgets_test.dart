import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:next_iot_dashboard/features/map/widgets/geofence_breach_warning.dart';
import 'package:next_iot_dashboard/features/map/widgets/geofence_layer.dart';
import 'package:next_iot_dashboard/features/mission/models/geofence_models.dart';

void main() {
  final sampleZones = [
    GeofenceZone(
      id: 'zone-1',
      tenantId: 'tenant-1',
      name: 'No-Fly Alpha',
      polygonCoords: const [
        GeofencePoint(lat: -6.2100, lon: 106.8440),
        GeofencePoint(lat: -6.2100, lon: 106.8460),
        GeofencePoint(lat: -6.2080, lon: 106.8460),
        GeofencePoint(lat: -6.2080, lon: 106.8440),
      ],
      maxAltitude: 120,
      minAltitude: 0,
      actionOnBreach: GeofenceAction.warn,
    ),
  ];

  test('GeofenceLayer.buildMapLayers returns polygon layer for zones', () {
    final layers = GeofenceLayer.buildMapLayers(sampleZones);
    expect(layers.length, 1);
  });

  test('GeofenceLayer.buildMapLayers empty for no zones', () {
    expect(GeofenceLayer.buildMapLayers(const []), isEmpty);
  });

  testWidgets('GeofenceBreachWarning shows breach warning text', (tester) async {
    await tester.pumpWidget(
      const MaterialApp(
        home: Scaffold(
          body: GeofenceBreachWarning(),
        ),
      ),
    );
    await tester.pump();

    expect(find.text('GEOFENCE BREACH WARNING'), findsOneWidget);
    expect(find.text('Drone entered forbidden zone'), findsOneWidget);
    expect(find.byIcon(Icons.fence), findsOneWidget);
  });

  testWidgets('GeofenceBreachWarning compact mode shows short label', (tester) async {
    await tester.pumpWidget(
      const MaterialApp(
        home: Scaffold(
          body: GeofenceBreachWarning(compact: true),
        ),
      ),
    );
    await tester.pump();

    expect(find.text('GEOFENCE BREACH'), findsOneWidget);
  });
}
