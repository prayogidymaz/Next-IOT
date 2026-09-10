import 'package:flutter/foundation.dart';

/// API configuration for Next-IOT backend.
class ApiConfig {
  /// Override via: `flutter run --dart-define=API_BASE_URL=http://10.0.2.2:8000`
  ///
  /// Flutter Web defaults to the local FastAPI container on port 8000.
  static String get baseUrl {
    const fromEnv = String.fromEnvironment('API_BASE_URL');
    if (fromEnv.isNotEmpty) return fromEnv;
    if (kIsWeb) return 'http://localhost:8000';
    return 'http://localhost:8000';
  }

  static const Duration connectTimeout = Duration(seconds: 15);
  static const Duration receiveTimeout = Duration(seconds: 15);
}