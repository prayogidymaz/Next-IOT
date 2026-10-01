enum OperationalDomain {
  smartHome,
  smartFarming,
  cyberdeckTactical,
  droneLogistics,
  industrialRobotics,
}

enum EnterpriseSegment {
  b2c,
  b2bEnterprise,
  b2bWhiteLabel,
  apiDeveloper,
}

extension OperationalDomainMeta on OperationalDomain {
  String get emoji => switch (this) {
        OperationalDomain.smartHome => '🏠',
        OperationalDomain.smartFarming => '🚜',
        OperationalDomain.cyberdeckTactical => '📟',
        OperationalDomain.droneLogistics => '🛸',
        OperationalDomain.industrialRobotics => '🤖',
      };

  String get title => switch (this) {
        OperationalDomain.smartHome => 'Smart Home',
        OperationalDomain.smartFarming => 'Smart Farming',
        OperationalDomain.cyberdeckTactical => 'Cyberdeck Tactical',
        OperationalDomain.droneLogistics => 'Drone & Logistics',
        OperationalDomain.industrialRobotics => 'Industrial Robotics',
      };

  String get description => switch (this) {
        OperationalDomain.smartHome =>
          'Rooms, scenes, and consumer device orchestration.',
        OperationalDomain.smartFarming =>
          'Fields, irrigation telemetry, and crop alerts.',
        OperationalDomain.cyberdeckTactical =>
          'Mesh radio, PTT, and field tactical ops.',
        OperationalDomain.droneLogistics =>
          'Fleet airspace, missions, and delivery nodes.',
        OperationalDomain.industrialRobotics =>
          'Factory lines, AMR fleets, and safety interlocks.',
      };

  static OperationalDomain? fromStorage(String? raw) {
    if (raw == null || raw.isEmpty) return null;
    for (final d in OperationalDomain.values) {
      if (d.name == raw) return d;
    }
    return null;
  }
}

extension EnterpriseSegmentMeta on EnterpriseSegment {
  String get title => switch (this) {
        EnterpriseSegment.b2c => 'B2C Consumer',
        EnterpriseSegment.b2bEnterprise => 'B2B Enterprise',
        EnterpriseSegment.b2bWhiteLabel => 'B2B White Label',
        EnterpriseSegment.apiDeveloper => 'API Developer',
      };

  String get subtitle => switch (this) {
        EnterpriseSegment.b2c => 'Single-home / prosumer apps',
        EnterpriseSegment.b2bEnterprise => 'Multi-tenant operator HQ',
        EnterpriseSegment.b2bWhiteLabel => 'Branded tenant experiences',
        EnterpriseSegment.apiDeveloper => 'Keys, webhooks, and SDK-first',
      };

  static EnterpriseSegment? fromStorage(String? raw) {
    if (raw == null || raw.isEmpty) return null;
    for (final s in EnterpriseSegment.values) {
      if (s.name == raw) return s;
    }
    return null;
  }
}
