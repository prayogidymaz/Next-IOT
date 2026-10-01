import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';

import 'package:next_iot_field_app/features/auth/login_screen.dart';

void main() {
  testWidgets('Login screen renders field execution title', (tester) async {
    await tester.pumpWidget(
      const ProviderScope(
        child: MaterialApp(home: LoginScreen()),
      ),
    );
    expect(find.text('Field Execution'), findsOneWidget);
    expect(find.text('Sign in'), findsOneWidget);
  });
}
