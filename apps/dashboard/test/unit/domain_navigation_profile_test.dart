import 'package:flutter_test/flutter_test.dart';
import 'package:next_iot_dashboard/core/widgets/tactical_shell.dart';
import 'package:next_iot_dashboard/features/onboarding/models/domain_navigation_profile.dart';
import 'package:next_iot_dashboard/features/onboarding/models/operational_domain.dart';

void main() {
  test('smart home domain uses consumer nav labels', () {
    final profile = navigationProfileFor(
      domain: OperationalDomain.smartHome,
      segment: EnterpriseSegment.b2c,
    );
    expect(profile.tabs.first.label, 'Rooms');
    expect(profile.showCyberdeckShortcut, isFalse);
  });

  test('cyberdeck domain enables cyberdeck shortcut', () {
    final profile = navigationProfileFor(
      domain: OperationalDomain.cyberdeckTactical,
      segment: EnterpriseSegment.b2bEnterprise,
    );
    expect(profile.showCyberdeckShortcut, isTrue);
    expect(profile.primarySection, TacticalNavSection.mapView);
  });
}
