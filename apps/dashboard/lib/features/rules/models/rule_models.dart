import '../../alerts/models/alert_models.dart';

enum AlertRuleSeverity {
  critical,
  warning,
  info;

  String get label => switch (this) {
        AlertRuleSeverity.critical => 'Critical',
        AlertRuleSeverity.warning => 'Warning',
        AlertRuleSeverity.info => 'Info',
      };

  AlertSeverity get toAlertSeverity => switch (this) {
        AlertRuleSeverity.critical => AlertSeverity.critical,
        AlertRuleSeverity.warning => AlertSeverity.warning,
        AlertRuleSeverity.info => AlertSeverity.info,
      };

  static AlertRuleSeverity fromKey(String key) => switch (key.toLowerCase()) {
        'critical' => AlertRuleSeverity.critical,
        'warning' => AlertRuleSeverity.warning,
        _ => AlertRuleSeverity.info,
      };

  static AlertRuleSeverity inferFromMetric(String metric) {
    final m = metric.toLowerCase();
    if (m.contains('voltage') ||
        m.contains('battery') ||
        m.contains('geofence') ||
        m.contains('breach')) {
      return AlertRuleSeverity.critical;
    }
    if (m.contains('temp') ||
        m.contains('wind') ||
        m.contains('humid') ||
        m.contains('pressure')) {
      return AlertRuleSeverity.warning;
    }
    return AlertRuleSeverity.info;
  }

  static String encodeName(String name, AlertRuleSeverity severity) =>
      '[severity:${severity.name}] $name';
}

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
  telegram('alert', 'Telegram Bot'),
  webhook('webhook', 'WhatsApp Webhook'),
  email('email', 'Email Services');

  const NotificationChannel(this.actionType, this.label);

  final String actionType;
  final String label;

  /// Backend-supported channels for rule dispatch.
  static const apiChannels = [telegram, webhook];
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

  NotificationChannel get channel => switch (actionType) {
        'webhook' => NotificationChannel.webhook,
        'email' => NotificationChannel.email,
        _ => NotificationChannel.telegram,
      };

  static final _severityPrefix =
      RegExp(r'^\[severity:(critical|warning|info)\]\s*(.*)$', caseSensitive: false);

  String get displayName {
    final match = _severityPrefix.firstMatch(name);
    return match?.group(2)?.trim().isNotEmpty == true ? match!.group(2)! : name;
  }

  /// Parsed from encoded rule name or inferred from metric.
  AlertRuleSeverity get severity {
    final match = _severityPrefix.firstMatch(name);
    if (match != null) {
      return AlertRuleSeverity.fromKey(match.group(1)!);
    }
    return AlertRuleSeverity.inferFromMetric(metric);
  }

  String get thresholdLabel => '$metric $operator $threshold';

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
    this.severity = AlertRuleSeverity.warning,
  });

  final String deviceId;
  final String name;
  final String metric;
  final String operator;
  final double threshold;
  final String actionType;
  final AlertRuleSeverity severity;

  Map<String, dynamic> toJson() => {
        'device_id': deviceId,
        'name': AlertRuleSeverity.encodeName(name, severity),
        'metric': metric,
        'operator': operator,
        'threshold': threshold,
        'action_type': actionType,
        'is_active': true,
      };
}
