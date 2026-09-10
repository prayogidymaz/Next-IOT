import 'dart:io' show Platform;

import 'package:flutter/material.dart';
import 'package:flutter_map/flutter_map.dart';

bool get isFlutterTestEnvironment {
  try {
    return Platform.environment.containsKey('FLUTTER_TEST');
  } catch (_) {
    return false;
  }
}

/// OpenStreetMap tiles for production. Omitted during widget tests (no network).
class TacticalTileLayer extends StatelessWidget {
  const TacticalTileLayer({super.key});

  @override
  Widget build(BuildContext context) {
    if (isFlutterTestEnvironment) {
      return const SizedBox.shrink();
    }

    return TileLayer(
      urlTemplate: 'https://tile.openstreetmap.org/{z}/{x}/{y}.png',
      userAgentPackageName: 'com.nextiot.dashboard',
    );
  }
}
