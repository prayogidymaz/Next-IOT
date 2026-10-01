import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../data/automation_repository.dart';
import '../models/automation_pipeline_models.dart';
import '../widgets/pipeline_ports.dart';

final automationRepositoryProvider = Provider<AutomationRepository>(
  (ref) => AutomationRepository(),
);

class AutomationBuilderState {
  const AutomationBuilderState({
    this.pipelineId,
    this.pipelineName = 'Untitled Pipeline',
    this.nodes = const [],
    this.edges = const [],
    this.connectingFromNodeId,
    this.connectingFromPort,
    this.connectingPointer,
    this.connectingSnapTargetId,
    this.connectingSnapToPort,
    this.isWiringActive = false,
    this.selectedNodeId,
    this.selectedEdge,
    this.isSaving = false,
    this.isTesting = false,
    this.statusMessage,
    this.error,
    this.testRunResult,
  });

  final String? pipelineId;
  final String pipelineName;
  final List<PipelineNodeModel> nodes;
  final List<PipelineEdgeModel> edges;
  final String? connectingFromNodeId;
  final PipelinePortSide? connectingFromPort;
  final Offset? connectingPointer;
  final String? connectingSnapTargetId;
  final PipelinePortSide? connectingSnapToPort;
  final bool isWiringActive;
  final String? selectedNodeId;
  final PipelineEdgeModel? selectedEdge;
  final bool isSaving;
  final bool isTesting;
  final String? statusMessage;
  final String? error;
  final PipelineTestRunResult? testRunResult;

  AutomationBuilderState copyWith({
    String? pipelineId,
    String? pipelineName,
    List<PipelineNodeModel>? nodes,
    List<PipelineEdgeModel>? edges,
    String? connectingFromNodeId,
    PipelinePortSide? connectingFromPort,
    Offset? connectingPointer,
    String? connectingSnapTargetId,
    PipelinePortSide? connectingSnapToPort,
    bool? isWiringActive,
    String? selectedNodeId,
    PipelineEdgeModel? selectedEdge,
    bool? isSaving,
    bool? isTesting,
    String? statusMessage,
    String? error,
    PipelineTestRunResult? testRunResult,
    bool clearConnecting = false,
    bool clearError = false,
    bool clearTestRun = false,
    bool clearSelectedNode = false,
    bool clearSelectedEdge = false,
  }) {
    return AutomationBuilderState(
      pipelineId: pipelineId ?? this.pipelineId,
      pipelineName: pipelineName ?? this.pipelineName,
      nodes: nodes ?? this.nodes,
      edges: edges ?? this.edges,
      connectingFromNodeId: clearConnecting
          ? null
          : (connectingFromNodeId ?? this.connectingFromNodeId),
      connectingFromPort: clearConnecting
          ? null
          : (connectingFromPort ?? this.connectingFromPort),
      connectingPointer: clearConnecting
          ? null
          : (connectingPointer ?? this.connectingPointer),
      connectingSnapTargetId: clearConnecting
          ? null
          : (connectingSnapTargetId ?? this.connectingSnapTargetId),
      connectingSnapToPort: clearConnecting
          ? null
          : (connectingSnapToPort ?? this.connectingSnapToPort),
      isWiringActive:
          clearConnecting ? false : (isWiringActive ?? this.isWiringActive),
      selectedNodeId:
          clearSelectedNode ? null : (selectedNodeId ?? this.selectedNodeId),
      selectedEdge:
          clearSelectedEdge ? null : (selectedEdge ?? this.selectedEdge),
      isSaving: isSaving ?? this.isSaving,
      isTesting: isTesting ?? this.isTesting,
      statusMessage: statusMessage ?? this.statusMessage,
      error: clearError ? null : (error ?? this.error),
      testRunResult:
          clearTestRun ? null : (testRunResult ?? this.testRunResult),
    );
  }

  AutomationPipelineModel toPipelineModel() {
    return AutomationPipelineModel(
      id: pipelineId,
      name: pipelineName,
      isActive: true,
      nodes: nodes,
      edges: edges,
    );
  }
}

class AutomationBuilderNotifier extends StateNotifier<AutomationBuilderState> {
  AutomationBuilderNotifier(this._repository)
      : super(const AutomationBuilderState());

  final AutomationRepository _repository;
  int _nodeCounter = 0;

