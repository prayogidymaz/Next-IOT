import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:shared_preferences/shared_preferences.dart';

import '../config/tile_url_resolver.dart';

const _offlineModeKey = 'tactical_map_offline_mode';

class MapTileModeNotifier extends StateNotifier<MapTileMode> {
  MapTileModeNotifier() : super(MapTileMode.online) {
    _load();
  }

  Future<void> _load() async {
    final prefs = await SharedPreferences.getInstance();
    final offline = prefs.getBool(_offlineModeKey) ?? false;
    state = offline ? MapTileMode.offline : MapTileMode.online;
  }

  Future<void> toggle() async {
    final next = state == MapTileMode.online ? MapTileMode.offline : MapTileMode.online;
    state = next;
    final prefs = await SharedPreferences.getInstance();
    await prefs.setBool(_offlineModeKey, next == MapTileMode.offline);
  }

  Future<void> setMode(MapTileMode mode) async {
    state = mode;
    final prefs = await SharedPreferences.getInstance();
    await prefs.setBool(_offlineModeKey, mode == MapTileMode.offline);
  }
}

final mapTileModeProvider = StateNotifierProvider<MapTileModeNotifier, MapTileMode>((ref) {
  return MapTileModeNotifier();
});

final tileUrlResolverProvider = Provider<TileUrlResolver>((ref) => TileUrlResolver());
