import 'package:flutter/material.dart';

/// Tactical Control Center palette.
abstract final class TacticalColors {
  static const background = Color(0xFF0F172A);
  static const surface = Color(0xFF1E293B);
  static const surfaceElevated = Color(0xFF243044);
  static const border = Color(0xFF334155);
  static const borderNeon = Color(0xFF22D3EE);
  static const cyan = Color(0xFF06B6D4);
  static const cyanGlow = Color(0x6622D3EE);
  static const textPrimary = Color(0xFFF1F5F9);
  static const textSecondary = Color(0xFF94A3B8);
  static const critical = Color(0xFFEF4444);
  static const warning = Color(0xFFF59E0B);
  static const success = Color(0xFF22C55E);
  static const info = Color(0xFF3B82F6);
}

ThemeData buildTacticalTheme() {
  const scheme = ColorScheme.dark(
    surface: TacticalColors.surface,
    primary: TacticalColors.cyan,
    onPrimary: TacticalColors.background,
    secondary: TacticalColors.borderNeon,
    onSecondary: TacticalColors.background,
    error: TacticalColors.critical,
    onSurface: TacticalColors.textPrimary,
    outline: TacticalColors.border,
  );

  return ThemeData(
    useMaterial3: true,
    brightness: Brightness.dark,
    scaffoldBackgroundColor: TacticalColors.background,
    colorScheme: scheme,
    fontFamily: 'Segoe UI',
    textTheme: const TextTheme(
      headlineSmall: TextStyle(
        fontWeight: FontWeight.w700,
        letterSpacing: 0.5,
        color: TacticalColors.textPrimary,
      ),
      titleLarge: TextStyle(
        fontWeight: FontWeight.w700,
        letterSpacing: 0.3,
        color: TacticalColors.textPrimary,
      ),
      titleMedium: TextStyle(
        fontWeight: FontWeight.w600,
        color: TacticalColors.textPrimary,
      ),
      titleSmall: TextStyle(
        fontWeight: FontWeight.w600,
        color: TacticalColors.textSecondary,
      ),
      bodyMedium: TextStyle(color: TacticalColors.textSecondary),
      bodySmall: TextStyle(color: TacticalColors.textSecondary, fontSize: 12),
      labelLarge: TextStyle(fontWeight: FontWeight.w600, letterSpacing: 0.8),
    ),
    appBarTheme: const AppBarTheme(
      backgroundColor: TacticalColors.surface,
      foregroundColor: TacticalColors.textPrimary,
      elevation: 0,
      centerTitle: false,
    ),
    cardTheme: CardTheme(
      color: TacticalColors.surfaceElevated,
      elevation: 0,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(12),
        side: const BorderSide(color: TacticalColors.border),
      ),
    ),
    inputDecorationTheme: InputDecorationTheme(
      filled: true,
      fillColor: TacticalColors.background,
      border: OutlineInputBorder(
        borderRadius: BorderRadius.circular(8),
        borderSide: const BorderSide(color: TacticalColors.border),
      ),
      enabledBorder: OutlineInputBorder(
        borderRadius: BorderRadius.circular(8),
        borderSide: const BorderSide(color: TacticalColors.border),
      ),
      focusedBorder: OutlineInputBorder(
        borderRadius: BorderRadius.circular(8),
        borderSide: const BorderSide(color: TacticalColors.borderNeon, width: 1.5),
      ),
      labelStyle: const TextStyle(color: TacticalColors.textSecondary),
    ),
    filledButtonTheme: FilledButtonThemeData(
      style: FilledButton.styleFrom(
        backgroundColor: TacticalColors.cyan,
        foregroundColor: TacticalColors.background,
        padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(8)),
      ),
    ),
    outlinedButtonTheme: OutlinedButtonThemeData(
      style: OutlinedButton.styleFrom(
        foregroundColor: TacticalColors.borderNeon,
        side: const BorderSide(color: TacticalColors.borderNeon),
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(8)),
      ),
    ),
    dividerTheme: const DividerThemeData(color: TacticalColors.border, thickness: 1),
    navigationRailTheme: const NavigationRailThemeData(
      backgroundColor: TacticalColors.surface,
      selectedIconTheme: IconThemeData(color: TacticalColors.borderNeon),
      unselectedIconTheme: IconThemeData(color: TacticalColors.textSecondary),
      selectedLabelTextStyle: TextStyle(color: TacticalColors.borderNeon, fontWeight: FontWeight.w600),
      unselectedLabelTextStyle: TextStyle(color: TacticalColors.textSecondary),
      indicatorColor: TacticalColors.cyanGlow,
    ),
  );
}