  String _nextNodeId() {
    _nodeCounter += 1;
    return 'node_$_nodeCounter';
  }

  static const scenePaintOffset = Offset(10000, 10000);
  static const canvasWidth = 20000.0;
  static const canvasHeight = 20000.0;
  static const fallbackSpawnPosition = Offset(200, 200);
  static const firstNodeSpawnPosition = Offset(100, 100);

  Offset sanitizePosition(Offset position, {Offset? fallback}) {
    final safeFallback = fallback ??
        (state.nodes.isEmpty ? firstNodeSpawnPosition : fallbackSpawnPosition);
    if (!position.dx.isFinite || !position.dy.isFinite) {
      return safeFallback;
    }
    return position;
  }

  Offset clampNodePosition(Offset position) => sanitizePosition(position);

  Offset toPaintPosition(Offset logical) => logical + scenePaintOffset;

  Offset defaultSpawnPosition() {
    try {
      final index = state.nodes.length;
      return clampNodePosition(
        firstNodeSpawnPosition +
            Offset((index % 6) * 36.0, (index ~/ 6) * 36.0),
      );
    } catch (_) {
      return fallbackSpawnPosition;
    }
  }

  void spawnFromPalette({
    required PipelineNodeType type,
    required String subtype,
    Offset? position,
  }) {
    try {
      addNode(
        type: type,
        subtype: subtype,
        position: position ?? defaultSpawnPosition(),
      );
    } catch (e) {
      state = state.copyWith(error: 'Could not add node: $e');
    }
  }

  void addNode({
    required PipelineNodeType type,
    required String subtype,
    required Offset position,
    bool preserveExactPosition = false,
  }) {
    try {
      final existingNodes = List<PipelineNodeModel>.from(state.nodes);
      final resolvedPosition =
          preserveExactPosition && position.dx.isFinite && position.dy.isFinite
              ? position
              : clampNodePosition(position);
      final node = PipelineNodeModel(
        id: _nextNodeId(),
        type: type,
        subtype: subtype,
        position: resolvedPosition,
        config: _defaultConfigForSubtype(subtype),
      );
      state = state.copyWith(
        nodes: [...existingNodes, node],
        statusMessage: 'Added ${node.label}',
        clearError: true,
      );
    } catch (e) {
      state = state.copyWith(error: 'Could not add node: $e');
    }
  }

  Map<String, dynamic> _defaultConfigForSubtype(String subtype) {
    return switch (subtype) {
      'WIND_SPEED_LESS_THAN' => {'max_wind_mps': 12.0},
      'BATTERY_ABOVE' => {'min_percent': 30},
      'TIME_WINDOW' => {'start_hour': 6, 'end_hour': 18},
      'AI_DETECTION' => {'target_class': 'person', 'min_confidence': 0.7},
      'DISPATCH_SAR_GRID' => {'radius_m': 500},
      'WEBSOCKET_ALERT' => {'channel': 'tactical-alerts'},
      _ => {},
    };
  }

  void moveNode(String nodeId, Offset delta) {
    try {
      final nodes = state.nodes.map((n) {
        if (n.id != nodeId) return n;
        final next = n.position + delta;
        if (!next.dx.isFinite || !next.dy.isFinite) return n;
        return n.copyWith(position: next);
      }).toList(growable: false);
      state = state.copyWith(nodes: nodes);
    } catch (_) {
      // Ignore transient drag errors.
    }
  }

  void removeNode(String nodeId) {
    state = state.copyWith(
      nodes: state.nodes.where((n) => n.id != nodeId).toList(),
      edges: state.edges
          .where((e) => e.fromNode != nodeId && e.toNode != nodeId)
          .toList(),
      selectedNodeId:
          state.selectedNodeId == nodeId ? null : state.selectedNodeId,
      clearConnecting: state.connectingFromNodeId == nodeId,
    );
  }

  void updatePipelineName(String name) {
    final trimmed = name.trim();
    state = state.copyWith(
      pipelineName: trimmed.isEmpty ? 'Untitled Pipeline' : trimmed,
    );
  }

  void updateNodeConfig(String nodeId, Map<String, dynamic> config) {
    final nodes = state.nodes.map((n) {
      if (n.id != nodeId) return n;
      return n.copyWith(config: config);
    }).toList();
    state = state.copyWith(nodes: nodes);
  }

