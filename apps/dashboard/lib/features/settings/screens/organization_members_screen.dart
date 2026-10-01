import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../../core/rbac/app_permissions.dart';
import '../../../core/theme/tactical_theme.dart';
import '../../../core/widgets/permission_guard.dart';
import '../../../core/widgets/tactical_card.dart';
import '../../../core/widgets/tactical_shell.dart';
import '../../../routing/navigation_config.dart';
import '../../auth/providers/auth_provider.dart';
import '../../auth/providers/permissions_provider.dart';
import '../../tenants/providers/tenant_provider.dart';

class OrganizationMembersScreen extends ConsumerStatefulWidget {
  const OrganizationMembersScreen({super.key});

  @override
  ConsumerState<OrganizationMembersScreen> createState() =>
      _OrganizationMembersScreenState();
}

class _OrganizationMembersScreenState
    extends ConsumerState<OrganizationMembersScreen> {
  final _orgName = TextEditingController();
  final _orgSlug = TextEditingController();
  final _inviteEmail = TextEditingController();
  final _invitePassword = TextEditingController();
  String _inviteRole = 'operator';
  List<_MemberRow> _members = [];
  bool _loadingMembers = false;
  String? _membersError;

  @override
  void initState() {
    super.initState();
    Future.microtask(_loadMembers);
  }

  @override
  void dispose() {
    _orgName.dispose();
    _orgSlug.dispose();
    _inviteEmail.dispose();
    _invitePassword.dispose();
    super.dispose();
  }

  Future<void> _loadMembers() async {
    final tenantId = ref.read(authProvider).user?.tenantId;
    if (tenantId == null) return;
    setState(() {
      _loadingMembers = true;
      _membersError = null;
    });
    try {
      final repo = ref.read(tenantRepositoryProvider);
      final list = await repo.listMembers(tenantId);
      setState(() {
        _members = list
            .map((m) => _MemberRow(
                  email: m.email,
                  role: m.role,
                  isActive: m.isActive,
                ))
            .toList();
      });
    } catch (e) {
      setState(() => _membersError = e.toString());
    } finally {
      setState(() => _loadingMembers = false);
    }
  }

  Future<void> _createOrg() async {
    final name = _orgName.text.trim();
    final slug = _orgSlug.text.trim().toLowerCase();
    if (name.isEmpty || slug.isEmpty) return;
    final repo = ref.read(tenantRepositoryProvider);
    await repo.createTenant(name: name, slug: slug);
    await ref.read(tenantProvider.notifier).loadTenants();
    if (mounted) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Organization created')),
      );
      _orgName.clear();
      _orgSlug.clear();
    }
  }

  Future<void> _invite() async {
    final tenantId = ref.read(authProvider).user?.tenantId;
    if (tenantId == null) return;
    final email = _inviteEmail.text.trim();
    final password = _invitePassword.text;
    if (email.isEmpty || password.length < 8) return;
    final repo = ref.read(tenantRepositoryProvider);
    await repo.inviteMember(
      tenantId: tenantId,
      email: email,
      password: password,
      role: _inviteRole,
    );
    _inviteEmail.clear();
    _invitePassword.clear();
    await _loadMembers();
    if (mounted) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Invited $email as $_inviteRole')),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    final auth = ref.watch(authProvider);
    final user = auth.user!;
    final canManageMembers =
        ref.watch(permissionsProvider.select((s) => s.can(AppPermissions.membersManage)));

    return TacticalShell(
      section: TacticalNavSection.devices,
      showContentHeader: true,
      subtitle: 'Organization & Members',
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
      actions: [
        IconButton(
          tooltip: 'Back to dashboard',
          icon: const Icon(Icons.arrow_back, color: TacticalColors.textSecondary),
          onPressed: () => context.go(AppRoutes.dashboard),
        ),
      ],
      body: ListView(
        padding: const EdgeInsets.all(24),
        children: [
          Text(
            'Organization & Members',
            style: Theme.of(context).textTheme.headlineSmall,
          ),
          const SizedBox(height: 8),
          Text(
            'Tenant ${user.tenantId.substring(0, 8)}… · role ${user.role}',
            style: Theme.of(context).textTheme.bodySmall?.copyWith(
                  color: TacticalColors.textSecondary,
                ),
          ),
          const SizedBox(height: 24),
          PermissionGuard(
            permission: AppPermissions.tenantManage,
            child: TacticalCard(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.stretch,
                children: [
                  Text('Create organization',
                      style: Theme.of(context).textTheme.titleMedium),
                  const SizedBox(height: 12),
                  TextField(
                    controller: _orgName,
                    decoration: const InputDecoration(labelText: 'Display name'),
                  ),
                  const SizedBox(height: 8),
                  TextField(
                    controller: _orgSlug,
                    decoration: const InputDecoration(
                      labelText: 'Slug (lowercase, hyphens)',
                    ),
                  ),
                  const SizedBox(height: 12),
                  FilledButton(
                    onPressed: _createOrg,
                    child: const Text('Create tenant'),
                  ),
                ],
              ),
            ),
          ),
          const SizedBox(height: 16),
          TacticalCard(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                Text('Team members',
                    style: Theme.of(context).textTheme.titleMedium),
                const SizedBox(height: 12),
                if (_loadingMembers)
                  const Center(child: CircularProgressIndicator())
                else if (_membersError != null)
                  Text(_membersError!, style: const TextStyle(color: TacticalColors.critical))
                else if (_members.isEmpty)
                  const Text('No members loaded.')
                else
                  ..._members.map(
                    (m) => ListTile(
                      dense: true,
                      title: Text(m.email),
                      subtitle: Text(m.role),
                      trailing: m.isActive
                          ? const Icon(Icons.check_circle_outline,
                              color: TacticalColors.success, size: 18)
                          : const Icon(Icons.block, size: 18),
                    ),
                  ),
                if (canManageMembers) ...[
                  const Divider(height: 24),
                  Text('Invite member',
                      style: Theme.of(context).textTheme.titleSmall),
                  const SizedBox(height: 8),
                  TextField(
                    controller: _inviteEmail,
                    decoration: const InputDecoration(labelText: 'Email'),
                  ),
                  const SizedBox(height: 8),
                  TextField(
                    controller: _invitePassword,
                    obscureText: true,
                    decoration: const InputDecoration(
                      labelText: 'Temporary password (min 8 chars)',
                    ),
                  ),
                  const SizedBox(height: 8),
                  DropdownButtonFormField<String>(
                    value: _inviteRole,
                    decoration: const InputDecoration(labelText: 'Role'),
                    items: const [
                      DropdownMenuItem(value: 'tenant_admin', child: Text('Admin')),
                      DropdownMenuItem(value: 'operator', child: Text('Operator')),
                      DropdownMenuItem(value: 'viewer', child: Text('Viewer')),
                    ],
                    onChanged: (v) {
                      if (v != null) setState(() => _inviteRole = v);
                    },
                  ),
                  const SizedBox(height: 12),
                  FilledButton(
                    onPressed: _invite,
                    child: const Text('Send invite'),
                  ),
                ],
              ],
            ),
          ),
        ],
      ),
    );
  }
}

class _MemberRow {
  _MemberRow({
    required this.email,
    required this.role,
    required this.isActive,
  });

  final String email;
  final String role;
  final bool isActive;
}
