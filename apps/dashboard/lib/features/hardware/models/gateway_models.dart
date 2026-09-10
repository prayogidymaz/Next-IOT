class GatewayStatus {
  const GatewayStatus({
    required this.serialConnected,
    this.serialPort,
    required this.loraLink,
    this.lastPacketAt,
    this.nodeId,
    this.rssi,
    this.snr,
    required this.packetsReceived,
    this.updatedAt,
  });

  final bool serialConnected;
  final String? serialPort;
  final String loraLink;
  final String? lastPacketAt;
  final String? nodeId;
  final double? rssi;
  final double? snr;
  final int packetsReceived;
  final String? updatedAt;

  bool get isLinkHealthy =>
      serialConnected && (loraLink == 'connected' || loraLink == 'starting');

  factory GatewayStatus.fromJson(Map<String, dynamic> json) => GatewayStatus(
        serialConnected: json['serial_connected'] as bool? ?? false,
        serialPort: json['serial_port'] as String?,
        loraLink: json['lora_link'] as String? ?? 'disconnected',
        lastPacketAt: json['last_packet_at'] as String?,
        nodeId: json['node_id'] as String?,
        rssi: (json['rssi'] as num?)?.toDouble(),
        snr: (json['snr'] as num?)?.toDouble(),
        packetsReceived: json['packets_received'] as int? ?? 0,
        updatedAt: json['updated_at'] as String?,
      );

  static const disconnected = GatewayStatus(
    serialConnected: false,
    loraLink: 'disconnected',
    packetsReceived: 0,
  );
}