  void selectNode(String? nodeId) {
    if (nodeId == null) {
      state = state.copyWith(clearSelectedNode: true, clearSelectedEdge: true);
      return;
    }
    state = state.copyWith(
      selectedNodeId: nodeId,
      clearSelectedEdge: true,
    );
  }

  void selectEdge(PipelineEdgeModel edge) {
    state = state.copyWith(
      selectedEdge: edge,
      clearSelectedNode: true,
      clearConnecting: true,
    );
  }

  void deselectAll() {
    state = state.copyWith(clearSelectedNode: true, clearSelectedEdge: true);
  }

  void deselectAllNodes() => deselectAll();

  PipelineEdgeModel? hitTestEdge(Offset scenePoint, {double threshold = 18}) {
    PipelineEdgeModel? bestEdge;
    var bestDistance = threshold;

    for (final edge in state.edges) {
      final source = _nodeById(edge.fromNode);
      final target = _nodeById(edge.toNode);
      if (source == null || target == null) continue;

      final start = pipelinePortCenter(source.position, edge.fromPort);
      final end = pipelinePortCenter(target.position, edge.toPort);
      final distance = distanceToPipelineEdge(
        scenePoint,
        start,
        end,
        fromPort: edge.fromPort,
        toPort: edge.toPort,
      );
      if (distance <= bestDistance) {
        bestDistance = distance;
        bestEdge = edge;
      }
    }
    return bestEdge;
  }

  void removeSelectedEdge() {
    final edge = state.selectedEdge;
    if (edge == null) return;
    removeConnection(edge.fromNode, edge.toNode);
    state = state.copyWith(clearSelectedEdge: true);
  }

  void deleteSelection() {
    if (state.selectedEdge != null) {
      removeSelectedEdge();
      return;
    }
  }

  void resetConnectingState() {
    state = state.copyWith(clearConnecting: true, isWiringActive: false);
  }

  PipelineEdgeModel? edgeAtPort(String nodeId, PipelinePortSide side) {
    for (final edge in state.edges) {
      if (edge.fromNode == nodeId && edge.fromPort == side) return edge;
      if (edge.toNode == nodeId && edge.toPort == side) return edge;
    }
    return null;
  }

  PipelineEdgeModel? edgeAtInputPort(String nodeId, PipelinePortSide side) =>
      edgeAtPort(nodeId, side);

  Set<PipelinePortSide> connectedPortsFor(String nodeId) {
    final ports = <PipelinePortSide>{};
    for (final edge in state.edges) {
      if (edge.fromNode == nodeId) ports.add(edge.fromPort);
      if (edge.toNode == nodeId) ports.add(edge.toPort);
    }
    return ports;
  }

  Set<PipelinePortSide> connectedInputPortsFor(String nodeId) =>
      connectedPortsFor(nodeId);

  void removeConnection(String fromNode, String toNode) {
    final removingSelected = state.selectedEdge?.fromNode == fromNode &&
        state.selectedEdge?.toNode == toNode;
    state = state.copyWith(
      edges: state.edges
          .where((e) => !(e.fromNode == fromNode && e.toNode == toNode))
          .toList(),
      statusMessage: 'Connection removed',
      clearSelectedEdge: removingSelected,
    );
  }

  void removeConnectionAtPort(String nodeId, PipelinePortSide side) {
    final edge = edgeAtPort(nodeId, side);
    if (edge != null) removeConnection(edge.fromNode, edge.toNode);
  }

  void removeConnectionAtInputPort(String nodeId, PipelinePortSide side) =>
      removeConnectionAtPort(nodeId, side);

  bool canConnectFrom(String sourceNodeId) {
    final source = _nodeById(sourceNodeId);
    if (source == null) return false;
    return switch (source.type) {
      PipelineNodeType.trigger => true,
      PipelineNodeType.condition => true,
      PipelineNodeType.action => true,
    };
  }

  void beginWiring({
    required String fromNodeId,
    required PipelinePortSide fromPort,
    required Offset pointer,
  }) {
    if (!canConnectFrom(fromNodeId)) {
      resetConnectingState();
      return;
    }
    state = state.copyWith(
      isWiringActive: true,
      connectingFromNodeId: fromNodeId,
      connectingFromPort: fromPort,
      connectingPointer: pointer,
      connectingSnapTargetId: null,
      connectingSnapToPort: null,
      clearError: true,
      clearSelectedEdge: true,
    );
  }

