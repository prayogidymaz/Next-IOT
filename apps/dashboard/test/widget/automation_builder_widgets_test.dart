import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:next_iot_dashboard/core/theme/tactical_theme.dart';
import 'package:next_iot_dashboard/features/auth/data/permissions_repository.dart';
import 'package:next_iot_dashboard/features/auth/providers/permissions_provider.dart';
import 'package:next_iot_dashboard/features/automation/models/automation_pipeline_models.dart';
import 'package:next_iot_dashboard/features/automation/providers/automation_builder_provider.dart';
import 'package:next_iot_dashboard/features/automation/providers/palette_placement_provider.dart';
import 'package:next_iot_dashboard/features/automation/screens/automation_builder_screen.dart';
import 'package:next_iot_dashboard/features/automation/widgets/canvas_drop_registrar.dart';
import 'package:next_iot_dashboard/features/automation/widgets/dry_run_log_panel.dart';
import 'package:next_iot_dashboard/features/automation/widgets/node_config_dialog.dart';
import 'package:next_iot_dashboard/features/automation/widgets/node_palette.dart';
import 'package:next_iot_dashboard/features/automation/widgets/pipeline_canvas.dart';
import 'package:next_iot_dashboard/features/automation/widgets/pipeline_node_widget.dart';

ProviderScope automationTestScope({required Widget child}) {
  return ProviderScope(
    overrides: [
      permissionsProvider.overrideWith(
        (ref) => fullAccessPermissionsNotifier(
          ref.watch(permissionsRepositoryProvider),
        ),
      ),
    ],
    child: child,
  );
}

