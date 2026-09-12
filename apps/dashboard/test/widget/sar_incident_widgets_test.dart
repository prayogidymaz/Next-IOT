import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:next_iot_dashboard/features/map/widgets/incident_target_marker.dart';
import 'package:next_iot_dashboard/features/mission/data/sar_incident_repository.dart';
import 'package:next_iot_dashboard/features/mission/models/sar_incident_models.dart';
import 'package:next_iot_dashboard/features/mission/providers/sar_incident_provider.dart';
import 'package:next_iot_dashboard/features/mission/widgets/sar_incident_response_panel.dart';

class _TestSarIncidentNotifier extends SarIncidentNotifier {
  _TestSarIncidentNotifier(Ref ref, SarIncidentState initial)
      : super(SarIncidentRepository(), ref) {
    state = initial;
  }

  @override
  Future<void> togglePanel() async {}
}

void main() {
  final sampleIncident = SarIncident(
    id: 'inc-1',
    tenantId: 'tenant-1',
    incidentType: SarIncidentType.personLost,
    status: SarIncidentStatus.active,
    targetLat: -6.209,
    targetLon: 106.845,
    severity: 'critical',
    message: 'Missing person detected by AI',
    assignedDeviceId: 'dev-1',
  );

  testWidgets('IncidentTargetMarker shows incident type label', (tester) async {
    await tester.pumpWidget(
      MaterialApp(
        home: Scaffold(
          body: IncidentTargetMarker(incident: sampleIncident),
        ),
      ),
    );
    await tester.pump();

    expect(find.text('PERSON LOST'), findsOneWidget);
    expect(find.byIcon(Icons.person_search), findsOneWidget);
  });

  testWidgets('IncidentTargetMarker shows vehicle crash styling', (tester) async {
    final vehicle = SarIncident(
      id: 'inc-2',
      tenantId: 'tenant-1',
      incidentType: SarIncidentType.vehicleCrash,
      status: SarIncidentStatus.active,
      targetLat: -6.2,
      targetLon: 106.8,
      severity: 'critical',
    );

    await tester.pumpWidget(
      MaterialApp(
        home: Scaffold(
          body: IncidentTargetMarker(incident: vehicle, isSelected: true),
        ),
      ),
    );
    await tester.pump();

    expect(find.text('VEHICLE CRASH'), findsOneWidget);
    expect(find.byIcon(Icons.car_crash), findsOneWidget);
  });

  testWidgets('SarIncidentResponsePanel lists active incidents and actions', (tester) async {
    await tester.pumpWidget(
      ProviderScope(
        overrides: [
          sarIncidentProvider.overrideWith(
            (ref) => _TestSarIncidentNotifier(
              ref,
              SarIncidentState(
                panelOpen: true,
                incidents: [sampleIncident],
              ),
            ),
          ),
        ],
        child: const MaterialApp(
          home: Scaffold(
            body: SizedBox(
              height: 420,
              width: 360,
              child: SarIncidentResponsePanel(selectedDeviceId: 'dev-1'),
            ),
          ),
        ),
      ),
    );
    await tester.pump();

    expect(find.text('SAR INCIDENT RESPONSE'), findsOneWidget);
    expect(find.text('Missing person detected by AI'), findsOneWidget);
    expect(find.text('Assign Drone'), findsOneWidget);
    expect(find.text('SAR Grid'), findsOneWidget);
    expect(find.text('Resolve'), findsOneWidget);
  });
}
