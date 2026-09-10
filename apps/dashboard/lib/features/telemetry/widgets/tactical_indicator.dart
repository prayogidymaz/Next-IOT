import 'package:flutter/material.dart';

import '../models/telemetry_models.dart';

class TacticalIndicator extends StatelessWidget {
  const TacticalIndicator({
    super.key,
    required this.latest,
    required this.deviceName,
    required this.deviceStatusLabel,
  });

  final TelemetryLatest? latest;
  final String deviceName;
  final String deviceStatusLabel;

  @override
  Widget build(BuildContext context) {
    final metrics = latest?.metrics ?? {};
    final lat = metrics['latitude'];
    final lon = metrics['longitude'];
    final alt = metrics['altitude_m'];
    final hasFix = lat != null && lon != null;
    final recordedAt = latest?.recordedAt;

    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: const Color(0xFF1B2A1F),
        borderRadius: BorderRadius.circular(8),
        border: Border.all(color: const Color(0xFF3D5C45)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Icon(Icons.radar, color: Colors.greenAccent.shade400, size: 20),
              const SizedBox(width: 8),
              Text(
                'TACTICAL TELEMETRY',
                style: TextStyle(
                  color: Colors.greenAccent.shade200,
                  letterSpacing: 1.2,
                  fontWeight: FontWeight.bold,
                  fontSize: 12,
                ),
              ),
              const Spacer(),
              _StatusPill(label: deviceStatusLabel),
            ],
          ),
          const SizedBox(height: 12),
          Text(deviceName, style: const TextStyle(color: Colors.white, fontSize: 16, fontWeight: FontWeight.w600)),
          const SizedBox(height: 12),
          _Row(label: 'GPS FIX', value: hasFix ? 'LOCKED' : 'NO FIX', highlight: hasFix),
          _Row(
            label: 'COORDINATES',
            value: hasFix ? '${lat!.toStringAsFixed(6)}, ${lon!.toStringAsFixed(6)}' : '—',
          ),
          _Row(label: 'ALTITUDE', value: alt != null ? '${alt.toStringAsFixed(1)} m' : '—'),
          _Row(
            label: 'LAST TELEMETRY',
            value: recordedAt != null ? recordedAt.toLocal().toString().split('.').first : '—',
          ),
          _Row(label: 'SOURCE', value: latest?.source.toUpperCase() ?? '—'),
        ],
      ),
    );
  }
}

class _StatusPill extends StatelessWidget {
  const _StatusPill({required this.label});

  final String label;

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
      decoration: BoxDecoration(
        color: Colors.green.withOpacity(0.2),
        borderRadius: BorderRadius.circular(4),
        border: Border.all(color: Colors.greenAccent.shade400),
      ),
      child: Text(
        label.toUpperCase(),
        style: TextStyle(color: Colors.greenAccent.shade200, fontSize: 10, fontWeight: FontWeight.bold),
      ),
    );
  }
}

class _Row extends StatelessWidget {
  const _Row({required this.label, required this.value, this.highlight = false});

  final String label;
  final String value;
  final bool highlight;

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 6),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          SizedBox(
            width: 120,
            child: Text(
              label,
              style: TextStyle(color: Colors.green.shade200, fontSize: 11, letterSpacing: 0.8),
            ),
          ),
          Expanded(
            child: Text(
              value,
              style: TextStyle(
                color: highlight ? Colors.greenAccent.shade100 : Colors.white70,
                fontSize: 12,
                fontFamily: 'monospace',
              ),
            ),
          ),
        ],
      ),
    );
  }
}
