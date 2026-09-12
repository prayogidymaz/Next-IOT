import 'package:flutter/material.dart';

import '../../../core/theme/tactical_theme.dart';
import '../models/video_feed_models.dart';

class AiDetectionOverlay extends StatelessWidget {
  const AiDetectionOverlay({
    super.key,
    required this.detections,
    this.showLabels = true,
  });

  final List<AiDetectionBox> detections;
  final bool showLabels;

  @override
  Widget build(BuildContext context) {
    return LayoutBuilder(
      builder: (context, constraints) {
        return CustomPaint(
          size: Size(constraints.maxWidth, constraints.maxHeight),
          painter: _AiDetectionPainter(
            detections: detections,
            showLabels: showLabels,
          ),
        );
      },
    );
  }
}

class _AiDetectionPainter extends CustomPainter {
  _AiDetectionPainter({required this.detections, required this.showLabels});

  final List<AiDetectionBox> detections;
  final bool showLabels;

  @override
  void paint(Canvas canvas, Size size) {
    for (final detection in detections) {
      if (detection.bbox.length != 4) continue;
      final x = detection.bbox[0] * size.width;
      final y = detection.bbox[1] * size.height;
      final w = detection.bbox[2] * size.width;
      final h = detection.bbox[3] * size.height;
      final rect = Rect.fromLTWH(x, y, w, h);

      final isPerson = detection.targetType == 'person';
      final color = isPerson ? TacticalColors.cyan : TacticalColors.warning;

      final boxPaint = Paint()
        ..color = color
        ..style = PaintingStyle.stroke
        ..strokeWidth = 2;
      canvas.drawRect(rect, boxPaint);

      final cornerLen = (w.clamp(12, 40)) * 0.25;
      final cornerPaint = Paint()
        ..color = color
        ..strokeWidth = 3
        ..style = PaintingStyle.stroke;
      _drawCorner(canvas, Offset(x, y), cornerLen, cornerPaint, top: true, left: true);
      _drawCorner(canvas, Offset(x + w, y), cornerLen, cornerPaint, top: true, left: false);
      _drawCorner(canvas, Offset(x, y + h), cornerLen, cornerPaint, top: false, left: true);
      _drawCorner(canvas, Offset(x + w, y + h), cornerLen, cornerPaint, top: false, left: false);

      if (showLabels) {
        final label = '${detection.targetType.toUpperCase()} ${(detection.confidence * 100).round()}%';
        final textPainter = TextPainter(
          text: TextSpan(
            text: label,
            style: TextStyle(
              color: Colors.white,
              fontSize: 10,
              fontWeight: FontWeight.w800,
              backgroundColor: color.withOpacity(0.85),
            ),
          ),
          textDirection: TextDirection.ltr,
        )..layout();
        textPainter.paint(canvas, Offset(x, (y - textPainter.height).clamp(0, size.height - textPainter.height)));
      }
    }
  }

  void _drawCorner(
    Canvas canvas,
    Offset origin,
    double len,
    Paint paint, {
    required bool top,
    required bool left,
  }) {
    final dx = left ? 1.0 : -1.0;
    final dy = top ? 1.0 : -1.0;
    canvas.drawLine(origin, origin + Offset(len * dx, 0), paint);
    canvas.drawLine(origin, origin + Offset(0, len * dy), paint);
  }

  @override
  bool shouldRepaint(covariant _AiDetectionPainter oldDelegate) {
    return oldDelegate.detections != detections;
  }
}
