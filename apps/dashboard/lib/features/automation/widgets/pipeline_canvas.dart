import 'package:flutter/gestures.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../core/theme/tactical_theme.dart';
import '../models/automation_pipeline_models.dart';
import '../providers/automation_builder_provider.dart';
import '../providers/palette_placement_provider.dart';
import 'canvas_drop_registrar.dart';
import 'node_config_dialog.dart';
import 'pipeline_node_widget.dart';
import 'pipeline_ports.dart';

class PipelineCanvas extends ConsumerStatefulWidget {
  const PipelineCanvas({super.key});

  static const canvasWidth = AutomationBuilderNotifier.canvasWidth;
  static const canvasHeight = AutomationBuilderNotifier.canvasHeight;

  @override
  ConsumerState<PipelineCanvas> createState() => _PipelineCanvasState();
}

class _PipelineCanvasState extends ConsumerState<PipelineCanvas> {
  final _dropZoneKey = GlobalKey();
  final _sceneKey = GlobalKey();
  final _transformController = TransformationController();

  int? _wiringPointerId;
  Offset? _wiringDownScene;
  bool _wiringDragged = false;
  bool _portDragActive = false;
  PointerRoute? _pointerRoute;

  static const _dragThreshold = 8.0;

  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) => _registerDropZone());
  }

  void _registerDropZone() {
    if (!mounted) return;
    ref.read(canvasDropRegistrarProvider).register(
          dropZoneKey: _dropZoneKey,
          sceneKey: _sceneKey,
          transformController: _transformController,
        );
  }

  double get _viewportScale =>
      _transformController.value.getMaxScaleOnAxis().clamp(0.01, 8.0);

  Offset? _logicalCenterFromGlobal(Offset global) {
    return ref.read(canvasDropRegistrarProvider).logicalFromGlobal(global);
  }

  Offset? _logicalCenterFromPlacementTap(Offset global, Offset viewportLocal) {
    final registrar = ref.read(canvasDropRegistrarProvider);
    final fromViewport = registrar.logicalFromViewportLocal(viewportLocal);
    if (fromViewport != null) return fromViewport;
    return registrar.logicalFromGlobal(global);
  }

  void _openConfig(PipelineNodeModel node) {
    if (!mounted) return;
    ref.read(automationBuilderProvider.notifier).selectNode(node.id);
    NodeConfigDialog.show(
      context,
      node: node,
      onSave: (config) => ref
          .read(automationBuilderProvider.notifier)
          .updateNodeConfig(node.id, config),
    ).whenComplete(() {
      if (mounted) {
        ref.read(automationBuilderProvider.notifier).selectNode(null);
      }
    });
  }

  void _attachPointerRoute(int pointer) {
    _pointerRoute ??= _handleGlobalPointer;
    GestureBinding.instance.pointerRouter.addRoute(pointer, _pointerRoute!);
  }

  void _detachPointerRoute(int pointer) {
    if (_pointerRoute != null) {
      GestureBinding.instance.pointerRouter.removeRoute(pointer, _pointerRoute!);
    }
  }

  void _resetLocalWiringTracking() {
    final pointer = _wiringPointerId;
    _wiringPointerId = null;
    _wiringDownScene = null;
    _wiringDragged = false;
    _portDragActive = false;
    if (pointer != null) {
      _detachPointerRoute(pointer);
    }
  }

  void _handleGlobalPointer(PointerEvent event) {
    if (!mounted) return;
    final notifier = ref.read(automationBuilderProvider.notifier);
    final state = ref.read(automationBuilderProvider);
    if (!state.isWiringActive) return;

    if (_wiringPointerId != null && event.pointer != _wiringPointerId) {
      return;
    }

    if (event is PointerMoveEvent) {
      final scene = _logicalCenterFromGlobal(event.position);
      if (scene == null) return;
      if (_wiringDownScene != null &&
          !_wiringDragged &&
          (scene - _wiringDownScene!).distance >= _dragThreshold) {
        _wiringDragged = true;
      }
      notifier.updateConnectionPointer(scene);
      return;
    }

    if (event is PointerUpEvent || event is PointerCancelEvent) {
      if (_wiringPointerId == null || event.pointer != _wiringPointerId) {
        return;
      }

      final scene = _logicalCenterFromGlobal(event.position);
      _finishWiringPointerUp(
        notifier: notifier,
        state: state,
        scene: scene,
      );
    }
  }

  void _finishWiringPointerUp({
    required AutomationBuilderNotifier notifier,
    required AutomationBuilderState state,
    required Offset? scene,
    PipelinePortSide? explicitTargetSide,
    String? explicitTargetNodeId,
  }) {
    final fromId = state.connectingFromNodeId;
    final fromPort = state.connectingFromPort;
    if (fromId == null) {
      _resetLocalWiringTracking();
      return;
    }

    if (explicitTargetNodeId != null &&
        explicitTargetSide != null &&
        notifier.canCompleteWiringTo(explicitTargetNodeId, explicitTargetSide)) {
      notifier.completeConnection(
        explicitTargetNodeId,
        toPort: explicitTargetSide,
      );
      _resetLocalWiringTracking();
      return;
    }

    if (scene != null) {
      final hit = notifier.hitTestPortAt(scene);
      if (hit != null &&
          notifier.canCompleteWiringTo(hit.nodeId, hit.port)) {
        notifier.completeConnection(hit.nodeId, toPort: hit.port);
        _resetLocalWiringTracking();
        return;
      }

      if (!_wiringDragged &&
          hit != null &&
          hit.nodeId == fromId &&
          hit.port == fromPort) {
        // Click step 1: release on same source port — keep wiring active.
        _resetLocalWiringTracking();
        return;
      }

      if (_wiringDragged) {
        notifier.finishConnectionAt(scene);
        _resetLocalWiringTracking();
        return;
      }
    }

    notifier.resetConnectingState();
    _resetLocalWiringTracking();
  }

  void _handlePortTap(
    PipelineNodeModel node,
    PipelinePortSide side,
    AutomationBuilderState state,
    AutomationBuilderNotifier notifier,
  ) {
    if (state.isWiringActive) {
      if (!notifier.canCompleteWiringTo(node.id, side)) return;
      notifier.completeConnection(node.id, toPort: side);
      _resetLocalWiringTracking();
      return;
    }

    final connected = notifier.connectedPortsFor(node.id).contains(side);
    if (connected) {
      notifier.removeConnectionAtPort(node.id, side);
    }
  }

  void _handlePortPointerDown(
    PipelineNodeModel node,
    PipelinePortSide side,
    PointerDownEvent event,
    AutomationBuilderState state,
    AutomationBuilderNotifier notifier,
  ) {
    if (state.isWiringActive) {
      if (notifier.canCompleteWiringTo(node.id, side)) {
        notifier.completeConnection(node.id, toPort: side);
        _resetLocalWiringTracking();
      }
      return;
    }

    if (notifier.connectedPortsFor(node.id).contains(side)) {
      return;
    }

    final scene = _logicalCenterFromGlobal(event.position) ??
        pipelinePortCenter(node.position, side);

    _wiringPointerId = event.pointer;
    _wiringDownScene = scene;
    _wiringDragged = false;
    _portDragActive = true;

    notifier.beginWiring(
      fromNodeId: node.id,
      fromPort: side,
      pointer: scene,
    );
    _attachPointerRoute(event.pointer);
  }

  void _handlePortPointerUp(
    PipelineNodeModel node,
    PipelinePortSide side,
    PointerUpEvent event,
    AutomationBuilderState state,
    AutomationBuilderNotifier notifier,
  ) {
    if (!state.isWiringActive || _wiringPointerId != event.pointer) return;

    final scene = _logicalCenterFromGlobal(event.position);
    _finishWiringPointerUp(
      notifier: notifier,
      state: state,
      scene: scene,
      explicitTargetSide: side,
      explicitTargetNodeId: node.id,
    );
  }

  @override
  void dispose() {
    _resetLocalWiringTracking();
    try {
      ref.read(canvasDropRegistrarProvider).unregister();
    } catch (_) {
      // Provider may already be disposed during teardown.
    }
    _transformController.dispose();
    super.dispose();
  }

  Widget _buildSceneStack({
    required AutomationBuilderState state,
    required AutomationBuilderNotifier notifier,
    required Offset paintOffset,
    required bool showEmptyHint,
  }) {
    final canvasNodes = state.nodes;

    return SizedBox(
      key: _sceneKey,
      width: PipelineCanvas.canvasWidth,
      height: PipelineCanvas.canvasHeight,
      child: Stack(
        clipBehavior: Clip.none,
        children: [
          Positioned.fill(
            child: GestureDetector(
              key: const Key('pipeline-canvas-background'),
              behavior: HitTestBehavior.translucent,
              onTapDown: (details) {
                if (state.isWiringActive) {
                  notifier.resetConnectingState();
                  _resetLocalWiringTracking();
                  return;
                }
                final scene = _logicalCenterFromGlobal(details.globalPosition);
                if (scene == null) {
                  notifier.deselectAll();
                  return;
                }
                final hitEdge = notifier.hitTestEdge(scene);
                if (hitEdge != null) {
                  notifier.selectEdge(hitEdge);
                } else {
                  notifier.deselectAll();
                }
              },
            ),
          ),
          ...canvasNodes.map((node) {
            final connectedPorts = notifier.connectedPortsFor(node.id);
            final paintPos = paintOffset + node.position;
            final isSnapTarget = state.connectingSnapTargetId == node.id;
            return Positioned(
              key: ValueKey(node.id),
              left: paintPos.dx,
              top: paintPos.dy,
              child: PipelineNodeWidget(
                key: ValueKey('pipeline-node-${node.id}'),
                node: node,
                selected: state.selectedNodeId == node.id,
                connecting: state.connectingFromNodeId == node.id,
                wiringSourcePort: state.isWiringActive &&
                        state.connectingFromNodeId == node.id
                    ? state.connectingFromPort
                    : null,
                highlightedPort:
                    isSnapTarget ? state.connectingSnapToPort : null,
                connectedPorts: connectedPorts,
                onDelete: () => notifier.removeNode(node.id),
                onConfigure: () => _openConfig(node),
                onSelect: () => notifier.selectNode(node.id),
                onDragDelta: (delta) =>
                    notifier.moveNode(node.id, delta / _viewportScale),
                onPortTap: (side) =>
                    _handlePortTap(node, side, state, notifier),
                onPortPointerDown: (side, event) => _handlePortPointerDown(
                  node,
                  side,
                  event,
                  state,
                  notifier,
                ),
                onPortPointerUp: (side, event) => _handlePortPointerUp(
                  node,
                  side,
                  event,
                  state,
                  notifier,
                ),
              ),
            );
          }),
          if (canvasNodes.isEmpty && showEmptyHint)
            Positioned(
              left: paintOffset.dx + 120,
              top: paintOffset.dy + 120,
              child: const Text(
                'Select a palette item, then click the canvas to place it',
                style: TextStyle(color: TacticalColors.textSecondary),
              ),
            ),
          Positioned.fill(
            child: IgnorePointer(
              ignoring: true,
              child: CustomPaint(
                painter: _EdgePainter(
                  nodes: canvasNodes,
                  edges: state.edges,
                  selectedEdge: state.selectedEdge,
                  connectingFrom: state.connectingFromNodeId,
                  connectingFromPort: state.connectingFromPort,
                  connectingPointer: state.connectingPointer,
                  connectingSnapTargetId: state.connectingSnapTargetId,
                  connectingSnapToPort: state.connectingSnapToPort,
                  paintOffset: paintOffset,
                ),
              ),
            ),
          ),
          ..._buildEdgeHitTargets(
            state: state,
            notifier: notifier,
            paintOffset: paintOffset,
          ),
        ],
      ),
    );
  }

  List<Widget> _buildEdgeHitTargets({
    required AutomationBuilderState state,
    required AutomationBuilderNotifier notifier,
    required Offset paintOffset,
  }) {
    if (state.isWiringActive) return const [];

    const hitSize = 22.0;
    final targets = <Widget>[];

    for (final edge in state.edges) {
      PipelineNodeModel? source;
      PipelineNodeModel? target;
      for (final node in state.nodes) {
        if (node.id == edge.fromNode) source = node;
        if (node.id == edge.toNode) target = node;
      }
      if (source == null || target == null) continue;

      final start =
          paintOffset + pipelinePortCenter(source.position, edge.fromPort);
      final end =
          paintOffset + pipelinePortCenter(target.position, edge.toPort);
      final points = samplePipelineEdgePoints(
        start,
        end,
        fromPort: edge.fromPort,
        toPort: edge.toPort,
        samples: 10,
      );

      for (final point in points) {
        targets.add(
          Positioned(
            left: point.dx - hitSize / 2,
            top: point.dy - hitSize / 2,
            width: hitSize,
            height: hitSize,
            child: GestureDetector(
              key: Key('edge-hit-${edge.fromNode}-${edge.toNode}-${point.dx}'),
              behavior: HitTestBehavior.translucent,
              onTap: () => notifier.selectEdge(edge),
              child: const SizedBox.expand(),
            ),
          ),
        );
      }
    }

    return targets;
  }

  @override
  Widget build(BuildContext context) {
    final state = ref.watch(automationBuilderProvider);
    final placement = ref.watch(palettePlacementProvider);
    final placementNotifier = ref.read(palettePlacementProvider.notifier);
    final notifier = ref.read(automationBuilderProvider.notifier);
    final paintOffset = AutomationBuilderNotifier.scenePaintOffset;

    final canvasView = Container(
      key: _dropZoneKey,
      color: placement.isActive && placement.isOverCanvas
          ? TacticalColors.cyan.withOpacity(0.06)
          : TacticalColors.background,
      child: InteractiveViewer(
        transformationController: _transformController,
        alignment: Alignment.topLeft,
        boundaryMargin: const EdgeInsets.all(400),
        minScale: 0.25,
        maxScale: 2.5,
        panEnabled: !placement.isActive && !_portDragActive,
        scaleEnabled: !placement.isActive && !_portDragActive,
        child: _buildSceneStack(
          state: state,
          notifier: notifier,
          paintOffset: paintOffset,
          showEmptyHint: !placement.isActive,
        ),
      ),
    );

    if (!placement.isActive) {
      return SizedBox.expand(child: canvasView);
    }

    return SizedBox.expand(
      child: GestureDetector(
        behavior: HitTestBehavior.opaque,
        onTapDown: (details) {
          final center = _logicalCenterFromPlacementTap(
            details.globalPosition,
            details.localPosition,
          );
          if (center != null) {
            placementNotifier.placeAtScene(center);
          }
        },
        onSecondaryTapDown: (_) => placementNotifier.cancelPlacement(),
        child: IgnorePointer(
          ignoring: true,
          child: canvasView,
        ),
      ),
    );
  }
}

