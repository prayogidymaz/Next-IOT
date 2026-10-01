import 'package:flutter/material.dart';

import '../models/cyberdeck_models.dart';
import '../theme/cyberdeck_theme.dart';

class CyberdeckMeshPanel extends StatelessWidget {
  const CyberdeckMeshPanel({
    super.key,
    required this.nodes,
    required this.selectedNodeId,
    required this.onSelect,
    this.expand = false,
  });

  final List<CyberdeckMeshNode> nodes;
  final String? selectedNodeId;
  final ValueChanged<String?> onSelect;
  final bool expand;

  Color _signalColor(double? rssi) {
    if (rssi == null) return CyberdeckColors.muted;
    if (rssi > -85) return CyberdeckColors.green;
    if (rssi >= -105) return CyberdeckColors.amber;
    return CyberdeckColors.red;
  }

  @override
  Widget build(BuildContext context) {
    return Container(
      key: const Key('cyberdeck-mesh-panel'),
      padding: const EdgeInsets.all(14),
      decoration: BoxDecoration(
        color: CyberdeckColors.panel,
        border: Border.all(color: CyberdeckColors.border),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          const Text('NODE MESH TRACKER', style: TextStyle(color: CyberdeckColors.amber, fontWeight: FontWeight.bold)),
          const SizedBox(height: 8),
          if (expand)
            Expanded(child: _nodeList())
          else
            _nodeList(shrinkWrap: true),
        ],
      ),
    );
  }

  Widget _nodeList({bool shrinkWrap = false}) {
    return ListView.separated(
      shrinkWrap: shrinkWrap,
      physics: shrinkWrap ? const ClampingScrollPhysics() : null,
      itemCount: nodes.length,
      separatorBuilder: (_, __) => const Divider(color: CyberdeckColors.border, height: 12),
      itemBuilder: (context, index) {
        final node = nodes[index];
        final selected = node.nodeId == selectedNodeId;
        final sig = _signalColor(node.rssi);
        return InkWell(
          onTap: () => onSelect(node.nodeId),
          child: Container(
            padding: const EdgeInsets.all(8),
            decoration: BoxDecoration(
              border: Border.all(color: selected ? CyberdeckColors.green : Colors.transparent),
            ),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(node.label, style: const TextStyle(fontWeight: FontWeight.w700)),
                Text(
                  '${node.nodeId} • ${node.deviceType.toUpperCase()}',
                  style: const TextStyle(color: CyberdeckColors.muted, fontSize: 11),
                ),
                const SizedBox(height: 4),
                Text(
                  'RSSI ${node.rssi?.toStringAsFixed(0) ?? '—'} dBm • SNR ${node.snr?.toStringAsFixed(1) ?? '—'} dB • BATT ${node.batteryPct?.toStringAsFixed(0) ?? '—'}%',
                  style: TextStyle(color: sig, fontSize: 11),
                ),
              ],
            ),
          ),
        );
      },
    );
  }
}
