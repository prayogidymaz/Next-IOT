import 'package:flutter/material.dart';

abstract final class FieldColors {
  static const page = Color(0xFFF9F8F6);
  static const card = Color(0xFFFFFFFF);
  static const border = Color(0xFFECECE8);
  static const ink = Color(0xFF1A1A1A);
  static const inkMuted = Color(0xFF666666);
  static const emerald = Color(0xFF10B981);
  static const amber = Color(0xFFF59E0B);
  static const indigo = Color(0xFF4F46E5);
  static const danger = Color(0xFFDC2626);
}

ThemeData buildFieldTheme() {
  final base = ThemeData(
    useMaterial3: true,
    colorScheme: ColorScheme.fromSeed(
      seedColor: FieldColors.emerald,
      surface: FieldColors.page,
    ),
    scaffoldBackgroundColor: FieldColors.page,
    fontFamily: 'Roboto',
  );
  return base.copyWith(
    appBarTheme: const AppBarTheme(
      backgroundColor: FieldColors.card,
      foregroundColor: FieldColors.ink,
      elevation: 0,
      centerTitle: false,
    ),
    cardTheme: CardTheme(
      color: FieldColors.card,
      elevation: 0,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(16),
        side: const BorderSide(color: FieldColors.border),
      ),
    ),
  );
}
