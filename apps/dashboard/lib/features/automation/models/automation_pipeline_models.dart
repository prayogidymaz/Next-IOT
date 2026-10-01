import 'dart:ui' show Offset;

enum PipelineNodeType { trigger, condition, action }

/// n8n-style multi-directional connection port.
enum PipelinePortSide {
  left,
  top,
  bottom,
  right;

  /// Legacy helpers — all four sides are omni-directional for canvas wiring.
  bool get isInput => true;
  bool get isOutput => true;

  static const allPorts = [
    PipelinePortSide.left,
    PipelinePortSide.top,
    PipelinePortSide.bottom,
    PipelinePortSide.right,
  ];

  static const inputPorts = allPorts;

  String get apiValue => name.toUpperCase();

  static PipelinePortSide fromApiValue(String? raw,
      {PipelinePortSide fallback = PipelinePortSide.left}) {
    return switch (raw?.toUpperCase()) {
      'TOP' => PipelinePortSide.top,
      'BOTTOM' => PipelinePortSide.bottom,
      'RIGHT' => PipelinePortSide.right,
      'LEFT' => PipelinePortSide.left,
      _ => fallback,
    };
  }
}

enum TriggerSubtype {
  aiDetection('AI_DETECTION', 'AI Detection'),
  telemetryAnomaly('TELEMETRY_ANOMALY', 'Telemetry Anomaly'),
  telemetryThreshold('TELEMETRY_THRESHOLD', 'Telemetry Threshold'),
  geofenceBreach('GEOFENCE_BREACH', 'Geofence Breach'),
  weatherHazard('WEATHER_HAZARD', 'Weather Hazard');

  const TriggerSubtype(this.apiValue, this.label);
  final String apiValue;
  final String label;
}

enum ConditionSubtype {
  windSpeedLessThan('WIND_SPEED_LESS_THAN', 'Wind Speed <'),
  batteryAbove('BATTERY_ABOVE', 'Battery Above'),
  timeWindow('TIME_WINDOW', 'Time Window'),
  logicAnd('LOGIC_AND', 'Multi-sensor AND'),
  logicOr('LOGIC_OR', 'Multi-sensor OR');

  const ConditionSubtype(this.apiValue, this.label);
  final String apiValue;
  final String label;
}

enum ActionSubtype {
  mavlinkArm('MAVLINK_ARM', 'MAVLink ARM'),
  mavlinkRtl('MAVLINK_RTL', 'MAVLink RTL'),
  mavlinkLand('MAVLINK_LAND', 'MAVLink LAND'),
  dispatchSarGrid('DISPATCH_SAR_GRID', 'Dispatch SAR Grid'),
  triggerAlarm('TRIGGER_ALARM', 'Trigger Alarm'),
  triggerAlert('TRIGGER_ALERT', 'Trigger Alert'),
  deviceCommand('DEVICE_COMMAND', 'Device Command'),
  sendWebhook('SEND_WEBHOOK', 'Send Webhook'),
  websocketAlert('WEBSOCKET_ALERT', 'WebSocket Alert');

  const ActionSubtype(this.apiValue, this.label);
  final String apiValue;
  final String label;
}

class PipelineNodeModel {
  const PipelineNodeModel({
    required this.id,
    required this.type,
    required this.subtype,
    this.config = const {},
    this.position = Offset.zero,
  });

  final String id;
  final PipelineNodeType type;
  final String subtype;
  final Map<String, dynamic> config;
  final Offset position;

  String get label {
    for (final t in TriggerSubtype.values) {
      if (t.apiValue == subtype) return t.label;
    }
    for (final c in ConditionSubtype.values) {
      if (c.apiValue == subtype) return c.label;
    }
    for (final a in ActionSubtype.values) {
      if (a.apiValue == subtype) return a.label;
    }
    return subtype;
  }

  PipelineNodeModel copyWith({
    String? id,
    PipelineNodeType? type,
    String? subtype,
    Map<String, dynamic>? config,
    Offset? position,
  }) {
    return PipelineNodeModel(
      id: id ?? this.id,
      type: type ?? this.type,
      subtype: subtype ?? this.subtype,
      config: config ?? this.config,
      position: position ?? this.position,
    );
  }

  Map<String, dynamic> toJson() => toApiJson();

