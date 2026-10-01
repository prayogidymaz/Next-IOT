import 'package:flutter/material.dart';

import '../../../core/theme/tactical_theme.dart';
import '../../telemetry/models/telemetry_models.dart';

bool metricsLookLikeSmartHome(Map<String, dynamic> metrics) {
  const keys = {'relay_state', 'pir_motion', 'hvac_temp', 'lock_state'};
  return metrics.keys.any(keys.contains);
}

class SmartHomeBentoTelemetry extends StatelessWidget {
  const SmartHomeBentoTelemetry({
    super.key,
    required this.latest,
    this.onRelayToggle,
  });

  final TelemetryLatest? latest;
  final ValueChanged<bool>? onRelayToggle;

  @override
  Widget build(BuildContext context) {
    final metrics = latest?.metrics ?? {};
    final relayRaw = metrics['relay_state'];
    final relayOn = _relayIsOn(relayRaw);
    final temp = _asDouble(metrics['hvac_temp']);
    final pir = metrics['pir_motion'];
    final motion = pir == true || pir == 1 || pir == '1' || pir == 'true';

    return LayoutBuilder(
      builder: (context, constraints) {
        final wide = constraints.maxWidth >= 520;
        return Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            Text('Smart home', style: Theme.of(context).textTheme.titleMedium),
            const SizedBox(height: 14),
            if (wide)
              Row(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Expanded(child: _RelayBento(relayOn: relayOn, onToggle: onRelayToggle)),
                  const SizedBox(width: 12),
                  Expanded(child: _HvacBento(celsius: temp)),
                  const SizedBox(width: 12),
                  Expanded(child: _PirBento(motionDetected: motion)),
                ],
              )
            else ...[
              _RelayBento(relayOn: relayOn, onToggle: onRelayToggle),
              const SizedBox(height: 12),
              _HvacBento(celsius: temp),
              const SizedBox(height: 12),
              _PirBento(motionDetected: motion),
            ],
          ],
        );
      },
    );
  }

  static bool _relayIsOn(dynamic raw) {
    if (raw == null) return false;
    if (raw is bool) return raw;
    final s = raw.toString().toUpperCase();
    return s == 'ON' || s == '1' || s == 'TRUE';
  }

  static double? _asDouble(dynamic v) {
    if (v == null) return null;
    if (v is num) return v.toDouble();
    return double.tryParse(v.toString());
  }
}

class _RelayBento extends StatelessWidget {
  const _RelayBento({required this.relayOn, this.onToggle});

  final bool relayOn;
  final ValueChanged<bool>? onToggle;

  @override
  Widget build(BuildContext context) {
    return _BentoSurface(
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text('Relay', style: Theme.of(context).textTheme.titleSmall),
          const SizedBox(height: 16),
          FilledButton(
            onPressed: onToggle != null ? () => onToggle!(!relayOn) : null,
            style: FilledButton.styleFrom(
              minimumSize: const Size.fromHeight(52),
              backgroundColor: relayOn ? BentoTokens.accentLime : TacticalColors.surface,
              foregroundColor: const Color(0xFF0F1015),
              disabledBackgroundColor: TacticalColors.surface,
              disabledForegroundColor: TacticalColors.textSecondary,
            ),
            child: Text(relayOn ? 'ON · Energized' : 'OFF · Standby'),
          ),
        ],
      ),
    );
  }
}

class _HvacBento extends StatelessWidget {
  const _HvacBento({required this.celsius});

  final double? celsius;

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(22),
      decoration: BoxDecoration(
        color: BentoTokens.accentLavender.withOpacity( 0.12),
        borderRadius: BorderRadius.circular(BentoTokens.radius),
        border: Border.all(color: BentoTokens.accentLavender.withOpacity( 0.35)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text('HVAC', style: Theme.of(context).textTheme.titleSmall),
          const SizedBox(height: 12),
          Text(
            celsius != null ? '${celsius!.toStringAsFixed(1)}°' : '—°',
            style: Theme.of(context).textTheme.headlineSmall?.copyWith(
                  fontSize: 40,
                  fontWeight: FontWeight.w800,
                  color: BentoTokens.accentLavender,
                  height: 1,
                ),
          ),
          const SizedBox(height: 6),
          Text('Indoor setpoint', style: Theme.of(context).textTheme.bodySmall),
        ],
      ),
    );
  }
}

class _PirBento extends StatelessWidget {
  const _PirBento({required this.motionDetected});

  final bool motionDetected;

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(22),
      decoration: BoxDecoration(
        color: BentoTokens.accentSoftBlue.withOpacity( 0.1),
        borderRadius: BorderRadius.circular(BentoTokens.radius),
        border: Border.all(color: BentoTokens.accentSoftBlue.withOpacity( 0.35)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text('Indoor status', style: Theme.of(context).textTheme.titleSmall),
          const SizedBox(height: 16),
          Row(
            children: [
              Container(
                width: 10,
                height: 10,
                decoration: BoxDecoration(
                  shape: BoxShape.circle,
                  color: motionDetected ? BentoTokens.accentSoftBlue : TacticalColors.border,
                ),
              ),
              const SizedBox(width: 10),
              Text(
                motionDetected ? 'PIR motion detected' : 'No motion',
                style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                      color: TacticalColors.textPrimary,
                    ),
              ),
            ],
          ),
        ],
      ),
    );
  }
}

class _BentoSurface extends StatelessWidget {
  const _BentoSurface({required this.child});

  final Widget child;

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(22),
      decoration: BoxDecoration(
        color: TacticalColors.surfaceElevated,
        borderRadius: BorderRadius.circular(BentoTokens.radius),
        border: Border.all(color: TacticalColors.border.withOpacity( 0.7)),
      ),
      child: child,
    );
  }
}
