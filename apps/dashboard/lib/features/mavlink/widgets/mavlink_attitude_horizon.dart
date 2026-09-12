import 'dart:math' as math;

import 'package:flutter/material.dart';

import '../../../core/theme/tactical_theme.dart';
import '../models/mavlink_models.dart';

class MavlinkAttitudeHorizon extends StatelessWidget {
  const MavlinkAttitudeHorizon({
    super.key,
    required this.attitude,
    this.size = 120,
  });

  final MavlinkAttitude attitude;
  final double size;

  @override
  Widget build(BuildContext context) {
    return SizedBox(
      width: size,
      height: size,
      child: CustomPaint(
        painter: _HorizonPainter(attitude: attitude),
        child: Center(
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              Text(
                '${attitude.pitch.toStringAsFixed(0)}°',
                style: const TextStyle(fontSize: 9, color: TacticalColors.textSecondary),
              ),
              Text(
                'R ${attitude.roll.toStringAsFixed(0)}°',
                style: const TextStyle(
                  fontSize: 10,
                  fontWeight: FontWeight.w700,
                  color: TacticalColors.borderNeon,
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}

class _HorizonPainter extends CustomPainter {
  _HorizonPainter({required this.attitude});

  final MavlinkAttitude attitude;

  @override
  void paint(Canvas canvas, Size size) {
    final center = Offset(size.width / 2, size.height / 2);
    final radius = size.width / 2 - 4;

    canvas.save();
    canvas.clipPath(Path()..addOval(Rect.fromCircle(center: center, radius: radius)));

    canvas.translate(center.dx, center.dy);
    canvas.rotate(-attitude.roll * math.pi / 180);
    canvas.translate(0, attitude.pitch * 1.2);

    final skyPaint = Paint()..color = const Color(0xFF123047);
    final groundPaint = Paint()..color = const Color(0xFF2A2418);
    canvas.drawRect(Rect.fromLTWH(-radius * 2, -radius * 2, radius * 4, radius * 2), skyPaint);
    canvas.drawRect(Rect.fromLTWH(-radius * 2, 0, radius * 4, radius * 2), groundPaint);

    final horizonPaint = Paint()
      ..color = TacticalColors.warning
      ..strokeWidth = 2;
    canvas.drawLine(Offset(-radius, 0), Offset(radius, 0), horizonPaint);

    canvas.restore();

    final ringPaint = Paint()
      ..color = TacticalColors.borderNeon
      ..style = PaintingStyle.stroke
      ..strokeWidth = 2;
    canvas.drawCircle(center, radius, ringPaint);

    final aircraftPaint = Paint()
      ..color = TacticalColors.cyan
      ..strokeWidth = 2.5
      ..strokeCap = StrokeCap.round;
    canvas.drawLine(
      Offset(center.dx - 24, center.dy),
      Offset(center.dx + 24, center.dy),
      aircraftPaint,
    );
    canvas.drawLine(
      Offset(center.dx, center.dy - 8),
      Offset(center.dx, center.dy + 8),
      aircraftPaint,
    );

    final yawRad = attitude.yaw * math.pi / 180;
    final yawTip = center + Offset(math.sin(yawRad) * (radius - 8), -math.cos(yawRad) * (radius - 8));
    final yawPaint = Paint()
      ..color = TacticalColors.success
      ..strokeWidth = 2;
    canvas.drawLine(center, yawTip, yawPaint);
  }

  @override
  bool shouldRepaint(covariant _HorizonPainter oldDelegate) {
    return oldDelegate.attitude.roll != attitude.roll ||
        oldDelegate.attitude.pitch != attitude.pitch ||
        oldDelegate.attitude.yaw != attitude.yaw;
  }
}
