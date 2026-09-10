import 'package:flutter_test/flutter_test.dart';
import 'package:next_iot_dashboard/features/alerts/models/alert_models.dart';
import 'package:next_iot_dashboard/features/rules/models/rule_models.dart';

void main() {
  group('AlertRule.fromJson', () {
    test('parses rule response', () {
      final rule = AlertRule.fromJson({
        'id': 'r1',
        'tenant_id': 't1',
        'device_id': 'd1',
        'name': 'High temp',
        'metric': 'temperature',
        'operator': '>',
        'threshold': 45.0,
        'action_type': 'alert',
        'is_active': true,
        'created_at': '2026-09-10T10:00:00Z',
      });

      expect(rule.name, 'High temp');
      expect(rule.channel, NotificationChannel.telegram);
    });
  });

  group('CreateRuleRequest.toJson', () {
    test('maps channel to action_type', () {
      const req = CreateRuleRequest(
        deviceId: 'd1',
        name: 'Webhook rule',
        metric: 'temperature',
        operator: '>',
        threshold: 45,
        actionType: 'webhook',
      );
      expect(req.toJson()['action_type'], 'webhook');
    });
  });

  group('DeviceAlert.fromJson', () {
    test('parses alert with severity', () {
      final alert = DeviceAlert.fromJson({
        'id': 'a1',
        'event': 'rule.triggered',
        'device_id': 'd1',
        'tenant_id': 't1',
        'metric': 'temperature',
        'operator': '>',
        'threshold': 45,
        'actual_value': 50,
        'severity': 'critical',
        'status': 'active',
        'notification_channel': 'telegram',
        'timestamp': '2026-09-10T10:00:00Z',
      });

      expect(alert.severity, AlertSeverity.critical);
      expect(alert.isActive, isTrue);
      expect(alert.summary, contains('50'));
    });
  });
}
