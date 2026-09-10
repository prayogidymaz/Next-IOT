import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import 'core/theme/tactical_theme.dart';
import 'routing/app_router.dart';

class NextIotApp extends ConsumerWidget {
  const NextIotApp({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final router = ref.watch(routerProvider);

    return MaterialApp.router(
      title: 'Next-IOT Dashboard',
      debugShowCheckedModeBanner: false,
      theme: buildTacticalTheme(),
      routerConfig: router,
    );
  }
}
