/// Central route paths for the Next-IOT dashboard shell vs studio workspace.
abstract final class AppRoutes {
  static const login = '/login';
  static const onboarding = '/onboarding';

  /// Main monitoring shell (TacticalShell + sidebar nav).
  static const dashboard = '/dashboard';

  /// Isolated fullscreen Automation Studio workspace.
  static const studio = '/studio';

  static const devices = '/devices';
  static const devicesOta = '/devices/ota';
  static const mapView = '/map-view';
  static const alerts = '/alerts';
  static const settings = '/settings';
  static const analytics = '/analytics';
  static const audit = '/audit';
  static const cyberdeck = '/cyberdeck';

  /// Legacy aliases kept for bookmarks and deep links.
  static const home = '/home';
  static const automation = '/automation';
}
