import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:next_iot_dashboard/features/onboarding/data/domain_storage.dart';
import 'package:next_iot_dashboard/features/onboarding/providers/domain_context_provider.dart';
import 'package:next_iot_dashboard/features/onboarding/screens/domain_onboarding_screen.dart';

void main() {
  testWidgets('DomainOnboardingScreen lists all operational domains', (tester) async {
    await tester.pumpWidget(
      ProviderScope(
        overrides: [
          domainContextProvider.overrideWith(
            (ref) => DomainContextNotifier(DomainStorage()),
          ),
        ],
        child: const MaterialApp(home: DomainOnboardingScreen()),
      ),
    );

    expect(find.text('Smart Home'), findsOneWidget);
    expect(find.text('Cyberdeck Tactical'), findsOneWidget);
    expect(find.text('ENTER CONTROL CENTER'), findsOneWidget);
  });
}
