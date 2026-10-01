import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../../core/theme/tactical_theme.dart';
import '../../../core/widgets/tactical_card.dart';
import '../../../routing/navigation_config.dart';
import '../models/operational_domain.dart';
import '../providers/domain_context_provider.dart';

class DomainOnboardingScreen extends ConsumerStatefulWidget {
  const DomainOnboardingScreen({super.key});

  @override
  ConsumerState<DomainOnboardingScreen> createState() =>
      _DomainOnboardingScreenState();
}

class _DomainOnboardingScreenState extends ConsumerState<DomainOnboardingScreen> {
  OperationalDomain? _domain;
  EnterpriseSegment _segment = EnterpriseSegment.b2bEnterprise;
  bool _saving = false;

  Future<void> _continue() async {
    final domain = _domain;
    if (domain == null) return;
    setState(() => _saving = true);
    await ref.read(domainContextProvider.notifier).select(
          domain: domain,
          segment: _segment,
        );
    if (!mounted) return;
    context.go(AppRoutes.dashboard);
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);

    return Scaffold(
      backgroundColor: TacticalColors.background,
      body: SafeArea(
        child: Center(
          child: SingleChildScrollView(
            padding: const EdgeInsets.all(24),
            child: ConstrainedBox(
              constraints: const BoxConstraints(maxWidth: 720),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.stretch,
                children: [
                  Text(
                    'Choose your operational domain',
                    style: theme.textTheme.headlineSmall,
                    textAlign: TextAlign.center,
                  ),
                  const SizedBox(height: 8),
                  Text(
                    'Navigation, labels, and dashboard context adapt to your selection.',
                    style: theme.textTheme.bodyMedium,
                    textAlign: TextAlign.center,
                  ),
                  const SizedBox(height: 24),
                  ...OperationalDomain.values.map((d) {
                    final selected = _domain == d;
                    return Padding(
                      padding: const EdgeInsets.only(bottom: 10),
                      child: Material(
                        color: Colors.transparent,
                        child: InkWell(
                          onTap: () => setState(() => _domain = d),
                          borderRadius: BorderRadius.circular(16),
                          child: TacticalCard(
                            padding: const EdgeInsets.all(16),
                            child: Row(
                              children: [
                                Text(d.emoji, style: const TextStyle(fontSize: 28)),
                                const SizedBox(width: 16),
                                Expanded(
                                  child: Column(
                                    crossAxisAlignment: CrossAxisAlignment.start,
                                    children: [
                                      Text(
                                        d.title,
                                        style: theme.textTheme.titleMedium,
                                      ),
                                      const SizedBox(height: 4),
                                      Text(
                                        d.description,
                                        style: theme.textTheme.bodySmall,
                                      ),
                                    ],
                                  ),
                                ),
                                if (selected)
                                  Icon(Icons.check_circle,
                                      color: TacticalColors.borderNeon),
                              ],
                            ),
                          ),
                        ),
                      ),
                    );
                  }),
                  const SizedBox(height: 16),
                  Text(
                    'Enterprise preset',
                    style: theme.textTheme.titleSmall,
                  ),
                  const SizedBox(height: 8),
                  Wrap(
                    spacing: 8,
                    runSpacing: 8,
                    children: EnterpriseSegment.values.map((s) {
                      final selected = _segment == s;
                      return ChoiceChip(
                        label: Text(s.title),
                        selected: selected,
                        onSelected: (_) => setState(() => _segment = s),
                      );
                    }).toList(),
                  ),
                  if (_segment != EnterpriseSegment.b2c)
                    Padding(
                      padding: const EdgeInsets.only(top: 8),
                      child: Text(
                        _segment.subtitle,
                        style: theme.textTheme.bodySmall,
                      ),
                    ),
                  const SizedBox(height: 28),
                  FilledButton(
                    onPressed: _domain == null || _saving ? null : _continue,
                    child: _saving
                        ? const SizedBox(
                            height: 22,
                            width: 22,
                            child: CircularProgressIndicator(strokeWidth: 2),
                          )
                        : const Text('ENTER CONTROL CENTER'),
                  ),
                ],
              ),
            ),
          ),
        ),
      ),
    );
  }
}
