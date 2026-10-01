import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../providers/automation_builder_provider.dart';
import 'pipeline_node_widget.dart';

extension TransformationControllerScene on TransformationController {
  /// Converts a viewport-local point to scene (canvas) coordinates.
  Offset toScene(Offset viewportLocal) {
    final inverse = Matrix4.inverted(value);
    return MatrixUtils.transformPoint(inverse, viewportLocal);
  }
}

/// Bridges palette pointer-drag sessions with the pipeline canvas viewport.
class CanvasDropRegistrar {
  GlobalKey? dropZoneKey;
  GlobalKey? sceneKey;
  TransformationController? transformController;

  void register({
    required GlobalKey dropZoneKey,
    required GlobalKey sceneKey,
    required TransformationController transformController,
  }) {
    this.dropZoneKey = dropZoneKey;
    this.sceneKey = sceneKey;
    this.transformController = transformController;
  }

  void unregister() {
    dropZoneKey = null;
    sceneKey = null;
    transformController = null;
  }

  RenderBox? get _dropBox =>
      dropZoneKey?.currentContext?.findRenderObject() as RenderBox?;

  bool isPointerOverDropZone(Offset global) {
    try {
      final box = _dropBox;
      if (box == null || !box.hasSize) return false;
      final local = box.globalToLocal(global);
      return local.dx >= 0 &&
          local.dy >= 0 &&
          local.dx <= box.size.width &&
          local.dy <= box.size.height;
    } catch (_) {
      return false;
    }
  }

  /// Converts a global pointer position to scene (canvas) coordinates.
  Offset? globalToScene(Offset global, {bool clamp = true}) {
    try {
      final controller = transformController;
      final box = _dropBox;
      if (controller == null || box == null || !box.hasSize) {
        return _sceneFromGlobalDirect(global, clamp: clamp);
      }

      final viewportLocal = box.globalToLocal(global);
      final logical = controller.toScene(viewportLocal) -
          AutomationBuilderNotifier.scenePaintOffset;
      return clamp ? clampScene(logical) : logical;
    } catch (_) {
      return _sceneFromGlobalDirect(global, clamp: clamp);
    }
  }

  Offset? _sceneFromGlobalDirect(Offset global, {bool clamp = true}) {
    try {
      final sceneBox =
          sceneKey?.currentContext?.findRenderObject() as RenderBox?;
      if (sceneBox == null || !sceneBox.hasSize) return null;
      final logical = sceneBox.globalToLocal(global) -
          AutomationBuilderNotifier.scenePaintOffset;
      return clamp ? clampScene(logical) : logical;
    } catch (_) {
      return null;
    }
  }

  /// Converts a viewport-local point to logical scene coordinates (node space).
  Offset? logicalFromViewportLocal(Offset viewportLocal) {
    try {
      final controller = transformController;
      if (controller == null) return null;
      final paint = controller.toScene(viewportLocal);
      final logical = paint - AutomationBuilderNotifier.scenePaintOffset;
      return logical.dx.isFinite && logical.dy.isFinite ? logical : null;
    } catch (_) {
      return null;
    }
  }

  /// Converts a global pointer position to logical scene coordinates.
  Offset? logicalFromGlobal(Offset global) {
    try {
      final box = _dropBox;
      if (box != null && box.hasSize) {
        final viewportLocal = box.globalToLocal(global);
        final fromViewport = logicalFromViewportLocal(viewportLocal);
        if (fromViewport != null) return fromViewport;
      }
      return _sceneFromGlobalDirect(global, clamp: false);
    } catch (_) {
      return null;
    }
  }

  Offset? sanitizeSceneCenter(Offset scene) {
    if (!scene.dx.isFinite || !scene.dy.isFinite) return null;
    return scene;
  }

  Offset clampScene(Offset scene, {Offset? fallback}) {
    return sanitizeSceneCenter(scene) ?? fallback ?? scene;
  }
}

final canvasDropRegistrarProvider = Provider<CanvasDropRegistrar>((ref) {
  final registrar = CanvasDropRegistrar();
  ref.onDispose(registrar.unregister);
  return registrar;
});
