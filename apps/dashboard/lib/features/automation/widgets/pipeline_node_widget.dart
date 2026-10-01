import 'package:flutter/gestures.dart';
import 'package:flutter/material.dart';

import '../../../core/theme/tactical_theme.dart';
import '../models/automation_pipeline_models.dart';
import 'pipeline_port_widget.dart';
import 'pipeline_ports.dart';

export 'pipeline_ports.dart' show kPipelineNodeWidth, kPipelineNodeHeight;

class PipelineNodeWidget extends StatefulWidget {
  const PipelineNodeWidget({
    super.key,
    required this.node,
    required this.selected,
    required this.connecting,
    required this.onDelete,
    required this.onConfigure,
    required this.onDragDelta,
    required this.onPortTap,
    required this.onSelect,
    this.onPortPointerDown,
    this.onPortPointerUp,
    this.wiringSourcePort,
    this.highlightedPort,
    this.connectedPorts = const {},
  });

  final PipelineNodeModel node;
  final bool selected;
  final bool connecting;
  final VoidCallback onDelete;
  final VoidCallback onConfigure;
  final ValueChanged<Offset> onDragDelta;
  final ValueChanged<PipelinePortSide> onPortTap;
  final VoidCallback onSelect;
  final void Function(PipelinePortSide side, PointerDownEvent event)?
      onPortPointerDown;
  final void Function(PipelinePortSide side, PointerUpEvent event)?
      onPortPointerUp;
  final PipelinePortSide? wiringSourcePort;
  final PipelinePortSide? highlightedPort;
  final Set<PipelinePortSide> connectedPorts;

  @override
  State<PipelineNodeWidget> createState() => _PipelineNodeWidgetState();
}

class _PipelineNodeWidgetState extends State<PipelineNodeWidget> {
  bool _dragging = false;

  Color get _accent {
    return switch (widget.node.type) {
      PipelineNodeType.trigger => TacticalColors.info,
      PipelineNodeType.condition => TacticalColors.warning,
      PipelineNodeType.action => TacticalColors.success,
    };
  }

  IconData get _icon {
    return switch (widget.node.type) {
      PipelineNodeType.trigger => Icons.flash_on,
      PipelineNodeType.condition => Icons.filter_alt,
      PipelineNodeType.action => Icons.play_circle,
    };
  }

  void _onPanStart(DragStartDetails _) {
    _dragging = false;
    widget.onSelect();
  }

  void _onPanUpdate(DragUpdateDetails details) {
    if (!_dragging && details.delta.distanceSquared > 4) {
      _dragging = true;
    }
    if (_dragging) widget.onDragDelta(details.delta);
  }

  void _onPanEnd(DragEndDetails _) {
    _dragging = false;
  }

  Widget _buildPort(PipelinePortSide side) {
    final connected = widget.connectedPorts.contains(side);

    final label = switch (side) {
      PipelinePortSide.left => 'Port left — drag or click to connect',
      PipelinePortSide.top => 'Port top — drag or click to connect',
      PipelinePortSide.bottom => 'Port bottom — drag or click to connect',
      PipelinePortSide.right => 'Port right — drag or click to connect',
    };

    return PipelinePortWidget(
      key: Key('pipeline-port-${side.name}-${widget.node.id}'),
      side: side,
      label: label,
      color: _accent,
      connected: connected,
      isWiringSource: widget.wiringSourcePort == side,
      isTargetHighlight: widget.highlightedPort == side,
      onTap: () => widget.onPortTap(side),
      onPointerDown: widget.onPortPointerDown == null
          ? null
          : (event) => widget.onPortPointerDown!(side, event),
      onPointerUp: widget.onPortPointerUp == null
          ? null
          : (event) => widget.onPortPointerUp!(side, event),
    );
  }

  @override
  Widget build(BuildContext context) {
    final halfHit = kPortHitSize / 2;

    return SizedBox(
      width: kPipelineNodeWidth,
      height: kPipelineNodeHeight,
      child: Stack(
        clipBehavior: Clip.none,
        children: [
          Positioned.fill(
            child: GestureDetector(
              key: const Key('pipeline-node-body'),
              behavior: HitTestBehavior.opaque,
              onPanStart: _onPanStart,
              onPanUpdate: _onPanUpdate,
              onPanEnd: _onPanEnd,
              onDoubleTap: widget.onConfigure,
              child: Container(
                decoration: BoxDecoration(
                  color: TacticalColors.surfaceElevated,
                  borderRadius: BorderRadius.circular(10),
                  border: Border.all(
                    color: widget.selected || widget.connecting
                        ? _accent
                        : TacticalColors.border,
                    width: widget.selected || widget.connecting ? 2 : 1,
                  ),
                  boxShadow: widget.selected
                      ? [
                          BoxShadow(
                            color: _accent.withOpacity(0.25),
                            blurRadius: 12,
                          ),
                        ]
                      : null,
                ),
                padding: const EdgeInsets.fromLTRB(12, 10, 12, 8),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Row(
                      children: [
                        Icon(_icon, size: 16, color: _accent),
                        const SizedBox(width: 6),
                        Expanded(
                          child: Text(
                            widget.node.type.name.toUpperCase(),
                            style: Theme.of(context)
                                .textTheme
                                .labelSmall
                                ?.copyWith(
                                  color: _accent,
                                  letterSpacing: 0.6,
                                ),
                          ),
                        ),
                        GestureDetector(
                          onTap: widget.onDelete,
                          child: const Icon(
                            Icons.close,
                            size: 16,
                            color: TacticalColors.textSecondary,
                          ),
                        ),
                      ],
                    ),
                    const SizedBox(height: 6),
                    Text(
                      widget.node.label,
                      maxLines: 2,
                      overflow: TextOverflow.ellipsis,
                      style: Theme.of(context).textTheme.bodySmall?.copyWith(
                            color: TacticalColors.textPrimary,
                            fontWeight: FontWeight.w600,
                          ),
                    ),
                  ],
                ),
              ),
            ),
          ),
          Positioned(
            left: -halfHit,
            top: kPipelineNodeHeight / 2 - halfHit,
            child: _buildPort(PipelinePortSide.left),
          ),
          Positioned(
            left: kPipelineNodeWidth / 2 - halfHit,
            top: -halfHit,
            child: _buildPort(PipelinePortSide.top),
          ),
          Positioned(
            left: kPipelineNodeWidth / 2 - halfHit,
            top: kPipelineNodeHeight - halfHit,
            child: _buildPort(PipelinePortSide.bottom),
          ),
          Positioned(
            left: kPipelineNodeWidth - halfHit,
            top: kPipelineNodeHeight / 2 - halfHit,
            child: _buildPort(PipelinePortSide.right),
          ),
        ],
      ),
    );
  }
}
