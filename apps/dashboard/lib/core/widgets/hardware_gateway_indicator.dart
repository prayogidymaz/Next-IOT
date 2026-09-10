import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../features/hardware/models/gateway_models.dart';
import '../../features/hardware/providers/gateway_provider.dart';
import '../theme/tactical_theme.dart';

class HardwareGatewayIndicator extends ConsumerWidget {
  const HardwareGatewayIndicator({super.key, this.compact = false});

  final bool compact;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final status = ref.watch(gatewayStatusProvider);
    final linkColor = status.isLinkHealthy ? TacticalColors.success : TacticalColors.critical;

    if (compact) {
      return _CompactGatewayBadge(status: status, linkColor: linkColor);
    }

    return Row(
      mainAxisSize: MainAxisSize.min,
      children: [
        _SerialBadge(connected: status.serialConnected, port: status.serialPort),
        const SizedBox(width: 10),
        _LoRaBadge(status: status, linkColor: linkColor),
        const SizedBox(width: 10),
        _SignalMeter(rssi: status.rssi, snr: status.snr),
      ],
    );
  }
}

class _CompactGatewayBadge extends StatelessWidget {
  const _CompactGatewayBadge({required this.status, required this.linkColor});

  final GatewayStatus status;
  final Color linkColor;

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
      decoration: BoxDecoration(
        color: TacticalColors.background,
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: linkColor.withOpacity(0.45)),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Icon(Icons.usb, size: 12, color: status.serialConnected ? TacticalColors.success : TacticalColors.textSecondary),
          const SizedBox(width: 4),
          Icon(Icons.settings_input_antenna, size: 12, color: linkColor),
        ],
      ),
    );
  }
}

class _SerialBadge extends StatelessWidget {
  const _SerialBadge({required this.connected, this.port});

  final bool connected;
  final String? port;

  @override
  Widget build(BuildContext context) {
    final color = connected ? TacticalColors.success : TacticalColors.textSecondary;
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
      decoration: BoxDecoration(
        color: TacticalColors.background,
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: color.withOpacity(0.4)),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Icon(Icons.usb, size: 12, color: color),
          const SizedBox(width: 4),
          Text(
            connected ? 'SERIAL ${port ?? 'OK'}' : 'SERIAL OFF',
            style: TextStyle(color: color, fontSize: 10, fontWeight: FontWeight.w700),
          ),
        ],
      ),
    );
  }
}

class _LoRaBadge extends StatelessWidget {
  const _LoRaBadge({required this.status, required this.linkColor});

  final GatewayStatus status;
  final Color linkColor;

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
      decoration: BoxDecoration(
        color: TacticalColors.background,
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: linkColor.withOpacity(0.4)),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Icon(Icons.settings_input_antenna, size: 12, color: linkColor),
          const SizedBox(width: 4),
          Text(
            'LoRa ${status.loraLink.toUpperCase()}',
            style: TextStyle(color: linkColor, fontSize: 10, fontWeight: FontWeight.w700),
          ),
        ],
      ),
    );
  }
}

class _SignalMeter extends StatelessWidget {
  const _SignalMeter({this.rssi, this.snr});

  final double? rssi;
  final double? snr;

  @override
  Widget build(BuildContext context) {
    final rssiValue = rssi ?? -999.0;
    final bars = rssiValue >= -70 ? 4 : rssiValue >= -80 ? 3 : rssiValue >= -90 ? 2 : rssiValue > -999 ? 1 : 0;
    final color = bars >= 3 ? TacticalColors.success : bars >= 2 ? TacticalColors.warning : TacticalColors.critical;

    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
      decoration: BoxDecoration(
        color: TacticalColors.background,
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: color.withOpacity(0.4)),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          for (var i = 0; i < 4; i++)
            Container(
              width: 3,
              height: 6 + i * 3,
              margin: const EdgeInsets.only(right: 2),
              decoration: BoxDecoration(
                color: i < bars ? color : TacticalColors.border,
                borderRadius: BorderRadius.circular(1),
              ),
            ),
          const SizedBox(width: 4),
          Text(
            rssi != null ? '${rssi!.round()} dBm' : 'NO SIG',
            style: TextStyle(color: color, fontSize: 10, fontWeight: FontWeight.w700),
          ),
          if (snr != null) ...[
            const SizedBox(width: 6),
            Text('SNR ${snr!.toStringAsFixed(1)}', style: Theme.of(context).textTheme.bodySmall?.copyWith(fontSize: 10)),
          ],
        ],
      ),
    );
  }
}
