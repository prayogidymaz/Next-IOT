class MissionWaypoint {
  const MissionWaypoint({
    required this.id,
    required this.sequence,
    required this.latitude,
    required this.longitude,
  });

  final String id;
  final int sequence;
  final double latitude;
  final double longitude;

  String get label => 'P$sequence';

  Map<String, dynamic> toCommandJson() => {
        'sequence': sequence,
        'lat': latitude,
        'lon': longitude,
      };

  MissionWaypoint copyWith({int? sequence}) => MissionWaypoint(
        id: id,
        sequence: sequence ?? this.sequence,
        latitude: latitude,
        longitude: longitude,
      );
}

enum DeviceCommandType {
  goToWaypoint('GO_TO_WAYPOINT'),
  goToMission('GO_TO_MISSION'),
  rtl('RTL'),
  takeoff('TAKEOFF'),
  land('LAND');

  const DeviceCommandType(this.apiValue);
  final String apiValue;
}

class DeviceCommandResult {
  const DeviceCommandResult({
    required this.id,
    required this.commandType,
    required this.status,
  });

  final String id;
  final String commandType;
  final String status;

  factory DeviceCommandResult.fromJson(Map<String, dynamic> json) => DeviceCommandResult(
        id: json['id'] as String,
        commandType: json['command_type'] as String,
        status: json['status'] as String,
      );
}