class _EdgePainter extends CustomPainter {
  _EdgePainter({
    required this.nodes,
    required this.edges,
    required this.paintOffset,
    this.selectedEdge,
    this.connectingFrom,
    this.connectingFromPort,
    this.connectingPointer,
    this.connectingSnapTargetId,
    this.connectingSnapToPort,
  });

  final List<PipelineNodeModel> nodes;
  final List<PipelineEdgeModel> edges;
  final Offset paintOffset;
  final PipelineEdgeModel? selectedEdge;
  final String? connectingFrom;
  final PipelinePortSide? connectingFromPort;
  final Offset? connectingPointer;
  final String? connectingSnapTargetId;
  final PipelinePortSide? connectingSnapToPort;

  Offset _toPaint(Offset logical) => logical + paintOffset;

  Offset? _portCenter(String nodeId, PipelinePortSide side) {
    for (final node in nodes) {
      if (node.id == nodeId) {
        return _toPaint(pipelinePortCenter(node.position, side));
      }
    }
    return null;
  }

  @override
  void paint(Canvas canvas, Size size) {
    for (final edge in edges) {
      final start = _portCenter(edge.fromNode, edge.fromPort);
      final end = _portCenter(edge.toNode, edge.toPort);
      if (start == null || end == null) continue;

      final isSelected = selectedEdge != null && selectedEdge == edge;
      final edgePaint = Paint()
        ..color = isSelected
            ? TacticalColors.warning.withOpacity(0.98)
            : TacticalColors.cyan.withOpacity(0.9)
        ..strokeWidth = isSelected ? 4 : 2.5
        ..style = PaintingStyle.stroke
        ..strokeCap = StrokeCap.round;

      drawPipelineEdgeBezier(
        canvas,
        edgePaint,
        start,
        end,
        fromPort: edge.fromPort,
        toPort: edge.toPort,
      );
    }

    if (connectingFrom != null) {
      final fromSide = connectingFromPort ?? PipelinePortSide.right;
      final start = _portCenter(connectingFrom!, fromSide);
      if (start != null) {
        Offset end;
        PipelinePortSide toPort = PipelinePortSide.left;
        if (connectingSnapTargetId != null && connectingSnapToPort != null) {
          end = _portCenter(connectingSnapTargetId!, connectingSnapToPort!) ??
              start + const Offset(120, 0);
          toPort = connectingSnapToPort!;
        } else {
          end = connectingPointer != null
              ? _toPaint(connectingPointer!)
              : (start + const Offset(120, 0));
        }

        final previewPaint = Paint()
          ..color = TacticalColors.warning.withOpacity(0.95)
          ..strokeWidth = 3
          ..style = PaintingStyle.stroke
          ..strokeCap = StrokeCap.round;
        drawPipelineEdgeBezier(
          canvas,
          previewPaint,
          start,
          end,
          fromPort: fromSide,
          toPort: toPort,
          dashed: true,
        );
        canvas.drawCircle(end, 6, Paint()..color = TacticalColors.warning);
        canvas.drawCircle(
          start,
          5,
          Paint()..color = TacticalColors.warning.withOpacity(0.8),
        );
      }
    }
  }

  @override
  bool shouldRepaint(covariant _EdgePainter oldDelegate) {
    return oldDelegate.nodes != nodes ||
        oldDelegate.edges != edges ||
        oldDelegate.selectedEdge != selectedEdge ||
        oldDelegate.connectingFrom != connectingFrom ||
        oldDelegate.connectingFromPort != connectingFromPort ||
        oldDelegate.connectingPointer != connectingPointer ||
        oldDelegate.connectingSnapTargetId != connectingSnapTargetId ||
        oldDelegate.connectingSnapToPort != connectingSnapToPort ||
        oldDelegate.paintOffset != paintOffset;
  }
}
