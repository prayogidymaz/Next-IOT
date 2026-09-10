import '../../../core/config/api_config.dart';

enum MapTileMode { online, offline }

class TileUrlResolver {
  TileUrlResolver({
    String? apiBaseUrl,
    String? tileServerBaseUrl,
  })  : apiBaseUrl = apiBaseUrl ?? ApiConfig.baseUrl,
        tileServerBaseUrl = tileServerBaseUrl ?? ApiConfig.tileServerBaseUrl;

  final String apiBaseUrl;
  final String tileServerBaseUrl;

  static const onlineOsmTemplate = 'https://tile.openstreetmap.org/{z}/{x}/{y}.png';
  static const onlineCartoTemplate =
      'https://basemaps.cartocdn.com/dark_all/{z}/{x}/{y}.png';

  String urlTemplate(MapTileMode mode) {
    switch (mode) {
      case MapTileMode.online:
        return onlineCartoTemplate;
      case MapTileMode.offline:
        return offlineTemplate();
    }
  }

  String offlineTemplate() {
    if (tileServerBaseUrl.isNotEmpty) {
      final base = tileServerBaseUrl.endsWith('/')
          ? tileServerBaseUrl.substring(0, tileServerBaseUrl.length - 1)
          : tileServerBaseUrl;
      return '$base/{z}/{x}/{y}.png';
    }
    final api = apiBaseUrl.endsWith('/') ? apiBaseUrl.substring(0, apiBaseUrl.length - 1) : apiBaseUrl;
    return '$api/api/v1/tiles/{z}/{x}/{y}.png';
  }

  /// Prefer offline tiles; fall back to online Carto when offline URL unavailable.
  String resolveWithFallback({
    required MapTileMode mode,
    required bool offlineReachable,
  }) {
    if (mode == MapTileMode.offline && offlineReachable) {
      return offlineTemplate();
    }
    if (mode == MapTileMode.offline && !offlineReachable) {
      return onlineCartoTemplate;
    }
    return urlTemplate(mode);
  }
}
