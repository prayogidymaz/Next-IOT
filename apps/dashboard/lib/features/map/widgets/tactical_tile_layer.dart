import 'dart:io' show Platform;

import 'package:dio_cache_interceptor/dio_cache_interceptor.dart';
import 'package:dio_cache_interceptor_file_store/dio_cache_interceptor_file_store.dart';
import 'package:flutter/material.dart';
import 'package:flutter_map/flutter_map.dart';
import 'package:flutter_map_cache/flutter_map_cache.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:path_provider/path_provider.dart';

import '../providers/map_tile_provider.dart';

bool get isFlutterTestEnvironment {
  try {
    return Platform.environment.containsKey('FLUTTER_TEST');
  } catch (_) {
    return false;
  }
}

final mapTileCacheStoreProvider = FutureProvider<CacheStore>((ref) async {
  if (isFlutterTestEnvironment) {
    return MemCacheStore(maxSize: 1024 * 1024);
  }
  final dir = await getApplicationDocumentsDirectory();
  return FileCacheStore('${dir.path}/next_iot_map_tiles');
});

/// Tactical basemap with online/offline switch and local tile cache (Cyberdeck).
class TacticalTileLayer extends ConsumerWidget {
  const TacticalTileLayer({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    if (isFlutterTestEnvironment) {
      return const SizedBox.shrink();
    }

    final mode = ref.watch(mapTileModeProvider);
    final resolver = ref.watch(tileUrlResolverProvider);
    final cacheAsync = ref.watch(mapTileCacheStoreProvider);

    final urlTemplate = resolver.resolveWithFallback(
      mode: mode,
      offlineReachable: true,
    );

    return cacheAsync.when(
      data: (store) => TileLayer(
        urlTemplate: urlTemplate,
        userAgentPackageName: 'com.nextiot.dashboard',
        tileProvider: CachedTileProvider(
          store: store,
          maxStale: const Duration(days: 30),
        ),
      ),
      loading: () => TileLayer(
        urlTemplate: urlTemplate,
        userAgentPackageName: 'com.nextiot.dashboard',
      ),
      error: (_, __) => TileLayer(
        urlTemplate: urlTemplate,
        userAgentPackageName: 'com.nextiot.dashboard',
      ),
    );
  }
}
