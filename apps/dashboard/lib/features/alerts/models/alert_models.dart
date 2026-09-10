enum AlertSeverity {
  critical,
  warning,
  info;

  static AlertSeverity fromApi(String value) {
    switch (value) {
      case 'critical':
        return AlertSeverity.critical;
      case 'warning':
        return AlertSeverity.warning;
      default:
        return AlertSeverity.info;
    }
  }

  String get label {
    switch (this) {
      case AlertSeverity.critical:
        return 'Critical';
      case AlertSeverity.warning:
        return 'Warning';
      case AlertSeverity.info:
        return 'Info';
    }
  }
}

class DeviceAlert {
  const DeviceAlert({
    required this.id,
    required this.event,
    required this.deviceId,
    required this.tenantId,
    required this.severity,
    required this.status,
    this.ruleId,
    this.metric,
    this.operator,
    this.threshold,
    this.actualValue,
    this.actionType,
    this.notificationChannel,
    this.timestamp,
  });

  final String id;
  final String event;
  final String deviceId;
  final String tenantId;
  final AlertSeverity severity;
  final String status;
  final String? ruleId;
  final String? metric;
  final String? operator;
  final double? threshold;
  final double? actualValue;
  final String? actionType;
  final String? notificationChannel;
  final DateTime? timestamp;

  bool get isActive => status == 'active';

  String get summary {
    if (metric != null && actualValue != null && threshold != null && operator != null) {
      return '$metric $operator $threshold (actual: $actualValue)';
    }
    return event;
  }

  factory DeviceAlert.fromJson(Map<String, dynamic> json) => DeviceAlert(
        id: json['id'] as String? ?? json['reading_id'] as String? ?? '',
        event: json['event'] as String? ?? 'alert',
        deviceId: json['device_id'] as String,
        tenantId: json['tenant_id'] as String,
        severity: AlertSeverity.fromApi(json['severity'] as String? ?? 'info'),
        status: json['status'] as String? ?? 'active',
        ruleId: json['rule_id'] as String?,
        metric: json['metric'] as String?,
        operator: json['operator'] as String?,
        threshold: json['threshold'] != null ? (json['threshold'] as num).toDouble() : null,
        actualValue: json['actual_value'] != null ? (json['actual_value'] as num).toDouble() : null,
        actionType: json['action_type'] as String?,
        notificationChannel: json['notification_channel'] as String?,
        timestamp: json['timestamp'] != null ? DateTime.parse(json['timestamp'] as String) : null,
      );
}

class AlertList {
  const AlertList({required this.count, required this.items});

  final int count;
  final List<DeviceAlert> items;

  factory AlertList.fromJson(Map<String, dynamic> json) {
    final items = (json['items'] as List<dynamic>)
        .map((e) => DeviceAlert.fromJson(e as Map<String, dynamic>))
        .toList();
    return AlertList(count: json['count'] as int, items: items);
  }
}

class AlertSummary {
  const AlertSummary({required this.activeCount, required this.items});

  final int activeCount;
  final List<DeviceAlert> items;

  factory AlertSummary.fromJson(Map<String, dynamic> json) => AlertSummary(
        activeCount: json['active_count'] as int,
        items: (json['items'] as List<dynamic>)
            .map((e) => DeviceAlert.fromJson(e as Map<String, dynamic>))
            .toList(),
      );
}