void main() {
  Future<void> useLargeSurface(WidgetTester tester) async {
    await tester.binding.setSurfaceSize(const Size(1440, 900));
    addTearDown(() => tester.binding.setSurfaceSize(null));
  }

  testWidgets('NodePalette renders TRIGGER, CONDITION, and ACTION sections',
      (tester) async {
    await useLargeSurface(tester);
    await tester.pumpWidget(
      automationTestScope(
        child: MaterialApp(
          home: Scaffold(body: NodePalette()),
        ),
      ),
    );

    expect(find.text('NODE PALETTE'), findsOneWidget);
    expect(find.text('TRIGGER'), findsOneWidget);
    expect(find.text('CONDITION'), findsOneWidget);
    expect(find.text('ACTION'), findsOneWidget);
    expect(find.text('AI Detection'), findsOneWidget);
    expect(find.text('Click item to select · click canvas to place'),
        findsOneWidget);
    expect(find.byIcon(Icons.add_circle_outline), findsWidgets);
    expect(find.byType(Draggable), findsNothing);
    expect(find.byType(DragTarget), findsNothing);
  });

  testWidgets('Click palette item enters placement mode', (tester) async {
    await useLargeSurface(tester);
    await tester.pumpWidget(
      automationTestScope(
        child: MaterialApp(
          theme: buildTacticalTheme(),
          home: const AutomationBuilderScreen(),
        ),
      ),
    );
    await tester.pump();

    final container = ProviderScope.containerOf(
      tester.element(find.byType(AutomationBuilderScreen)),
    );

    await tester.tap(find.text('AI Detection'));
    await tester.pump();

    expect(container.read(palettePlacementProvider).isActive, isTrue);
    expect(container.read(palettePlacementProvider).label, 'AI Detection');
    expect(find.textContaining('Placement mode'), findsOneWidget);
  });

  testWidgets('Click-to-select then click canvas places node', (tester) async {
    await useLargeSurface(tester);
    await tester.pumpWidget(
      automationTestScope(
        child: MaterialApp(
          theme: buildTacticalTheme(),
          home: const AutomationBuilderScreen(),
        ),
      ),
    );
    await tester.pumpAndSettle();

    final container = ProviderScope.containerOf(
      tester.element(find.byType(AutomationBuilderScreen)),
    );

    await tester.tap(find.text('AI Detection'));
    await tester.pump();

    await tester.tap(find.byType(PipelineCanvas));
    await tester.pump();
    await tester.pump();

    expect(container.read(automationBuilderProvider).nodes, hasLength(1));
    expect(container.read(palettePlacementProvider).isActive, isFalse);
    final placed = container.read(automationBuilderProvider).nodes.first;
    expect(placed.position,
        isNot(AutomationBuilderNotifier.firstNodeSpawnPosition));
    expect(
      find.descendant(
        of: find.byType(PipelineCanvas),
        matching: find.text('AI Detection'),
      ),
      findsOneWidget,
    );
    expect(find.byKey(const Key('pipeline-node-body')), findsOneWidget);
  });

  testWidgets('Escape cancels placement mode without adding node',
      (tester) async {
    await useLargeSurface(tester);
    await tester.pumpWidget(
      automationTestScope(
        child: MaterialApp(
          theme: buildTacticalTheme(),
          home: const AutomationBuilderScreen(),
        ),
      ),
    );
    await tester.pump();

    final container = ProviderScope.containerOf(
      tester.element(find.byType(AutomationBuilderScreen)),
    );

    await tester.tap(find.text('Geofence Breach'));
    await tester.pump();
    expect(container.read(palettePlacementProvider).isActive, isTrue);

    await tester.sendKeyEvent(LogicalKeyboardKey.escape);
    await tester.pump();

    expect(container.read(palettePlacementProvider).isActive, isFalse);
    expect(container.read(automationBuilderProvider).nodes, isEmpty);
  });

  test('TransformationController.toScene inverts viewport scale', () {
    final controller = TransformationController(Matrix4.identity()..scale(2.0));
    expect(controller.toScene(const Offset(200, 100)), const Offset(100, 50));
  });

  testWidgets('PipelineCanvas renders placed nodes', (tester) async {
    final node = PipelineNodeModel(
      id: 't1',
      type: PipelineNodeType.trigger,
      subtype: TriggerSubtype.weatherHazard.apiValue,
      position: const Offset(120, 80),
    );

    await tester.pumpWidget(
      ProviderScope(
        overrides: [
          automationBuilderProvider.overrideWith(
            (ref) => AutomationBuilderNotifier(
                ref.watch(automationRepositoryProvider))
              ..state = AutomationBuilderState(nodes: [node]),
          ),
        ],
        child: MaterialApp(
          theme: buildTacticalTheme(),
          home: const Scaffold(body: PipelineCanvas()),
        ),
      ),
    );
    await tester.pump();

    expect(find.text('Weather Hazard'), findsOneWidget);
    expect(find.text('TRIGGER'), findsOneWidget);
  });

  testWidgets('PipelineNodeWidget shows input/output ports and delete control',
      (tester) async {
    const node = PipelineNodeModel(
      id: 'c1',
      type: PipelineNodeType.condition,
      subtype: 'WIND_SPEED_LESS_THAN',
      position: Offset.zero,
    );

    await tester.pumpWidget(
      MaterialApp(
        theme: buildTacticalTheme(),
        home: Scaffold(
          body: Center(
            child: PipelineNodeWidget(
              node: node,
              selected: false,
              connecting: false,
              onDelete: () {},
              onConfigure: () {},
              onDragDelta: (_) {},
              onPortTap: (_) {},
              onSelect: () {},
            ),
          ),
        ),
      ),
    );

    expect(find.text('Wind Speed <'), findsOneWidget);
    expect(find.byIcon(Icons.close), findsOneWidget);
    expect(find.byIcon(Icons.filter_alt), findsOneWidget);
    expect(find.byKey(const Key('pipeline-port-left-c1')), findsOneWidget);
    expect(find.byKey(const Key('pipeline-port-top-c1')), findsOneWidget);
    expect(find.byKey(const Key('pipeline-port-bottom-c1')), findsOneWidget);
    expect(find.byKey(const Key('pipeline-port-right-c1')), findsOneWidget);
  });

  testWidgets('NodeConfigDialog renders subtype-specific fields',
      (tester) async {
    const node = PipelineNodeModel(
      id: 'a1',
      type: PipelineNodeType.action,
      subtype: 'MAVLINK_RTL',
      config: {'device_id': 'drone-1'},
    );

    await tester.pumpWidget(
      MaterialApp(
        theme: buildTacticalTheme(),
        home: Scaffold(
          body: Builder(
            builder: (context) {
              return ElevatedButton(
                onPressed: () => NodeConfigDialog.show(
                  context,
                  node: node,
                  onSave: (_) {},
                ),
                child: const Text('Open'),
              );
            },
          ),
        ),
      ),
    );

    await tester.tap(find.text('Open'));
    await tester.pumpAndSettle();

    expect(find.text('Configure MAVLink RTL'), findsOneWidget);
    expect(find.text('Target device ID'), findsOneWidget);
    expect(find.text('Save'), findsOneWidget);
  });

  testWidgets(
      'AutomationBuilderScreen renders palette, canvas toolbar, and collapsible dry-run sidebar',
      (tester) async {
    await useLargeSurface(tester);
    await tester.pumpWidget(
      automationTestScope(
        child: MaterialApp(
          theme: buildTacticalTheme(),
          home: const AutomationBuilderScreen(),
        ),
      ),
    );
    await tester.pump();

    expect(find.text('Automation Studio'), findsOneWidget);
    expect(find.text('Save & Deploy Pipeline'), findsOneWidget);
    expect(find.text('Clear Canvas'), findsOneWidget);
    expect(find.text('Dry-Run Test'), findsOneWidget);
    expect(find.text('Dry-run execution log will appear here.'), findsNothing);

    await tester.tap(find.text('AI Detection'));
    await tester.pump();
    await tester.tap(find.byType(PipelineCanvas));
    await tester.pump();

    await tester.tap(find.text('Dry-Run Test'));
    await tester.pump();
    await tester.pump(const Duration(milliseconds: 280));

    expect(find.byKey(const Key('dry-run-log-sidebar')), findsOneWidget);
    expect(find.text('Dry-Run Execution Log'), findsOneWidget);
    expect(find.text('Running dry-run simulation…'), findsOneWidget);

    await tester.tap(
      find.descendant(
        of: find.byKey(const Key('dry-run-log-sidebar')),
        matching: find.byIcon(Icons.close),
      ),
    );
    await tester.pump();
    await tester.pump(const Duration(milliseconds: 280));
    await tester.pump(const Duration(milliseconds: 280));

    expect(find.byKey(const Key('dry-run-log-sidebar')), findsNothing);
  });

  testWidgets('DryRunLogPanel renders execution steps', (tester) async {
    const result = PipelineTestRunResult(
      pipelineId: 'p1',
      pipelineName: 'Weather RTL',
      eventType: 'WEATHER_HAZARD',
      executed: true,
      steps: [
        PipelineExecutionStepModel(
          nodeId: 't1',
          nodeType: 'TRIGGER',
          subtype: 'WEATHER_HAZARD',
          matched: true,
        ),
        PipelineExecutionStepModel(
          nodeId: 'a1',
          nodeType: 'ACTION',
          subtype: 'MAVLINK_RTL',
          matched: true,
        ),
      ],
    );

    await tester.pumpWidget(
      MaterialApp(
        home: Scaffold(
          body: SizedBox(
            width: 340,
            height: 600,
            child: DryRunLogPanel(sidebar: true, result: result),
          ),
        ),
      ),
    );

    expect(find.text('Weather RTL · WEATHER_HAZARD'), findsOneWidget);
    expect(find.text('EXECUTED'), findsOneWidget);
    expect(find.text('TRIGGER · WEATHER_HAZARD'), findsOneWidget);
    expect(find.text('ACTION · MAVLINK_RTL'), findsOneWidget);
  });
}