  void startConnection(
    String fromNodeId, {
    Offset? pointer,
    PipelinePortSide fromPort = PipelinePortSide.right,
  }) {
    beginWiring(
      fromNodeId: fromNodeId,
      fromPort: fromPort,
      pointer: pointer ?? Offset.zero,
    );
  }

  PipelineNodeModel? _nodeById(String id) {
    for (final node in state.nodes) {
      if (node.id == id) return node;
    }
    return null;
  }

  Offset? _sourcePortPosition() {
    final fromId = state.connectingFromNodeId;
    if (fromId == null) return null;
    final source = _nodeById(fromId);
    if (source == null) return null;
    final side = state.connectingFromPort ?? PipelinePortSide.right;
    return pipelinePortCenter(source.position, side);
  }

  PipelinePortSnap? _findSnapTarget(Offset scenePoint) {
    final fromId = state.connectingFromNodeId;
    if (fromId == null) return null;

    final sourcePos = _sourcePortPosition();
    if (sourcePos == null) return null;

    String? targetId;
    PipelinePortSide? targetPort;
    var bestScore = double.infinity;

    for (final node in state.nodes) {
      if (!_isValidConnectionTarget(fromId, node)) continue;

      final onNode = _nodeBodyContains(node, scenePoint);
      for (final side in PipelinePortSide.allPorts) {
        final portCenter = pipelinePortCenter(node.position, side);
        final distance = (portCenter - scenePoint).distance;
        if (distance >= 80 && !onNode) continue;

        final score = distance + (onNode ? 0 : 500);
        if (score < bestScore) {
          bestScore = score;
          targetId = node.id;
          targetPort = side;
        }
      }
    }

    if (targetId == null || targetPort == null) return null;
    return PipelinePortSnap(nodeId: targetId, port: targetPort);
  }

  void updateConnectionPointer(Offset pointer) {
    if (!state.isWiringActive || state.connectingFromNodeId == null) return;
    final snap = _findSnapTarget(pointer);
    state = state.copyWith(
      connectingPointer: pointer,
      connectingSnapTargetId: snap?.nodeId,
      connectingSnapToPort: snap?.port,
    );
  }

  void cancelConnection() => resetConnectingState();

  /// Returns the nearest port dot under [scenePoint] within the 40×40 hit-box.
  PipelinePortSnap? hitTestPortAt(Offset scenePoint) {
    const radius = kPortHitSize / 2;
    PipelinePortSnap? best;
    var bestDistance = double.infinity;

    for (final node in state.nodes) {
      for (final side in PipelinePortSide.allPorts) {
        final center = pipelinePortCenter(node.position, side);
        final distance = (center - scenePoint).distance;
        if (distance <= radius && distance < bestDistance) {
          bestDistance = distance;
          best = PipelinePortSnap(nodeId: node.id, port: side);
        }
      }
    }
    return best;
  }

  bool canCompleteWiringTo(String nodeId, PipelinePortSide side) {
    final fromId = state.connectingFromNodeId;
    if (fromId == null) return false;
    if (fromId == nodeId && side == state.connectingFromPort) return false;
    final target = _nodeById(nodeId);
    if (target == null) return false;
    return _isValidConnectionTarget(fromId, target);
  }

  bool _isValidConnectionTarget(String sourceNodeId, PipelineNodeModel node) {
    if (node.id == sourceNodeId || node.type == PipelineNodeType.trigger) {
      return false;
    }
    return true;
  }

  bool _nodeBodyContains(PipelineNodeModel node, Offset scenePoint) {
    return Rect.fromLTWH(
      node.position.dx,
      node.position.dy,
      kPipelineNodeWidth,
      kPipelineNodeHeight,
    ).inflate(28).contains(scenePoint);
  }

  void finishConnectionAt(Offset scenePoint) {
    final from = state.connectingFromNodeId;
    if (from == null) return;

    try {
      final snap = state.connectingSnapTargetId != null &&
              state.connectingSnapToPort != null
          ? PipelinePortSnap(
              nodeId: state.connectingSnapTargetId!,
              port: state.connectingSnapToPort!,
            )
          : _findSnapTarget(scenePoint);

      if (snap != null) {
        addConnection(from, snap.nodeId, toPort: snap.port);
      }
    } finally {
      resetConnectingState();
    }
  }

