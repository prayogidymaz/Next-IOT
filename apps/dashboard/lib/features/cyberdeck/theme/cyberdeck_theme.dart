import 'package:flutter/material.dart';

abstract final class CyberdeckColors {
  static const background = Color(0xFF000000);
  static const panel = Color(0xFF0A0A0A);
  static const border = Color(0xFF1F1F1F);
  static const amber = Color(0xFFFFB000);
  static const green = Color(0xFF39FF14);
  static const red = Color(0xFFFF3131);
  static const text = Color(0xFFE8E8E8);
  static const muted = Color(0xFF6B7280);
}

ThemeData cyberdeckTheme() {
  return ThemeData(
    brightness: Brightness.dark,
    scaffoldBackgroundColor: CyberdeckColors.background,
    fontFamily: 'Courier New',
    colorScheme: const ColorScheme.dark(
      primary: CyberdeckColors.amber,
      secondary: CyberdeckColors.green,
      surface: CyberdeckColors.panel,
      onSurface: CyberdeckColors.text,
    ),
    textTheme: const TextTheme(
      titleLarge: TextStyle(
        color: CyberdeckColors.amber,
        fontWeight: FontWeight.w700,
        letterSpacing: 1.2,
      ),
      bodyMedium: TextStyle(color: CyberdeckColors.text, fontFamily: 'Courier New'),
    ),
  );
}
