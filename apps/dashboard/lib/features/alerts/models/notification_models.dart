class ProviderDispatchResult {
  const ProviderDispatchResult({
    required this.provider,
    required this.success,
    required this.attempts,
    this.error,
  });

  final String provider;
  final bool success;
  final int attempts;
  final String? error;

  factory ProviderDispatchResult.fromJson(Map<String, dynamic> json) => ProviderDispatchResult(
        provider: json['provider'] as String,
        success: json['success'] as bool,
        attempts: json['attempts'] as int,
        error: json['error'] as String?,
      );
}

class NotificationTestResponse {
  const NotificationTestResponse({required this.results});

  final List<ProviderDispatchResult> results;

  bool get telegramSuccess =>
      results.any((r) => r.provider == 'telegram' && r.success);

  String? get telegramError =>
      results.where((r) => r.provider == 'telegram').map((r) => r.error).whereType<String>().firstOrNull;

  factory NotificationTestResponse.fromJson(Map<String, dynamic> json) {
    final raw = json['results'] as List<dynamic>? ?? [];
    return NotificationTestResponse(
      results: raw
          .map((e) => ProviderDispatchResult.fromJson(e as Map<String, dynamic>))
          .toList(),
    );
  }
}

extension _FirstOrNull<E> on Iterable<E> {
  E? get firstOrNull {
    final it = iterator;
    if (!it.moveNext()) return null;
    return it.current;
  }
}
