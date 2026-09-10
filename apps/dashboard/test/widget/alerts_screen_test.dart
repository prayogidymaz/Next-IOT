import 'package:flutter/material.dart';

import 'package:flutter_riverpod/flutter_riverpod.dart';

import 'package:flutter_test/flutter_test.dart';

import 'package:next_iot_dashboard/features/alerts/data/alert_repository.dart';

import 'package:next_iot_dashboard/features/alerts/models/alert_models.dart';

import 'package:next_iot_dashboard/features/alerts/providers/alert_provider.dart';

import 'package:next_iot_dashboard/features/alerts/screens/alerts_screen.dart';

import 'package:next_iot_dashboard/features/alerts/widgets/severity_badge.dart';

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

      status: 'active',

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

      name: 'High temperature',

      metric: 'temperature',

      operator: '>',

      threshold: 45,

      actionType: 'alert',

      isActive: true,

      createdAt: DateTime(2026, 9, 10),

    ),

  ];



  Widget buildApp() {

    return ProviderScope(

      overrides: [

        alertProvider.overrideWith((ref) => _TestAlertNotifier(AlertListState(

              activeAlerts: alerts,

              activeCount: 2,

            ))),

        ruleProvider.overrideWith((ref) => _TestRuleNotifier(RuleListState(rules: rules))),

      ],

      child: const MaterialApp(home: Scaffold(body: AlertsScreen())),

    );

  }



  testWidgets('AlertsScreen renders active alerts with severity badges', (tester) async {

    await tester.pumpWidget(buildApp());

    await tester.pumpAndSettle();



    expect(find.text('ALERTS & RULES'), findsOneWidget);

    expect(find.byType(SeverityBadge), findsNWidgets(2));

    expect(find.text('CRITICAL'), findsOneWidget);

    expect(find.text('WARNING'), findsOneWidget);

    expect(find.text('temperature'), findsWidgets);

  });



  testWidgets('AlertsScreen renders configured rules list', (tester) async {

    await tester.pumpWidget(buildApp());

    await tester.pumpAndSettle();



    expect(find.text('Configured Rules'), findsOneWidget);

    expect(find.text('High temperature'), findsOneWidget);

    expect(find.textContaining('temperature > 45.0 · Telegram'), findsOneWidget);

  });



  testWidgets('AlertsScreen shows create rule and telegram test buttons', (tester) async {

    await tester.pumpWidget(buildApp());

    await tester.pumpAndSettle();



    expect(find.text('Create New Rule'), findsOneWidget);

    expect(find.text('Send Test Telegram Alert'), findsOneWidget);

  });

}

