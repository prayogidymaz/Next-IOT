enum RuleOperator {
  gt('>', 'Greater than'),
  lt('<', 'Less than'),
  eq('==', 'Equal'),
  gte('>=', 'Greater or equal'),
  lte('<=', 'Less or equal');

  const RuleOperator(this.apiValue, this.label);

  final String apiValue;
  final String label;

  static RuleOperator? fromApiValue(String value) {
    for (final op in RuleOperator.values) {
      if (op.apiValue == value) return op;
    }
    return null;
  }
}

enum NotificationChannel {
  telegram('alert', 'Telegram'),
  webhook('webhook', 'Webhook');

  const NotificationChannel(this.actionType, this.label);

  final String actionType;
  final String label;
}

class AlertRule {
  const AlertRule({
    required this.id,
    required this.tenantId,
    required this.deviceId,
    required this.name,
    required this.metric,
    required this.operator,
    required this.threshold,
    required this.actionType,
    required this.isActive,
    required this.createdAt,
  });

  final String id;
  final String tenantId;
  final String deviceId;
  final String name;
  final String metric;
  final String operator;
  final double threshold;
  final String actionType;
  final bool isActive;
  final DateTime createdAt;

  NotificationChannel get channel =>
      actionType == 'webhook' ? NotificationChannel.webhook : NotificationChannel.telegram;

  factory AlertRule.fromJson(Map<String, dynamic> json) => AlertRule(
        id: json['id'] as String,
        tenantId: json['tenant_id'] as String,
        deviceId: json['device_id'] as String,
        name: json['name'] as String,
        metric: json['metric'] as String,
        operator: json['operator'] as String,
        threshold: (json['threshold'] as num).toDouble(),
        actionType: json['action_type'] as String,
        isActive: json['is_active'] as bool,
        createdAt: DateTime.parse(json['created_at'] as String),
      );
}

class CreateRuleRequest {
  const CreateRuleRequest({
    required this.deviceId,
    required this.name,
    required this.metric,
    required this.operator,
    required this.threshold,
    required this.actionType,
  });

  final String deviceId;
  final String name;
  final String metric;
  final String operator;
  final double threshold;
  final String actionType;

  Map<String, dynamic> toJson() => {
        'device_id': deviceId,
        'name': name,
        'metric': metric,
        'operator': operator,
        'threshold': threshold,
        'action_type': actionType,
        'is_active': true,
      };
}
