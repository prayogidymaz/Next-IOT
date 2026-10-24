import "dart:async";
import "dart:convert";

import "package:http/http.dart" as http;

typedef MeshSseHandler = void Function(Map<String, dynamic> event);

class MeshSseConnection {
  MeshSseConnection({
    required this.baseUrl,
    required this.jwt,
    this.onEvent,
  });

  final String baseUrl;
  final String jwt;
  final MeshSseHandler? onEvent;

  http.Client? _client;
  int _backoffSeconds = 1;
  bool _stopped = false;

  Future<void> connect() async {
    _stopped = false;
    while (!_stopped) {
      try {
        _client = http.Client();
        final request = http.Request(
          "GET",
          Uri.parse("$baseUrl/api/v1/mesh/events/stream"),
        );
        request.headers["Authorization"] = "Bearer $jwt";
        request.headers["Accept"] = "text/event-stream";
        final response = await _client!.send(request);
        if (response.statusCode != 200) {
          await _sleepBackoff();
          continue;
        }
        _backoffSeconds = 1;
        var buffer = "";
        await for (final chunk in response.stream.transform(utf8.decoder)) {
          buffer += chunk;
          final parts = buffer.split("\n\n");
          buffer = parts.removeLast();
          for (final block in parts) {
            _parseBlock(block);
          }
        }
      } catch (_) {
        await _sleepBackoff();
      } finally {
        _client?.close();
        _client = null;
      }
    }
  }

  void stop() {
    _stopped = true;
    _client?.close();
  }

  Future<void> _sleepBackoff() async {
    await Future<void>.delayed(Duration(seconds: _backoffSeconds));
    _backoffSeconds = _backoffSeconds >= 30 ? 30 : _backoffSeconds * 2;
  }

  void _parseBlock(String block) {
    var eventName = "";
    var dataLine = "";
    for (final line in block.split("\n")) {
      if (line.startsWith("event:")) {
        eventName = line.substring(6).trim();
      } else if (line.startsWith("data:")) {
        dataLine = line.substring(5).trim();
      }
    }
    if (eventName != "mesh" || dataLine.isEmpty) {
      return;
    }
    final decoded = jsonDecode(dataLine);
    if (decoded is Map<String, dynamic>) {
      onEvent?.call(decoded);
    }
  }
}
