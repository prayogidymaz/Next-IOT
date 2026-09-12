class AiDetectionBox {
  const AiDetectionBox({
    required this.targetType,
    required this.confidence,
    required this.bbox,
  });

  final String targetType;
  final double confidence;
  final List<double> bbox;

  factory AiDetectionBox.fromJson(Map<String, dynamic> json) => AiDetectionBox(
        targetType: json['target_type'] as String,
        confidence: (json['confidence'] as num).toDouble(),
        bbox: (json['bbox'] as List<dynamic>).map((e) => (e as num).toDouble()).toList(),
      );
}

class VideoStreamInfo {
  const VideoStreamInfo({
    required this.deviceId,
    required this.codec,
    required this.streamProtocol,
    required this.fps,
    required this.resolution,
  });

  final String deviceId;
  final String codec;
  final String streamProtocol;
  final double fps;
  final String resolution;

  factory VideoStreamInfo.fromJson(Map<String, dynamic> json) => VideoStreamInfo(
        deviceId: json['device_id'] as String,
        codec: json['codec'] as String,
        streamProtocol: json['stream_protocol'] as String,
        fps: (json['fps'] as num).toDouble(),
        resolution: json['resolution'] as String,
      );
}

class VideoFrameMessage {
  const VideoFrameMessage({
    required this.deviceId,
    required this.frameIndex,
    required this.timestamp,
    required this.codec,
    required this.frameB64,
    required this.width,
    required this.height,
    required this.detections,
  });

  final String deviceId;
  final int frameIndex;
  final DateTime timestamp;
  final String codec;
  final String frameB64;
  final int width;
  final int height;
  final List<AiDetectionBox> detections;

  factory VideoFrameMessage.fromJson(Map<String, dynamic> json) {
    final rawDetections = json['detections'] as List<dynamic>? ?? [];
    return VideoFrameMessage(
      deviceId: json['device_id'] as String,
      frameIndex: json['frame_index'] as int,
      timestamp: DateTime.parse(json['timestamp'] as String),
      codec: json['codec'] as String,
      frameB64: json['frame_b64'] as String,
      width: json['width'] as int,
      height: json['height'] as int,
      detections: rawDetections
          .map((e) => AiDetectionBox.fromJson(e as Map<String, dynamic>))
          .toList(),
    );
  }
}

enum VideoPanelLayout { pip, splitScreen }