  void addConnection(
    String sourceNodeId,
    String targetNodeId, {
    PipelinePortSide? fromPort,
    PipelinePortSide toPort = PipelinePortSide.left,
  }) {
    if (sourceNodeId == targetNodeId || !canConnectFrom(sourceNodeId)) {
      return;
    }

    PipelineNodeModel? target;
    for (final node in state.nodes) {
      if (node.id == targetNodeId) {
        target = node;
        break;
      }
    }
    if (target == null || !_isValidConnectionTarget(sourceNodeId, target)) {
      return;
    }

    final duplicate = state.edges.any(
      (e) => e.fromNode == sourceNodeId && e.toNode == targetNodeId,
    );
    if (duplicate) return;

    final resolvedFromPort =
        fromPort ?? state.connectingFromPort ?? PipelinePortSide.right;

    final nextEdge = PipelineEdgeModel(
      fromNode: sourceNodeId,
      toNode: targetNodeId,
      fromPort: resolvedFromPort,
      toPort: toPort,
    );

    state = state.copyWith(
      edges: [...state.edges, nextEdge],
      statusMessage: 'Connected nodes',
      clearSelectedEdge: true,
    );
  }

  void completeConnection(String toNodeId, {PipelinePortSide? toPort}) {
    final from = state.connectingFromNodeId;
    if (from == null) return;

    try {
      final target = _nodeById(toNodeId);
      final source = _nodeById(from);
      if (target == null || source == null) return;

      final pointer = state.connectingPointer;
      final fromSide = state.connectingFromPort ?? PipelinePortSide.right;
      final resolvedPort = toPort ??
          state.connectingSnapToPort ??
          (pointer != null
              ? resolveTargetPort(
                  sourcePosition: pipelinePortCenter(source.position, fromSide),
                  target: target,
                  scenePoint: pointer,
                  pointerNearTarget: _nodeBodyContains(target, pointer),
                )
              : PipelinePortSide.left);

      addConnection(
        from,
        toNodeId,
        fromPort: fromSide,
        toPort: resolvedPort,
      );
    } finally {
      resetConnectingState();
    }
  }

  void dismissError() {
    state = state.copyWith(clearError: true);
  }

  void clearCanvas() {
    state = const AutomationBuilderState(pipelineName: 'Untitled Pipeline');
    _nodeCounter = 0;
  }

  void loadPipeline(AutomationPipelineModel pipeline) {
    _nodeCounter = pipeline.nodes.length;
    state = AutomationBuilderState(
      pipelineId: pipeline.id,
      pipelineName: pipeline.name,
      nodes: pipeline.nodes,
      edges: pipeline.edges,
      statusMessage: 'Loaded ${pipeline.name}',
    );
  }

  Future<void> saveAndDeploy() async {
    state = state.copyWith(isSaving: true, clearError: true);
    try {
      final saved = await _syncPipelineToBackend();
      state = state.copyWith(
        isSaving: false,
        pipelineId: saved.id,
        statusMessage: 'Pipeline deployed',
      );
    } catch (e) {
      state = state.copyWith(isSaving: false, error: e.toString());
    }
  }

  Future<AutomationPipelineModel> _syncPipelineToBackend() async {
    final model = state.toPipelineModel();
    if (state.pipelineId == null) {
      return _repository.createPipeline(model);
    }
    return _repository.updatePipeline(state.pipelineId!, model);
  }

