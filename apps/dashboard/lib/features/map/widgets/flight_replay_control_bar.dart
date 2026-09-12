import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../core/theme/tactical_theme.dart';
import '../../telemetry/providers/flight_replay_provider.dart';

class FlightReplayControlBar extends ConsumerWidget {
  const FlightReplayControlBar({super.key});

  String _formatProgress(double progress, FlightReplayState state) {
    final data = state.data;
    if (data == null) return '0%';
    final elapsed = data.duration * progress;
    final mins = elapsed.inMinutes.remainder(60).toString().padLeft(2, '0');
    final secs = elapsed.inSeconds.remainder(60).toString().padLeft(2, '0');
    return '$mins:$secs';
  }

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final replay = ref.watch(flightReplayProvider);
    if (!replay.enabled) return const SizedBox.shrink();

    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 10),
      decoration: BoxDecoration(
        color: TacticalColors.surface.withOpacity(0.95),
        border: Border(top: BorderSide(color: TacticalColors.cyan.withOpacity(0.4))),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        mainAxisSize: MainAxisSize.min,
        children: [
          Row(
            children: [
              Icon(Icons.flight_takeoff, size: 16, color: TacticalColors.cyan),
              const SizedBox(width: 6),
              Text(
                'FLIGHT REPLAY',
                style: Theme.of(context).textTheme.labelSmall?.copyWith(
                      color: TacticalColors.cyan,
                      fontWeight: FontWeight.w800,
                      letterSpacing: 1.2,
                    ),
              ),
              const Spacer(),
              if (replay.isLoading)
                const SizedBox(
                  width: 16,
                  height: 16,
                  child: CircularProgressIndicator(strokeWidth: 2),
                )
              else
                Text(
                  '${(replay.progress * 100).round()}%',
                  style: const TextStyle(fontSize: 11, color: TacticalColors.textSecondary),
                ),
              const SizedBox(width: 8),
              IconButton(
                visualDensity: VisualDensity.compact,
                tooltip: 'Close replay',
                onPressed: () => ref.read(flightReplayProvider.notifier).stop(),
                icon: const Icon(Icons.close, size: 18),
              ),
            ],
          ),
          if (replay.error != null)
            Padding(
              padding: const EdgeInsets.only(bottom: 8),
              child: Text(replay.error!, style: const TextStyle(color: TacticalColors.warning, fontSize: 11)),
            ),
          if (replay.hasData) ...[
            SliderTheme(
              data: SliderTheme.of(context).copyWith(
                trackHeight: 3,
                thumbShape: const RoundSliderThumbShape(enabledThumbRadius: 6),
              ),
              child: Slider(
                value: replay.progress.clamp(0.0, 1.0),
                onChanged: replay.isLoading ? null : ref.read(flightReplayProvider.notifier).setProgress,
                activeColor: TacticalColors.cyan,
                inactiveColor: TacticalColors.border,
              ),
            ),
            Row(
              children: [
                IconButton(
                  tooltip: replay.isPlaying ? 'Pause' : 'Play',
                  onPressed: replay.isLoading ? null : ref.read(flightReplayProvider.notifier).togglePlayPause,
                  icon: Icon(replay.isPlaying ? Icons.pause_circle_filled : Icons.play_circle_filled),
                  color: TacticalColors.cyan,
                ),
                Text(
                  _formatProgress(replay.progress, replay),
                  style: const TextStyle(fontSize: 11, fontFeatures: [FontFeature.tabularFigures()]),
                ),
                const Spacer(),
                OutlinedButton(
                  onPressed: replay.isLoading ? null : ref.read(flightReplayProvider.notifier).cycleSpeed,
                  style: OutlinedButton.styleFrom(
                    visualDensity: VisualDensity.compact,
                    foregroundColor: TacticalColors.borderNeon,
                    side: BorderSide(color: TacticalColors.borderNeon.withOpacity(0.5)),
                  ),
                  child: Text('${replay.speedMultiplier}x'),
                ),
              ],
            ),
          ],
        ],
      ),
    );
  }
}
