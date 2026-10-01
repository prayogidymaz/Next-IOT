class SystemHealthSnapshot {
  SystemHealthSnapshot({
    required this.status,
    required this.database,
    required this.redisCache,
    required this.mqttBroker,
    this.cpuPercent,
    this.memoryPercent,
  });

  final String status;
  final String database;
  final String redisCache;
  final String mqttBroker;
  final double? cpuPercent;
  final double? memoryPercent;

  bool get isReady => status == 'ready';

  bool componentOk(String value) => value == 'ok' || value == 'standby';

  factory SystemHealthSnapshot.fromJson(Map<String, dynamic> json) {
    final components = json['components'] as Map<String, dynamic>? ?? {};
    final metrics = json['system_metrics'] as Map<String, dynamic>? ?? {};
    return SystemHealthSnapshot(
      status: json['status'] as String? ?? 'degraded',
      database: components['database'] as String? ?? 'fail',
      redisCache: components['redis_cache'] as String? ?? 'fail',
      mqttBroker: components['mqtt_broker'] as String? ?? 'fail',
      cpuPercent: (metrics['cpu_percent'] as num?)?.toDouble(),
      memoryPercent: (metrics['memory_percent'] as num?)?.toDouble(),
    );
  }
}
