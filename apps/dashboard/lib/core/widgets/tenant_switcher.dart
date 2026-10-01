import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../features/auth/providers/auth_provider.dart';
import '../../features/tenants/models/tenant_models.dart';
import '../../features/tenants/providers/tenant_provider.dart';
import '../theme/tactical_theme.dart';

class TenantSwitcher extends ConsumerWidget {
  const TenantSwitcher({super.key, this.compact = false});

  final bool compact;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final auth = ref.watch(authProvider);
    final tenantState = ref.watch(tenantProvider);
    final activeId = auth.user?.tenantId;
    final tenants = tenantState.tenants;
    if (activeId == null || tenants.isEmpty) {
      return const SizedBox.shrink();
    }

    TenantSummary? selected;
    for (final t in tenants) {
      if (t.id == activeId) {
        selected = t;
        break;
      }
    }
    selected ??= tenants.first;

    final label = compact ? selected.slug : selected.name;

    return PopupMenuButton<String>(
      tooltip: 'Active organization',
      enabled: !tenantState.isSwitching && tenants.length > 1,
      onSelected: (id) async {
        if (id == activeId) return;
        await ref.read(tenantProvider.notifier).switchTo(id);
      },
      itemBuilder: (context) {
        return tenants
            .map(
              (t) => PopupMenuItem<String>(
                value: t.id,
                child: Row(
                  children: [
                    if (t.id == activeId)
                      const Icon(Icons.check, size: 16, color: TacticalColors.success)
                    else
                      const SizedBox(width: 16),
                    const SizedBox(width: 8),
                    Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(t.name, style: Theme.of(context).textTheme.bodyMedium),
                          Text(
                            t.slug,
                            style: Theme.of(context).textTheme.bodySmall?.copyWith(
                                  color: TacticalColors.textSecondary,
                                ),
                          ),
                        ],
                      ),
                    ),
                  ],
                ),
              ),
            )
            .toList();
      },
      child: Container(
        padding: EdgeInsets.symmetric(horizontal: compact ? 8 : 12, vertical: 6),
        decoration: BoxDecoration(
          color: TacticalColors.background,
          borderRadius: BorderRadius.circular(20),
          border: Border.all(color: TacticalColors.border),
        ),
        child: Row(
          mainAxisSize: MainAxisSize.min,
          children: [
            Icon(Icons.apartment_outlined,
                size: 14, color: TacticalColors.borderNeon.withOpacity(0.9)),
            const SizedBox(width: 6),
            ConstrainedBox(
              constraints: BoxConstraints(maxWidth: compact ? 100 : 180),
              child: Text(
                label,
                overflow: TextOverflow.ellipsis,
                style: Theme.of(context).textTheme.labelMedium?.copyWith(
                      color: TacticalColors.textPrimary,
                      fontSize: compact ? 11 : 12,
                    ),
              ),
            ),
            if (tenantState.isSwitching) ...[
              const SizedBox(width: 6),
              const SizedBox(
                width: 12,
                height: 12,
                child: CircularProgressIndicator(strokeWidth: 2),
              ),
            ] else if (tenants.length > 1) ...[
              const SizedBox(width: 4),
              const Icon(Icons.expand_more, size: 16, color: TacticalColors.textSecondary),
            ],
          ],
        ),
      ),
    );
  }
}
