import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:go_router/go_router.dart';

import 'package:next_iot_dashboard/features/audit/models/audit_log_models.dart';
import 'package:next_iot_dashboard/features/audit/providers/audit_log_provider.dart';
import 'package:next_iot_dashboard/features/audit/screens/audit_log_screen.dart';
import 'package:next_iot_dashboard/features/auth/models/auth_models.dart';
import 'package:next_iot_dashboard/features/auth/data/auth_repository.dart';
import 'package:next_iot_dashboard/features/auth/providers/auth_provider.dart';
import 'package:next_iot_dashboard/features/auth/providers/permissions_provider.dart';
import 'package:next_iot_dashboard/features/audit/data/audit_repository.dart';

void main() {
  testWidgets('AuditLogScreen shows table for tenant admin', (tester) async {
    await tester.binding.setSurfaceSize(const Size(1440, 900));
    addTearDown(() => tester.binding.setSurfaceSize(null));

    final router = GoRouter(
      routes: [
        GoRoute(path: '/', builder: (_, __) => const AuditLogScreen()),
      ],
    );

    await tester.pumpWidget(
      ProviderScope(
        overrides: [
          authProvider.overrideWith(
            (ref) => _TestAuthNotifier(
              AuthState(
                user: AuthUser(
                  userId: 'u1',
                  email: 'admin@test.com',
                  role: 'tenant_admin',
                  tenantId: 't1',
                ),
              ),
            ),
          ),
          permissionsProvider.overrideWith(
            (ref) => fullAccessPermissionsNotifier(
              ref.watch(permissionsRepositoryProvider),
            ),
          ),
          auditLogProvider.overrideWith((ref) => _SeedAuditNotifier()),
        ],
        child: MaterialApp.router(routerConfig: router),
      ),
    );

    await tester.pumpAndSettle();
    expect(find.text('Audit Log'), findsOneWidget);
    expect(find.text('LOGIN'), findsOneWidget);
    expect(find.text('Export Audit CSV'), findsOneWidget);
  });
}

class _TestAuthNotifier extends AuthNotifier {
  _TestAuthNotifier(AuthState initial) : super(AuthRepository()) {
    state = initial;
  }
}

class _SeedAuditNotifier extends AuditLogNotifier {
  _SeedAuditNotifier() : super(AuditRepository()) {
    state = AuditLogState(
      page: AuditLogPage(
        items: [
          AuditLogEntry(
            id: '1',
            timestamp: DateTime.utc(2026, 1, 1),
            actorEmail: 'admin@test.com',
            action: 'LOGIN',
            resourceTarget: 'auth/login',
            status: 'success',
          ),
        ],
        total: 1,
        page: 1,
        pageSize: 50,
      ),
    );
  }

  @override
  Future<void> load({AuditLogFilter? filter}) async {}
}
