import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../../core/rbac/app_permissions.dart';
import '../../../core/theme/tactical_theme.dart';
import '../../../core/widgets/permission_guard.dart';
import '../../../core/widgets/tactical_card.dart';
import '../../../core/widgets/tactical_shell.dart';
import '../../../routing/navigation_config.dart';
import '../models/audit_log_models.dart';
import '../providers/audit_log_provider.dart';

const _actionFilters = [
  '',
  'LOGIN',
  'DEVICE_REGISTER',
  'DEVICE_COMMAND',
  'OTA_UPLOAD',
  'RULE_MUTATION',
  'TENANT_UPDATE',
];

class AuditLogScreen extends ConsumerStatefulWidget {
  const AuditLogScreen({super.key});

  @override
  ConsumerState<AuditLogScreen> createState() => _AuditLogScreenState();
}

class _AuditLogScreenState extends ConsumerState<AuditLogScreen> {
  final _actorController = TextEditingController();
  String _action = '';

  @override
  void initState() {
    super.initState();
    Future.microtask(() => ref.read(auditLogProvider.notifier).load());
  }

  @override
  void dispose() {
    _actorController.dispose();
    super.dispose();
  }

  void _applyFilters() {
    ref.read(auditLogProvider.notifier).load(
          filter: AuditLogFilter(
            action: _action.isEmpty ? null : _action,
            actor: _actorController.text.trim().isEmpty
                ? null
                : _actorController.text.trim(),
          ),
        );
  }

  @override
  Widget build(BuildContext context) {
    final state = ref.watch(auditLogProvider);

    return PermissionGuard(
      permission: AppPermissions.auditRead,
      fallback: Center(
        child: Text(
          'Audit logs require Tenant Admin or Super Admin role.',
          style: Theme.of(context).textTheme.bodyLarge,
        ),
      ),
      child: TacticalShell(
        section: TacticalNavSection.devices,
        subtitle: 'Enterprise audit trail',
        onSectionChanged: (s) {
          switch (s) {
            case TacticalNavSection.devices:
              context.go(AppRoutes.dashboard);
            case TacticalNavSection.mapView:
              context.go('${AppRoutes.dashboard}?tab=map');
            case TacticalNavSection.alerts:
              context.go(AppRoutes.alerts);
          }
        },
        onOpenStudio: () => context.go(AppRoutes.studio),
        body: Padding(
          padding: const EdgeInsets.all(24),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              Text(
                'Audit Log',
                style: Theme.of(context).textTheme.headlineSmall?.copyWith(
                      color: TacticalColors.borderNeon,
                    ),
              ),
              const SizedBox(height: 16),
              Wrap(
                spacing: 12,
                runSpacing: 12,
                crossAxisAlignment: WrapCrossAlignment.center,
                children: [
                  SizedBox(
                    width: 240,
                    child: DropdownButtonFormField<String>(
                      isExpanded: true,
                      value: _action,
                      decoration: const InputDecoration(labelText: 'Action'),
                      items: _actionFilters
                          .map(
                            (a) => DropdownMenuItem(
                              value: a,
                              child: Text(a.isEmpty ? 'All actions' : a),
                            ),
                          )
                          .toList(),
                      onChanged: (v) => setState(() => _action = v ?? ''),
                    ),
                  ),
                  SizedBox(
                    width: 260,
                    child: TextField(
                      controller: _actorController,
                      decoration: const InputDecoration(
                        labelText: 'Search actor / resource',
                      ),
                      onSubmitted: (_) => _applyFilters(),
                    ),
                  ),
                  FilledButton(
                    onPressed: _applyFilters,
                    child: const Text('Apply filters'),
                  ),
                  OutlinedButton.icon(
                    onPressed: state.exporting
                        ? null
                        : () => ref.read(auditLogProvider.notifier).exportCsv(),
                    icon: state.exporting
                        ? const SizedBox(
                            width: 16,
                            height: 16,
                            child: CircularProgressIndicator(strokeWidth: 2),
                          )
                        : const Icon(Icons.download_outlined, size: 18),
                    label: const Text('Export Audit CSV'),
                  ),
                ],
              ),
              if (state.error != null) ...[
                const SizedBox(height: 12),
                Text(state.error!, style: const TextStyle(color: TacticalColors.critical)),
              ],
              const SizedBox(height: 16),
              Expanded(
                child: TacticalCard(
                  child: state.isLoading && state.page == null
                      ? const Center(child: CircularProgressIndicator())
                      : _AuditTable(page: state.page),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}

class _AuditTable extends StatelessWidget {
  const _AuditTable({required this.page});

  final AuditLogPage? page;

  @override
  Widget build(BuildContext context) {
    final data = page;
    if (data == null || data.items.isEmpty) {
      return const Center(child: Text('No audit events yet.'));
    }

    return SingleChildScrollView(
      scrollDirection: Axis.horizontal,
      child: DataTable(
        columns: const [
          DataColumn(label: Text('Time (UTC)')),
          DataColumn(label: Text('Action')),
          DataColumn(label: Text('Actor')),
          DataColumn(label: Text('Resource')),
          DataColumn(label: Text('IP')),
          DataColumn(label: Text('Status')),
        ],
        rows: [
          for (final row in data.items)
            DataRow(
              cells: [
                DataCell(Text(row.timestamp.toUtc().toIso8601String())),
                DataCell(Text(row.action)),
                DataCell(Text(row.actorEmail)),
                DataCell(Text(row.resourceTarget)),
                DataCell(Text(row.ipAddress ?? '—')),
                DataCell(Text(row.status)),
              ],
            ),
        ],
      ),
    );
  }
}
