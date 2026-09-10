import 'package:flutter_test/flutter_test.dart';
import 'package:next_iot_dashboard/features/map/config/tile_url_resolver.dart';

void main() {
  final resolver = TileUrlResolver(
    apiBaseUrl: 'http://localhost:8000',
    tileServerBaseUrl: '',
  );

  test('online mode uses Carto dark basemap', () {
    expect(
      resolver.urlTemplate(MapTileMode.online),
      TileUrlResolver.onlineCartoTemplate,
    );
  });

  test('offline mode uses API tile proxy path', () {
    expect(
      resolver.offlineTemplate(),
      'http://localhost:8000/api/v1/tiles/{z}/{x}/{y}.png',
    );
  });

  test('offline mode uses direct tile server when configured', () {
    final direct = TileUrlResolver(
      apiBaseUrl: 'http://localhost:8000',
      tileServerBaseUrl: 'http://localhost:8080/services/offline-map/tiles',
    );
    expect(
      direct.offlineTemplate(),
      'http://localhost:8080/services/offline-map/tiles/{z}/{x}/{y}.png',
    );
  });

  test('resolveWithFallback uses online when offline unreachable', () {
    expect(
      resolver.resolveWithFallback(mode: MapTileMode.offline, offlineReachable: false),
      TileUrlResolver.onlineCartoTemplate,
    );
  });

  test('resolveWithFallback uses offline template when reachable', () {
    expect(
      resolver.resolveWithFallback(mode: MapTileMode.offline, offlineReachable: true),
      'http://localhost:8000/api/v1/tiles/{z}/{x}/{y}.png',
    );
  });
}
