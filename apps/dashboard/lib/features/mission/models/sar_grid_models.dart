class SarGridPoint {
  const SarGridPoint({required this.lat, required this.lon});

  final double lat;
  final double lon;

  factory SarGridPoint.fromJson(Map<String, dynamic> json) => SarGridPoint(
        lat: (json['lat'] as num).toDouble(),
        lon: (json['lon'] as num).toDouble(),
      );
}

class SarGridWaypoint {
  const SarGridWaypoint({
    required this.sequence,
    required this.lat,
    required this.lon,
    this.label,
  });

  final int sequence;
  final double lat;
  final double lon;
  final String? label;

  factory SarGridWaypoint.fromJson(Map<String, dynamic> json) => SarGridWaypoint(
        sequence: json['sequence'] as int,
        lat: (json['lat'] as num).toDouble(),
        lon: (json['lon'] as num).toDouble(),
        label: json['label'] as String?,
      );
}

class SarGridTrack {
  const SarGridTrack({required this.trackIndex, required this.points});

  final int trackIndex;
  final List<SarGridPoint> points;

  factory SarGridTrack.fromJson(Map<String, dynamic> json) => SarGridTrack(
        trackIndex: json['track_index'] as int,
        points: (json['points'] as List<dynamic>)
            .map((e) => SarGridPoint.fromJson(e as Map<String, dynamic>))
            .toList(),
      );
}

class SarGridSearchArea {
  const SarGridSearchArea({required this.label, required this.points});

  final String label;
  final List<SarGridPoint> points;

  factory SarGridSearchArea.fromJson(Map<String, dynamic> json) => SarGridSearchArea(
        label: json['label'] as String,
        points: (json['points'] as List<dynamic>)
            .map((e) => SarGridPoint.fromJson(e as Map<String, dynamic>))
            .toList(),
      );
}

enum SarGridPattern {
  expandingSquare('expanding_square'),
  parallelTrack('parallel_track');

  const SarGridPattern(this.apiValue);
  final String apiValue;
}

class SarGridResult {
  const SarGridResult({
    required this.pattern,
    required this.lkp,
    required this.radiusM,
    required this.waypoints,
    required this.tracks,
    required this.searchAreas,
  });

  final String pattern;
  final SarGridPoint lkp;
  final double radiusM;
  final List<SarGridWaypoint> waypoints;
  final List<SarGridTrack> tracks;
  final List<SarGridSearchArea> searchAreas;

  factory SarGridResult.fromJson(Map<String, dynamic> json) => SarGridResult(
        pattern: json['pattern'] as String,
        lkp: SarGridPoint.fromJson(json['lkp'] as Map<String, dynamic>),
        radiusM: (json['radius_m'] as num).toDouble(),
        waypoints: (json['waypoints'] as List<dynamic>)
            .map((e) => SarGridWaypoint.fromJson(e as Map<String, dynamic>))
            .toList(),
        tracks: (json['tracks'] as List<dynamic>)
            .map((e) => SarGridTrack.fromJson(e as Map<String, dynamic>))
            .toList(),
        searchAreas: (json['search_areas'] as List<dynamic>)
            .map((e) => SarGridSearchArea.fromJson(e as Map<String, dynamic>))
            .toList(),
      );
}