  /// Backend-facing node payload with normalized condition config keys.
  Map<String, dynamic> toApiJson() {
    final apiConfig = Map<String, dynamic>.from(config);
    apiConfig['canvas_x'] = position.dx;
    apiConfig['canvas_y'] = position.dy;

    if (subtype == 'WIND_SPEED_LESS_THAN' &&
        apiConfig.containsKey('max_wind_mps') &&
        !apiConfig.containsKey('threshold')) {
      apiConfig['threshold'] = apiConfig['max_wind_mps'];
    }
    if (subtype == 'BATTERY_ABOVE' &&
        apiConfig.containsKey('min_percent') &&
        !apiConfig.containsKey('threshold')) {
      apiConfig['threshold'] = 11.0;
    }

    return {
      'id': id,
      'type': type.name.toUpperCase(),
      'subtype': subtype,
      'config': apiConfig,
    };
  }

  factory PipelineNodeModel.fromJson(Map<String, dynamic> json) {
    final config = Map<String, dynamic>.from(json['config'] as Map? ?? {});
    final x = (config.remove('canvas_x') as num?)?.toDouble() ?? 0;
    final y = (config.remove('canvas_y') as num?)?.toDouble() ?? 0;
    final typeRaw = (json['type'] as String? ?? 'TRIGGER').toUpperCase();
    return PipelineNodeModel(
      id: json['id'] as String,
      type: switch (typeRaw) {
        'CONDITION' => PipelineNodeType.condition,
        'ACTION' => PipelineNodeType.action,
        _ => PipelineNodeType.trigger,
      },
      subtype: json['subtype'] as String,
      config: config,
      position: Offset(x, y),
    );
  }
}

class PipelineEdgeModel {
  const PipelineEdgeModel({
    required this.fromNode,
    required this.toNode,
    this.fromPort = PipelinePortSide.right,
    this.toPort = PipelinePortSide.left,
  });

  final String fromNode;
  final String toNode;
  final PipelinePortSide fromPort;
  final PipelinePortSide toPort;

  Map<String, dynamic> toJson() => toApiJson();

  Map<String, dynamic> toApiJson() => {
        'from': fromNode,
        'to': toNode,
        'from_port': fromPort.apiValue,
        'to_port': toPort.apiValue,
      };

  /// Graph payload shape used by dry-run test requests.
  Map<String, dynamic> toGraphJson() => {
        'source': fromNode,
        'target': toNode,
        'fromPort': fromPort.name,
        'toPort': toPort.name,
        'from': fromNode,
        'to': toNode,
        'from_port': fromPort.apiValue,
        'to_port': toPort.apiValue,
      };

  factory PipelineEdgeModel.fromJson(Map<String, dynamic> json) {
    return PipelineEdgeModel(
      fromNode: json['from'] as String,
      toNode: json['to'] as String,
      fromPort: PipelinePortSide.fromApiValue(
        json['from_port'] as String?,
        fallback: PipelinePortSide.right,
      ),
      toPort: PipelinePortSide.fromApiValue(
        json['to_port'] as String?,
        fallback: PipelinePortSide.left,
      ),
    );
  }

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        other is PipelineEdgeModel &&
            fromNode == other.fromNode &&
            toNode == other.toNode &&
            fromPort == other.fromPort &&
            toPort == other.toPort;
  }

  @override
  int get hashCode => Object.hash(fromNode, toNode, fromPort, toPort);
}

class AutomationPipelineModel {
  const AutomationPipelineModel({
    this.id,
    required this.name,
    this.description,
    this.isActive = true,
    this.nodes = const [],
    this.edges = const [],
  });

  final String? id;
  final String name;
  final String? description;
  final bool isActive;
  final List<PipelineNodeModel> nodes;
  final List<PipelineEdgeModel> edges;

  factory AutomationPipelineModel.fromExportDocument(Map<String, dynamic> doc) {
    final pipeline = doc['pipeline'] as Map<String, dynamic>? ?? doc;
    final nodesRaw = pipeline['nodes'] ?? pipeline['nodes_json'];
    final edgesRaw = pipeline['edges'] ?? pipeline['edges_json'];
    final nodes = (nodesRaw as List<dynamic>? ?? [])
        .map((e) => PipelineNodeModel.fromJson(e as Map<String, dynamic>))
        .toList();
    final edges = (edgesRaw as List<dynamic>? ?? [])
        .map((e) => PipelineEdgeModel.fromJson(e as Map<String, dynamic>))
        .toList();
    return AutomationPipelineModel(
      id: pipeline['id']?.toString(),
      name: pipeline['name'] as String? ?? 'Imported Pipeline',
      description: pipeline['description'] as String?,
      isActive: pipeline['is_active'] as bool? ?? true,
      nodes: nodes,
      edges: edges,
    );
  }

