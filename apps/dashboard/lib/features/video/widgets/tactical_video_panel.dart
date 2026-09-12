import 'package:flutter/material.dart';

import '../../../core/theme/tactical_theme.dart';
import '../models/video_feed_models.dart';
import 'ai_detection_overlay.dart';

class TacticalVideoPanel extends StatelessWidget {
  const TacticalVideoPanel({
    super.key,
    required this.streamInfo,
    required this.currentFrame,
    this.isConnecting = false,
    this.onToggleLayout,
    this.onClose,
    this.compact = false,
  });

  final VideoStreamInfo? streamInfo;
  final VideoFrameMessage? currentFrame;
  final bool isConnecting;
  final VoidCallback? onToggleLayout;
  final VoidCallback? onClose;
  final bool compact;

  @override
  Widget build(BuildContext context) {
    final frame = currentFrame;
    final detections = frame?.detections ?? const [];

    return Container(
      decoration: BoxDecoration(
        color: Colors.black,
        borderRadius: BorderRadius.circular(compact ? 10 : 12),
        border: Border.all(color: TacticalColors.cyan.withOpacity(0.6), width: compact ? 1.5 : 2),
        boxShadow: [
          BoxShadow(color: TacticalColors.cyan.withOpacity(0.15), blurRadius: 16),
        ],
      ),
      clipBehavior: Clip.antiAlias,
      child: Stack(
        fit: StackFit.expand,
        children: [
          _VideoPlaceholder(frameIndex: frame?.frameIndex ?? 0, isConnecting: isConnecting),
          if (detections.isNotEmpty)
            AiDetectionOverlay(detections: detections),
          Positioned(
            top: 8,
            left: 8,
            right: 8,
            child: Row(
              children: [
                _LiveBadge(isConnecting: isConnecting),
                const SizedBox(width: 8),
                Expanded(
                  child: Text(
                    streamInfo != null
                        ? '${streamInfo!.streamProtocol}/${streamInfo!.codec} · ${streamInfo!.resolution}'
                        : 'AWAITING STREAM',
                    style: const TextStyle(color: TacticalColors.textSecondary, fontSize: 10),
                    overflow: TextOverflow.ellipsis,
                  ),
                ),
                if (onToggleLayout != null)
                  IconButton(
                    visualDensity: VisualDensity.compact,
                    padding: EdgeInsets.zero,
                    constraints: const BoxConstraints(minWidth: 28, minHeight: 28),
                    tooltip: 'Toggle PiP / Split',
                    onPressed: onToggleLayout,
                    icon: Icon(
                      compact ? Icons.view_agenda_outlined : Icons.picture_in_picture_alt_outlined,
                      size: 16,
                      color: TacticalColors.cyan,
                    ),
                  ),
                if (onClose != null)
                  IconButton(
                    visualDensity: VisualDensity.compact,
                    padding: EdgeInsets.zero,
                    constraints: const BoxConstraints(minWidth: 28, minHeight: 28),
                    tooltip: 'Close HUD',
                    onPressed: onClose,
                    icon: const Icon(Icons.close, size: 16, color: TacticalColors.textSecondary),
                  ),
              ],
            ),
          ),
          if (frame != null)
            Positioned(
              bottom: 8,
              right: 8,
              child: Container(
                padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
                decoration: BoxDecoration(
                  color: Colors.black54,
                  borderRadius: BorderRadius.circular(4),
                ),
                child: Text(
                  'F${frame.frameIndex} · ${detections.length} AI',
                  style: const TextStyle(fontSize: 9, color: TacticalColors.borderNeon),
                ),
              ),
            ),
        ],
      ),
    );
  }
}

class _LiveBadge extends StatelessWidget {
  const _LiveBadge({required this.isConnecting});

  final bool isConnecting;

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
      decoration: BoxDecoration(
        color: (isConnecting ? TacticalColors.warning : TacticalColors.critical).withOpacity(0.85),
        borderRadius: BorderRadius.circular(4),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Icon(
            isConnecting ? Icons.sync : Icons.fiber_manual_record,
            size: 10,
            color: Colors.white,
          ),
          const SizedBox(width: 4),
          Text(
            isConnecting ? 'CONNECT' : 'LIVE',
            style: const TextStyle(color: Colors.white, fontSize: 9, fontWeight: FontWeight.w800),
          ),
        ],
      ),
    );
  }
}

class _VideoPlaceholder extends StatelessWidget {
  const _VideoPlaceholder({required this.frameIndex, required this.isConnecting});

  final int frameIndex;
  final bool isConnecting;

  @override
  Widget build(BuildContext context) {
    return CustomPaint(
      painter: _TacticalFeedPainter(frameIndex: frameIndex, isConnecting: isConnecting),
      child: Center(
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Icon(
              Icons.videocam,
              color: TacticalColors.cyan.withOpacity(0.35),
              size: 36,
            ),
            const SizedBox(height: 6),
            Text(
              isConnecting ? 'BUFFERING RTSP...' : 'TACTICAL VIDEO FEED',
              style: TextStyle(
                color: TacticalColors.cyan.withOpacity(0.55),
                fontSize: 10,
                fontWeight: FontWeight.w700,
                letterSpacing: 1.1,
              ),
            ),
          ],
        ),
      ),
    );
  }
}

class _TacticalFeedPainter extends CustomPainter {
  _TacticalFeedPainter({required this.frameIndex, required this.isConnecting});

  final int frameIndex;
  final bool isConnecting;

  @override
  void paint(Canvas canvas, Size size) {
    final bg = Paint()..color = const Color(0xFF0A1218);
    canvas.drawRect(Offset.zero & size, bg);

    final gridPaint = Paint()
      ..color = TacticalColors.cyan.withOpacity(0.08)
      ..strokeWidth = 1;
    const step = 24.0;
    for (var x = 0.0; x < size.width; x += step) {
      canvas.drawLine(Offset(x, 0), Offset(x, size.height), gridPaint);
    }
    for (var y = 0.0; y < size.height; y += step) {
      canvas.drawLine(Offset(0, y), Offset(size.width, y), gridPaint);
    }

    if (!isConnecting) {
      final scanY = (frameIndex * 7.0) % size.height;
      final scanPaint = Paint()
        ..color = TacticalColors.cyan.withOpacity(0.12)
        ..strokeWidth = 2;
      canvas.drawLine(Offset(0, scanY), Offset(size.width, scanY), scanPaint);
    }
  }

  @override
  bool shouldRepaint(covariant _TacticalFeedPainter oldDelegate) {
    return oldDelegate.frameIndex != frameIndex || oldDelegate.isConnecting != isConnecting;
  }
}
