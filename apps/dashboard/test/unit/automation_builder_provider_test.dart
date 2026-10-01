import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:next_iot_dashboard/features/automation/data/automation_repository.dart';
import 'package:next_iot_dashboard/features/automation/models/automation_pipeline_models.dart';
import 'package:next_iot_dashboard/features/automation/providers/automation_builder_provider.dart';
import 'package:next_iot_dashboard/features/automation/widgets/pipeline_ports.dart';

void main() {
  test('port hit target is 40x40 px', () {
    expect(kPortHitSize, 40.0);
    expect(kPortHitSize, greaterThanOrEqualTo(kPortDotSize + 24));
  });

  late AutomationBuilderNotifier notifier;

  setUp(() {
    notifier = AutomationBuilderNotifier(AutomationRepository());
    notifier.addNode(
      type: PipelineNodeType.trigger,
      subtype: TriggerSubtype.weatherHazard.apiValue,
      position: const Offset(80, 80),
    );
    notifier.addNode(
      type: PipelineNodeType.condition,
      subtype: ConditionSubtype.windSpeedLessThan.apiValue,
      position: const Offset(320, 80),
    );
    notifier.addNode(
      type: PipelineNodeType.action,
      subtype: ActionSubtype.mavlinkArm.apiValue,
      position: const Offset(560, 80),
    );
  });

  test('beginWiring activates global wiring state with fromPort', () {
    final nodes = notifier.state.nodes;
    notifier.beginWiring(
      fromNodeId: nodes[0].id,
      fromPort: PipelinePortSide.top,
      pointer: const Offset(100, 50),
    );
    expect(notifier.state.isWiringActive, isTrue);
    expect(notifier.state.connectingFromPort, PipelinePortSide.top);
    expect(notifier.state.connectingFromNodeId, nodes[0].id);
  });

  test('addConnection accumulates multi-chain edges A→B→C', () {
    final nodes = notifier.state.nodes;
    final trigger = nodes[0].id;
    final condition = nodes[1].id;
    final action = nodes[2].id;

    notifier.addConnection(trigger, condition);
    notifier.addConnection(condition, action);

    expect(notifier.state.edges, hasLength(2));
    expect(
      notifier.state.edges.map((e) => '${e.fromNode}->${e.toNode}'),
      containsAll(['$trigger->$condition', '$condition->$action']),
    );
  });

  test('deselectAll clears node and edge selection', () {
    notifier.selectNode(notifier.state.nodes[0].id);
    notifier.deselectAll();
    expect(notifier.state.selectedNodeId, isNull);

    final nodes = notifier.state.nodes;
    notifier.addConnection(nodes[0].id, nodes[1].id);
    notifier.selectEdge(notifier.state.edges.first);
    notifier.deselectAll();
    expect(notifier.state.selectedEdge, isNull);
  });

  test('removeSelectedEdge deletes only the selected connection', () {
    final nodes = notifier.state.nodes;
    notifier.addConnection(nodes[0].id, nodes[1].id);
    notifier.addConnection(nodes[1].id, nodes[2].id);

    final secondEdge = notifier.state.edges.last;
    notifier.selectEdge(secondEdge);
    notifier.removeSelectedEdge();

    expect(notifier.state.edges, hasLength(1));
    expect(notifier.state.edges.first.toNode, nodes[1].id);
    expect(notifier.state.selectedEdge, isNull);
  });

  test('addConnection preserves explicit fromPort and toPort', () {
    final nodes = notifier.state.nodes;
    notifier.addConnection(
      nodes[0].id,
      nodes[2].id,
      fromPort: PipelinePortSide.bottom,
      toPort: PipelinePortSide.top,
    );

    final edge = notifier.state.edges.single;
    expect(edge.fromPort, PipelinePortSide.bottom);
    expect(edge.toPort, PipelinePortSide.top);
  });

  test('hitTestPortAt finds nearest port within hit radius', () {
    final nodes = notifier.state.nodes;
    final target = nodes[1];
    final topCenter =
        pipelinePortCenter(target.position, PipelinePortSide.top);

    final hit = notifier.hitTestPortAt(topCenter);
    expect(hit, isNotNull);
    expect(hit!.nodeId, target.id);
    expect(hit.port, PipelinePortSide.top);
  });

  test('hitTestEdge finds edge near sampled bezier path', () {
    final nodes = notifier.state.nodes;
    notifier.addConnection(nodes[0].id, nodes[1].id);

    final source = nodes[0];
    final target = nodes[1];
    final edge = notifier.state.edges.first;
    final start = pipelinePortCenter(source.position, edge.fromPort);
    final end = pipelinePortCenter(target.position, edge.toPort);
    final sample =
        samplePipelineEdgePoints(start, end, samples: 8)[3];

    final hit = notifier.hitTestEdge(sample);
    expect(hit, isNotNull);
    expect(hit!.fromNode, source.id);
    expect(hit.toNode, target.id);
  });
}