  Map<String, dynamic> _buildDryRunContext(
    PipelineNodeModel trigger,
    List<PipelineNodeModel> nodes,
  ) {
    final context = <String, dynamic>{
      'device_id': trigger.config['device_id'] ?? 'dry-run-device',
      'dry_run': true,
    };

    switch (trigger.subtype) {
      case 'AI_DETECTION':
        context['detection_class'] = trigger.config['target_class'] ?? 'person';
        context['confidence'] = trigger.config['min_confidence'] ?? 0.9;
        break;
      case 'TELEMETRY_ANOMALY':
        context['anomaly_type'] =
            trigger.config['anomaly_type'] ?? 'telemetry_anomaly';
        break;
      case 'GEOFENCE_BREACH':
        context['anomaly_type'] = 'geofence_breach';
        context['breach_type'] = trigger.config['breach_type'] ?? 'exit';
        break;
      case 'WEATHER_HAZARD':
        context['flight_safety_status'] =
            trigger.config['flight_safety_status'] ?? 'CAUTION';
        break;
      case 'TELEMETRY_THRESHOLD':
        final metric = trigger.config['metric'] ?? 'temperature';
        final threshold = (trigger.config['threshold'] ?? 30) as num;
        final metrics = Map<String, dynamic>.from(
          context['metrics'] as Map<String, dynamic>? ?? {},
        );
        metrics[metric] = threshold + 1;
        context['metrics'] = metrics;
        break;
    }

    for (final node in nodes) {
      if (node.type != PipelineNodeType.condition) continue;
      switch (node.subtype) {
        case 'WIND_SPEED_LESS_THAN':
          final threshold = (node.config['max_wind_mps'] ??
              node.config['threshold'] ??
              15) as num;
          context['wind_speed_m_s'] = threshold - 1;
          break;
        case 'BATTERY_ABOVE':
          final threshold = (node.config['threshold'] ?? 11.0) as num;
          final metrics = Map<String, dynamic>.from(
            context['metrics'] as Map<String, dynamic>? ?? {},
          );
          metrics['voltage'] = threshold + 1;
          context['metrics'] = metrics;
          break;
        case 'TIME_WINDOW':
          break;
      }
    }

    return context;
  }

  Future<void> dryRunTest() async {
    state =
        state.copyWith(isTesting: true, clearError: true, clearTestRun: true);
    try {
      if (state.nodes.isEmpty) {
        state = state.copyWith(
          isTesting: false,
          error: 'Add at least one node before dry-run.',
        );
        return;
      }

      final trigger = state.nodes.firstWhere(
        (n) => n.type == PipelineNodeType.trigger,
        orElse: () => state.nodes.first,
      );
      final graph = state.toPipelineModel().toGraphJson();
      final result = await _repository.dryRunGraph(
        eventType: trigger.subtype,
        context: _buildDryRunContext(trigger, state.nodes),
        nodes: (graph['nodes'] as List).cast<Map<String, dynamic>>(),
        edges: (graph['edges'] as List).cast<Map<String, dynamic>>(),
        pipelineName: state.pipelineName,
      );
      state = state.copyWith(
        isTesting: false,
        testRunResult: result,
        statusMessage: result.executed
            ? 'Dry-run executed'
            : 'Dry-run completed (no match)',
      );
    } catch (e) {
      state = state.copyWith(isTesting: false, error: e.toString());
    }
  }

  Future<Map<String, dynamic>> buildExportDocument() async {
    if (state.pipelineId != null) {
      return _repository.exportPipelineJson(state.pipelineId!);
    }
    return state.toPipelineModel().toExportDocument();
  }

  Future<void> importDocument(Map<String, dynamic> document) async {
    state = state.copyWith(isSaving: true, clearError: true);
    try {
      final validation = await _repository.validatePipelineJson(document);
      if (!validation.valid) {
        throw Exception(validation.errors.join('; '));
      }
      final imported = await _repository.importPipelineJson(document);
      final model = AutomationPipelineModel.fromExportDocument(imported);
      state = AutomationBuilderState(
        pipelineId: model.id,
        pipelineName: model.name,
        nodes: model.nodes,
        edges: model.edges,
        statusMessage: 'Pipeline imported',
      );
    } catch (e) {
      state = state.copyWith(isSaving: false, error: e.toString());
    }
  }

  Future<void> previewDocument(Map<String, dynamic> document) async {
    state = state.copyWith(isSaving: true, clearError: true);
    try {
      final validation = await _repository.validatePipelineJson(document);
      if (!validation.valid) {
        throw Exception(validation.errors.join('; '));
      }
      applyLocalDocument(document);
      state = state.copyWith(isSaving: false);
    } catch (e) {
      state = state.copyWith(isSaving: false, error: e.toString());
    }
  }

  void applyLocalDocument(Map<String, dynamic> document) {
    final model = AutomationPipelineModel.fromExportDocument(document);
    state = AutomationBuilderState(
      pipelineId: model.id,
      pipelineName: model.name,
      nodes: model.nodes,
      edges: model.edges,
      statusMessage: 'Pipeline loaded from JSON',
    );
  }
}

final automationBuilderProvider =
    StateNotifierProvider<AutomationBuilderNotifier, AutomationBuilderState>(
  (ref) => AutomationBuilderNotifier(ref.watch(automationRepositoryProvider)),
);
