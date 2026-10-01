import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';

import 'navigation_config.dart';

/// Shared sidebar navigation — keeps Analytics/Settings visible on every shell route.
void navigateShellSection(BuildContext context, String path) {
  context.go(path);
}

String currentShellPath(BuildContext context) {
  return GoRouterState.of(context).uri.path;
}

void openDashboardDevices(BuildContext context) => context.go(AppRoutes.dashboard);

void openDashboardMap(BuildContext context) =>
    context.go('${AppRoutes.dashboard}?tab=map');

void openAlerts(BuildContext context) => context.go(AppRoutes.alerts);

void openAnalytics(BuildContext context) => context.go(AppRoutes.analytics);

void openSettings(BuildContext context) => context.go(AppRoutes.settings);

void openAuditLog(BuildContext context) => context.go(AppRoutes.audit);

void openStudio(BuildContext context) => context.go(AppRoutes.studio);

void openCyberdeck(BuildContext context) => context.go(AppRoutes.cyberdeck);
