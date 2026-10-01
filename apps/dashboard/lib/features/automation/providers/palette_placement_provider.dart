import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../models/automation_pipeline_models.dart';
import '../widgets/canvas_drop_registrar.dart';
import '../widgets/pipeline_node_widget.dart';
import 'automation_builder_provider.dart';

class PalettePlacementData {
  const PalettePlacementData({required this.type, required this.subtype});

  final PipelineNodeType type;
  final String subtype;
}

/// Click-to-select & click-to-place state (Figma/CAD style).
class PalettePlacementState {
  const PalettePlacementState({
    this.activePlacement,
    this.label,
    this.cursorGlobal,
    this.isOverCanvas = false,
  });

  final PalettePlacementData? activePlacement;
  final String? label;
  final Offset? cursorGlobal;
  final bool isOverCanvas;

  bool get isActive => activePlacement != null;

  PalettePlacementState copyWith({
    PalettePlacementData? activePlacement,
    String? label,
    Offset? cursorGlobal,
    bool? isOverCanvas,
    bool clear = false,
  }) {
    if (clear) return const PalettePlacementState();
    return PalettePlacementState(
      activePlacement: activePlacement ?? this.activePlacement,
      label: label ?? this.label,
      cursorGlobal: cursorGlobal ?? this.cursorGlobal,
      isOverCanvas: isOverCanvas ?? this.isOverCanvas,
    );
  }
}

class PalettePlacementNotifier extends StateNotifier<PalettePlacementState> {
  PalettePlacementNotifier(this._ref) : super(const PalettePlacementState());

  final Ref _ref;

  void selectPlacement(PalettePlacementData data, String label) {
    // ignore: avoid_print
    print('SELECTED NODE: ${data.subtype} ($label)');
    state = PalettePlacementState(
      activePlacement: data,
      label: label,
      cursorGlobal: state.cursorGlobal,
      isOverCanvas: state.cursorGlobal != null
          ? _ref
              .read(canvasDropRegistrarProvider)
              .isPointerOverDropZone(state.cursorGlobal!)
          : false,
    );
  }

  void updateCursor(Offset global) {
    if (!state.isActive) return;
    final registrar = _ref.read(canvasDropRegistrarProvider);
    state = state.copyWith(
      cursorGlobal: global,
      isOverCanvas: registrar.isPointerOverDropZone(global),
    );
  }

  void placeAtScene(Offset sceneCenter) {
    if (!state.isActive || state.activePlacement == null) return;

    try {
      final registrar = _ref.read(canvasDropRegistrarProvider);
      final center = registrar.sanitizeSceneCenter(sceneCenter);
      if (center == null) return;

      _ref.read(automationBuilderProvider.notifier).addNode(
            type: state.activePlacement!.type,
            subtype: state.activePlacement!.subtype,
            position: Offset(
              center.dx - kPipelineNodeWidth / 2,
              center.dy - kPipelineNodeHeight / 2,
            ),
            preserveExactPosition: true,
          );
    } catch (_) {
      // Ignore placement failures.
    } finally {
      cancelPlacement();
    }
  }

  void placeAtGlobal(Offset global) {
    if (!state.isActive || state.activePlacement == null) return;

    final registrar = _ref.read(canvasDropRegistrarProvider);
    final scene = registrar.globalToScene(global);
    if (scene == null) return;
    placeAtScene(scene);
  }

  void placeAtViewportLocal(
      Offset viewportLocal, TransformationController controller) {
    if (!state.isActive || state.activePlacement == null) return;
    placeAtScene(controller.toScene(viewportLocal));
  }

  void cancelPlacement() {
    state = const PalettePlacementState();
  }
}

final palettePlacementProvider =
    StateNotifierProvider<PalettePlacementNotifier, PalettePlacementState>(
  (ref) => PalettePlacementNotifier(ref),
);
