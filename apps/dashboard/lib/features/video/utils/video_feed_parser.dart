import '../models/video_feed_models.dart';

VideoStreamInfo? parseVideoFeedStreamInfo(Map<String, dynamic> json) {
  if (json['type'] != 'stream_info') return null;
  return VideoStreamInfo.fromJson(json);
}

VideoFrameMessage? parseVideoFeedFrame(Map<String, dynamic> json) {
  if (json['type'] != 'video_frame') return null;
  return VideoFrameMessage.fromJson(json);
}

AiDetectionBox? parseDetectionBox(Map<String, dynamic> json) {
  final bbox = json['bbox'];
  if (bbox is! List || bbox.length != 4) return null;
  for (final value in bbox) {
    if (value is! num || value < 0 || value > 1) return null;
  }
  final targetType = json['target_type'];
  if (targetType != 'person' && targetType != 'vehicle') return null;
  final confidence = json['confidence'];
  if (confidence is! num || confidence < 0 || confidence > 1) return null;
  return AiDetectionBox.fromJson(json);
}
