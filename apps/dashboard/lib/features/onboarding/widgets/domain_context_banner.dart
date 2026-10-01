import 'package:flutter/material.dart';

import '../../../core/theme/tactical_theme.dart';
import '../models/domain_navigation_profile.dart';

class DomainContextBanner extends StatelessWidget {
  const DomainContextBanner({super.key, required this.profile});

  final DomainNavigationProfile profile;

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.fromLTRB(24, 12, 24, 0),
      child: Container(
        padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 10),
        decoration: BoxDecoration(
          borderRadius: BorderRadius.circular(12),
          border: Border.all(color: TacticalColors.borderNeon.withOpacity(0.35)),
          color: TacticalColors.surface.withOpacity(0.6),
        ),
        child: Row(
          children: [
            Text(profile.domain.emoji, style: const TextStyle(fontSize: 20)),
            const SizedBox(width: 10),
            Expanded(
              child: Text(
                '${profile.domain.title} mode — contextual navigation active',
                style: Theme.of(context).textTheme.bodySmall,
              ),
            ),
          ],
        ),
      ),
    );
  }
}
