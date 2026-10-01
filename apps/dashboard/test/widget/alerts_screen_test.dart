import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';

import 'package:next_iot_dashboard/features/alerts/data/alert_repository.dart';
import 'package:next_iot_dashboard/features/alerts/models/alert_models.dart';
import 'package:next_iot_dashboard/features/alerts/providers/alert_provider.dart';
import 'package:next_iot_dashboard/features/alerts/providers/notification_channel_provider.dart';
import 'package:next_iot_dashboard/features/auth/data/permissions_repository.dart';
import 'package:next_iot_dashboard/features/auth/providers/permissions_provider.dart';
import 'package:next_iot_dashboard/features/alerts/screens/alerts_screen.dart';
import 'package:next_iot_dashboard/features/alerts/widgets/severity_badge.dart';
import 'package:next_iot_dashboard/features/devices/data/device_repository.dart';
import 'package:next_iot_dashboard/features/devices/models/device_models.dart';
import 'package:next_iot_dashboard/features/devices/providers/device_provider.dart';
import 'package:next_iot_dashboard/features/rules/data/rule_repository.dart';
import 'package:next_iot_dashboard/features/rules/models/rule_models.dart';
import 'package:next_iot_dashboard/features/rules/providers/rule_provider.dart';

class _TestAlertNotifier extends AlertNotifier {
  _TestAlertNotifier(AlertListState initial) : super(AlertRepository()) {
    state = initial;
  }

  @override
  Future<void> loadAlerts() async {}
}

class _TestRuleNotifier extends RuleNotifier {
  _TestRuleNotifier(RuleListState initial) : super(RuleRepository()) {
    state = initial;
  }

  @override
  Future<void> loadRules() async {}
}

class _TestDeviceNotifier extends DeviceNotifier {
  _TestDeviceNotifier(DeviceListState initial) : super(DeviceRepository()) {
    state = initial;
  }

  @override
  Future<void> loadDevices() async {}
}

void main() {
  final alerts = [
    DeviceAlert(
      id: 'a1',
      event: 'rule.triggered',
      deviceId: 'dev-1',
      tenantId: 't1',
      severity: AlertSeverity.critical,
      status: 'active',
      metric: 'temperature',
      operator: '>',
      threshold: 45,
      actualValue: 50,
      notificationChannel: 'telegram',
      timestamp: DateTime(2026, 9, 10, 12),
    ),
    DeviceAlert(
      id: 'a2',
      event: 'rule.triggered',
      deviceId: 'dev-2',
      tenantId: 't1',
      severity: AlertSeverity.warning,
      status: 'history',
      metric: 'humidity',
      operator: '>',
      threshold: 70,
      actualValue: 75,
      notificationChannel: 'webhook',
      timestamp: DateTime(2026, 9, 10, 11),
    ),
  ];

  final rules = [
    AlertRule(
      id: 'r1',
      tenantId: 't1',
      deviceId: 'dev-1',
      name: '[severity:critical] High temperature',
      metric: 'temperature',
      operator: '>',
      threshold: 45,
      actionType: 'alert',
      isActive: true,
      createdAt: DateTime(2026, 9, 10),
    ),
  ];

  final devices = [
    Device(
      id: 'dev-1',
      tenantId: 't1',
      name: 'Field Sensor A',
      deviceType: 'sensor',
      status: 'online',
      createdAt: DateTime(2026, 9, 1),
    ),
  ];

  Widget buildApp({Size size = const Size(1400, 900)}) {
    return ProviderScope(
      overrides: [
        permissionsProvider.overrideWith(
          (ref) => fullAccessPermissionsNotifier(
            ref.watch(permissionsRepositoryProvider),
          ),
        ),
        alertProvider.overrideWith(
          (ref) => _TestAlertNotifier(
            AlertListState(
              activeAlerts: [alerts.first],
              historyAlerts: [alerts.last],
              activeCount: 1,
            ),
          ),
        ),
        ruleProvider.overrideWith(
          (ref) => _TestRuleNotifier(RuleListState(rules: rules)),
        ),
        deviceProvider.overrideWith(
          (ref) => _TestDeviceNotifier(DeviceListState(devices: devices)),
        ),
      ],
      child: MaterialApp(
        home: MediaQuery(
          data: MediaQueryData(size: size),
          child: const Scaffold(body: AlertsScreen()),
        ),
      ),
    );
  }

  testWidgets('AlertsScreen renders alert engine header and create rule button',
      (tester) async {
    await tester.pumpWidget(buildApp());
    await tester.pumpAndSettle();

    expect(find.text('ALERT & NOTIFICATION ENGINE'), findsOneWidget);
    expect(find.text('Create New Alert Rule'), findsOneWidget);
  });

  testWidgets('AlertsScreen renders rules table and live activity feed',
      (tester) async {
    await tester.pumpWidget(buildApp());
    await tester.pumpAndSettle();

    expect(find.text('Alert Rules'), findsOneWidget);
    expect(find.text('Live Activity Feed'), findsOneWidget);
    expect(find.text('High temperature'), findsOneWidget);
    expect(find.text('Field Sensor A · Sensor'), findsOneWidget);
    expect(find.byType(SeverityBadge), findsWidgets);
    expect(find.text('temperature'), findsWidgets);
  });

  testWidgets('AlertsScreen renders notification channel toggles',
      (tester) async {
    await tester.pumpWidget(buildApp());
    await tester.pumpAndSettle();

    expect(find.text('Notification Channels'), findsOneWidget);
    expect(find.text('Telegram Bot'), findsOneWidget);
    expect(find.text('WhatsApp Webhook'), findsOneWidget);
    expect(find.text('Email Services'), findsOneWidget);
  });
}
