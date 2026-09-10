import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:next_iot_dashboard/features/auth/data/auth_repository.dart';
import 'package:next_iot_dashboard/features/auth/providers/auth_provider.dart';
import 'package:next_iot_dashboard/features/auth/screens/login_screen.dart';

class _TestAuthNotifier extends AuthNotifier {
  _TestAuthNotifier(AuthRepository repo, AuthState initial) : super(repo) {
    state = initial;
  }

  @override
  Future<bool> login(String email, String password) async => false;
}

void main() {
  testWidgets('LoginScreen renders email and password fields', (tester) async {
    await tester.pumpWidget(
      const ProviderScope(
        child: MaterialApp(home: LoginScreen()),
      ),
    );

    expect(find.text('NEXT-IOT'), findsOneWidget);
    expect(find.byType(TextFormField), findsNWidgets(2));
    expect(find.widgetWithText(FilledButton, 'AUTHENTICATE'), findsOneWidget);
  });

  testWidgets('LoginScreen shows validation errors on empty submit', (tester) async {
    await tester.pumpWidget(
      const ProviderScope(
        child: MaterialApp(home: LoginScreen()),
      ),
    );

    await tester.tap(find.widgetWithText(FilledButton, 'AUTHENTICATE'));
    await tester.pumpAndSettle();

    expect(find.text('Email required'), findsOneWidget);
    expect(find.text('Password required'), findsOneWidget);
  });

  testWidgets('LoginScreen shows loading indicator when auth is loading', (tester) async {
    await tester.pumpWidget(
      ProviderScope(
        overrides: [
          authProvider.overrideWith(
            (ref) => _TestAuthNotifier(
              AuthRepository(),
              const AuthState(isLoading: true),
            ),
          ),
        ],
        child: const MaterialApp(home: LoginScreen()),
      ),
    );

    expect(find.byType(CircularProgressIndicator), findsOneWidget);
  });

  testWidgets('LoginScreen displays auth error message', (tester) async {
    await tester.pumpWidget(
      ProviderScope(
        overrides: [
          authProvider.overrideWith(
            (ref) => _TestAuthNotifier(
              AuthRepository(),
              const AuthState(error: 'Invalid email or password'),
            ),
          ),
        ],
        child: const MaterialApp(home: LoginScreen()),
      ),
    );

    expect(find.text('Invalid email or password'), findsOneWidget);
  });
}