  Map<String, dynamic> toExportDocument() {
    return {
      'schema_version': 'next-iot.automation-pipeline.v1',
      'pipeline': {
        if (id != null) 'id': id,
        'name': name,
        'description': description,
        'is_active': isActive,
        'nodes': nodes.map((n) => n.toApiJson()).toList(),
        'edges': edges.map((e) => e.toApiJson()).toList(),
      },
    };
  }

  factory AutomationPipelineModel.fromJson(Map<String, dynamic> json) {
    final nodes = (json['nodes_json'] as List<dynamic>? ?? [])
        .map((e) => PipelineNodeModel.fromJson(e as Map<String, dynamic>))
        .toList();
    final edges = (json['edges_json'] as List<dynamic>? ?? [])
        .map((e) => PipelineEdgeModel.fromJson(e as Map<String, dynamic>))
        .toList();
    return AutomationPipelineModel(
      id: json['id']?.toString(),
      name: json['name'] as String,
      description: json['description'] as String?,
      isActive: json['is_active'] as bool? ?? true,
      nodes: nodes,
      edges: edges,
    );
  }

  Map<String, dynamic> toCreateJson() {
    return {
      'name': name,
      'description': description,
      'is_active': isActive,
      'nodes_json': nodes.map((n) => n.toApiJson()).toList(),
      'edges_json': edges.map((e) => e.toApiJson()).toList(),
    };
  }

  Map<String, dynamic> toGraphJson() {
    return {
      'nodes': nodes.map((n) => n.toApiJson()).toList(),
      'edges': edges.map((e) => e.toGraphJson()).toList(),
    };
  }
}

class PipelineExecutionStepModel {
  const PipelineExecutionStepModel({
    required this.nodeId,
    required this.nodeType,
    required this.subtype,
    required this.matched,
    this.result = const {},
  });

  final String nodeId;
  final String nodeType;
  final String subtype;
  final bool matched;
  final Map<String, dynamic> result;

  factory PipelineExecutionStepModel.fromJson(Map<String, dynamic> json) {
    return PipelineExecutionStepModel(
      nodeId: json['node_id'] as String,
      nodeType: json['node_type'] as String,
      subtype: json['subtype'] as String,
      matched: json['matched'] as bool? ?? false,
      result: Map<String, dynamic>.from(json['result'] as Map? ?? {}),
    );
  }
}

class PipelineValidationResult {
  const PipelineValidationResult({
    required this.valid,
    this.errors = const [],
    this.warnings = const [],
  });

  final bool valid;
  final List<String> errors;
  final List<String> warnings;

  factory PipelineValidationResult.fromJson(Map<String, dynamic> json) {
    return PipelineValidationResult(
      valid: json['valid'] as bool? ?? false,
      errors: (json['errors'] as List<dynamic>? ?? [])
          .map((e) => e.toString())
          .toList(),
      warnings: (json['warnings'] as List<dynamic>? ?? [])
          .map((e) => e.toString())
          .toList(),
    );
  }
}

class PipelineTestRunResult {
  const PipelineTestRunResult({
    required this.pipelineId,
    required this.pipelineName,
    required this.eventType,
    required this.executed,
    required this.steps,
  });

  final String pipelineId;
  final String pipelineName;
  final String eventType;
  final bool executed;
  final List<PipelineExecutionStepModel> steps;

  factory PipelineTestRunResult.fromJson(Map<String, dynamic> json) {
    final steps = (json['steps'] as List<dynamic>? ?? [])
        .map((e) =>
            PipelineExecutionStepModel.fromJson(e as Map<String, dynamic>))
        .toList();
    return PipelineTestRunResult(
      pipelineId: json['pipeline_id']?.toString() ?? '',
      pipelineName: json['pipeline_name'] as String,
      eventType: json['event_type'] as String,
      executed: json['executed'] as bool? ?? false,
      steps: steps,
    );
  }
}
