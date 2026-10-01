import 'package:flutter/gestures.dart';
import 'package:flutter/material.dart';

import '../../../core/theme/tactical_theme.dart';
import '../models/automation_pipeline_models.dart';
import 'pipeline_ports.dart';

class PipelinePortWidget extends StatefulWidget {
  const PipelinePortWidget({
    super.key,
    required this.side,
    required this.label,
    required this.color,
    this.onTap,
    this.onPointerDown,
    this.onPointerUp,
    this.connected = false,
    this.isWiringSource = false,
    this.isTargetHighlight = false,
  });

  final PipelinePortSide side;
  final String label;
  final Color color;
  final VoidCallback? onTap;
  final void Function(PointerDownEvent event)? onPointerDown;
  final void Function(PointerUpEvent event)? onPointerUp;
  final bool connected;
  final bool isWiringSource;
  final bool isTargetHighlight;

  @override
  State<PipelinePortWidget> createState() => _PipelinePortWidgetState();
}

class _PipelinePortWidgetState extends State<PipelinePortWidget>
    with SingleTickerProviderStateMixin {
  late final AnimationController _pulseController;
  late final Animation<double> _pulse;

  @override
  void initState() {
    super.initState();
    _pulseController = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 900),
    );
    _pulse = Tween<double>(begin: 0.35, end: 1.0).animate(
      CurvedAnimation(parent: _pulseController, curve: Curves.easeInOut),
    );
    _syncPulseRunning();
  }

  @override
  void didUpdateWidget(covariant PipelinePortWidget oldWidget) {
    super.didUpdateWidget(oldWidget);
    if (oldWidget.isWiringSource != widget.isWiringSource) {
      _syncPulseRunning();
    }
  }

  void _syncPulseRunning() {
    if (widget.isWiringSource) {
      if (!_pulseController.isAnimating) {
        _pulseController.repeat(reverse: true);
      }
    } else {
      _pulseController
        ..stop()
        ..value = 0;
    }
  }

  @override
  void dispose() {
    _pulseController.dispose();
    super.dispose();
  }

  Color get _borderColor {
    if (widget.isWiringSource) return TacticalColors.warning;
    if (widget.isTargetHighlight) return TacticalColors.success;
    if (widget.connected) {
      return TacticalColors.warning.withOpacity(0.85);
    }
    return widget.color.withOpacity(0.75);
  }

  @override
  Widget build(BuildContext context) {
    final tooltip = widget.connected
        ? 'Connected — click to disconnect'
        : widget.isWiringSource
            ? 'Source — drag or click target port'
            : widget.isTargetHighlight
                ? 'Release here to connect'
                : widget.label;

    Widget dot = AnimatedContainer(
      duration: const Duration(milliseconds: 120),
      width: widget.isWiringSource || widget.isTargetHighlight
          ? kPortDotSize + 4
          : kPortDotSize,
      height: widget.isWiringSource || widget.isTargetHighlight
          ? kPortDotSize + 4
          : kPortDotSize,
      decoration: BoxDecoration(
        color: widget.isTargetHighlight
            ? TacticalColors.success.withOpacity(0.28)
            : widget.isWiringSource
                ? TacticalColors.warning.withOpacity(0.32)
                : widget.color.withOpacity(0.16),
        shape: BoxShape.circle,
        border: Border.all(
          color: _borderColor,
          width: widget.isWiringSource || widget.isTargetHighlight ? 3 : 2,
        ),
        boxShadow: widget.isWiringSource
            ? [
                BoxShadow(
                  color: TacticalColors.warning.withOpacity(0.55),
                  blurRadius: 14,
                  spreadRadius: 2,
                ),
              ]
            : widget.isTargetHighlight
                ? [
                    BoxShadow(
                      color: TacticalColors.success.withOpacity(0.45),
                      blurRadius: 12,
                      spreadRadius: 1,
                    ),
                  ]
                : null,
      ),
    );

    if (widget.isWiringSource) {
      dot = AnimatedBuilder(
        animation: _pulse,
        builder: (context, child) {
          return DecoratedBox(
            decoration: BoxDecoration(
              shape: BoxShape.circle,
              boxShadow: [
                BoxShadow(
                  color: TacticalColors.warning
                      .withOpacity(0.25 + (_pulse.value * 0.45)),
                  blurRadius: 8 + (_pulse.value * 10),
                  spreadRadius: _pulse.value * 3,
                ),
              ],
            ),
            child: child,
          );
        },
        child: dot,
      );
    }

    return Listener(
      behavior: HitTestBehavior.opaque,
      onPointerDown: widget.onPointerDown,
      onPointerUp: widget.onPointerUp,
      child: GestureDetector(
        behavior: HitTestBehavior.translucent,
        onTap: widget.onTap,
        child: Tooltip(
          message: tooltip,
          child: SizedBox(
            width: kPortHitSize,
            height: kPortHitSize,
            child: Center(child: dot),
          ),
        ),
      ),
    );
  }
}
