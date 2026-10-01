import 'dart:ui';

import 'package:flutter/material.dart';

import '../models/automation_pipeline_models.dart';

const kPipelineNodeWidth = 168.0;
const kPipelineNodeHeight = 96.0;
const kPortDotSize = 10.0;
/// Transparent 40×40 px hit-box around each port dot.
const kPortHitSize = 40.0;
const kPortHitPadding = (kPortHitSize - kPortDotSize) / 2;

class PipelinePortSnap {
  const PipelinePortSnap({required this.nodeId, required this.port});

  final String nodeId;
  final PipelinePortSide port;
}

/// Logical scene-space center for a port on a node card.
Offset pipelinePortCenter(Offset nodePosition, PipelinePortSide side) {
  switch (side) {
    case PipelinePortSide.left:
      return nodePosition + Offset(0, kPipelineNodeHeight / 2);
    case PipelinePortSide.right:
      return nodePosition + Offset(kPipelineNodeWidth, kPipelineNodeHeight / 2);
    case PipelinePortSide.top:
      return nodePosition + Offset(kPipelineNodeWidth / 2, 0);
    case PipelinePortSide.bottom:
      return nodePosition + Offset(kPipelineNodeWidth / 2, kPipelineNodeHeight);
  }
}

Offset pipelineOutputPortCenter(Offset nodePosition) =>
    pipelinePortCenter(nodePosition, PipelinePortSide.right);

Offset pipelineInputPortCenter(Offset nodePosition) =>
    pipelinePortCenter(nodePosition, PipelinePortSide.left);

PipelinePortSide closestInputPort(PipelineNodeModel node, Offset scenePoint) {
  var bestDistance = double.infinity;
  var bestPort = PipelinePortSide.left;
  for (final side in PipelinePortSide.inputPorts) {
    final distance =
        (pipelinePortCenter(node.position, side) - scenePoint).distance;
    if (distance < bestDistance) {
      bestDistance = distance;
      bestPort = side;
    }
  }
  return bestPort;
}

PipelinePortSide optimalInputPort({
  required Offset sourcePosition,
  required Offset targetNodePosition,
}) {
  final targetCenter = targetNodePosition +
      Offset(kPipelineNodeWidth / 2, kPipelineNodeHeight / 2);
  final delta = targetCenter - sourcePosition;
  final absDx = delta.dx.abs();
  final absDy = delta.dy.abs();

  if (absDx > absDy * 1.15) {
    if (delta.dx > 0) return PipelinePortSide.left;
    return delta.dy > 0 ? PipelinePortSide.bottom : PipelinePortSide.top;
  }
  return delta.dy > 0 ? PipelinePortSide.top : PipelinePortSide.bottom;
}

PipelinePortSide resolveTargetPort({
  required Offset sourcePosition,
  required PipelineNodeModel target,
  required Offset scenePoint,
  required bool pointerNearTarget,
}) {
  if (!pointerNearTarget) {
    return optimalInputPort(
      sourcePosition: sourcePosition,
      targetNodePosition: target.position,
    );
  }
  return closestInputPort(target, scenePoint);
}

Offset portControlOffset(PipelinePortSide side, double magnitude) {
  switch (side) {
    case PipelinePortSide.left:
      return Offset(-magnitude, 0);
    case PipelinePortSide.right:
      return Offset(magnitude, 0);
    case PipelinePortSide.top:
      return Offset(0, -magnitude);
    case PipelinePortSide.bottom:
      return Offset(0, magnitude);
  }
}

Path buildPipelineEdgePath(
  Offset start,
  Offset end, {
  PipelinePortSide fromPort = PipelinePortSide.right,
  PipelinePortSide toPort = PipelinePortSide.left,
}) {
  const handle = 72.0;
  final cp1 = start + portControlOffset(fromPort, handle);
  final cp2 = end + portControlOffset(toPort, handle);
  return Path()
    ..moveTo(start.dx, start.dy)
    ..cubicTo(cp1.dx, cp1.dy, cp2.dx, cp2.dy, end.dx, end.dy);
}

List<Offset> samplePipelineEdgePoints(
  Offset start,
  Offset end, {
  PipelinePortSide fromPort = PipelinePortSide.right,
  PipelinePortSide toPort = PipelinePortSide.left,
  int samples = 12,
}) {
  final path = buildPipelineEdgePath(
    start,
    end,
    fromPort: fromPort,
    toPort: toPort,
  );
  final metrics = path.computeMetrics().toList();
  if (metrics.isEmpty) return [start, end];

  final metric = metrics.first;
  final points = <Offset>[];
  for (var i = 1; i < samples; i++) {
    final t = i / samples;
    points.add(metric.getTangentForOffset(metric.length * t)!.position);
  }
  return points;
}

double distanceToPipelineEdge(
  Offset point,
  Offset start,
  Offset end, {
  PipelinePortSide fromPort = PipelinePortSide.right,
  PipelinePortSide toPort = PipelinePortSide.left,
}) {
  final samples = samplePipelineEdgePoints(
    start,
    end,
    fromPort: fromPort,
    toPort: toPort,
    samples: 24,
  );
  var best = double.infinity;
  var previous = start;
  for (final sample in [...samples, end]) {
    final segmentDistance = _distanceToSegment(point, previous, sample);
    if (segmentDistance < best) best = segmentDistance;
    previous = sample;
  }
  return best;
}

double _distanceToSegment(Offset point, Offset a, Offset b) {
  final ab = b - a;
  final lengthSquared = ab.dx * ab.dx + ab.dy * ab.dy;
  if (lengthSquared == 0) return (point - a).distance;
  final t =
      ((point.dx - a.dx) * ab.dx + (point.dy - a.dy) * ab.dy) / lengthSquared;
  final clamped = t.clamp(0.0, 1.0);
  final projection = Offset(a.dx + ab.dx * clamped, a.dy + ab.dy * clamped);
  return (point - projection).distance;
}

void drawPipelineEdgeBezier(
  Canvas canvas,
  Paint paint,
  Offset start,
  Offset end, {
  PipelinePortSide fromPort = PipelinePortSide.right,
  PipelinePortSide toPort = PipelinePortSide.left,
  bool dashed = false,
}) {
  final path = buildPipelineEdgePath(
    start,
    end,
    fromPort: fromPort,
    toPort: toPort,
  );

  if (dashed) {
    for (final metric in path.computeMetrics()) {
      var distance = 0.0;
      while (distance < metric.length) {
        final next = distance + 10;
        canvas.drawPath(
          metric.extractPath(distance, next.clamp(0, metric.length)),
          paint,
        );
        distance = next + 8;
      }
    }
  } else {
    canvas.drawPath(path, paint);
  }

  final dotPaint = Paint()
    ..color = paint.color
    ..style = PaintingStyle.fill;
  canvas.drawCircle(start, 4, dotPaint);
  canvas.drawCircle(end, 4, dotPaint);
}
