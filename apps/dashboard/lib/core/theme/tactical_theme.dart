import 'package:flutter/material.dart';

/// Modern Bento Grid design tokens (Behance-style dark UI).
abstract final class BentoTokens {
  static const background = Color(0xFF0F1015);
  static const backgroundAlt = Color(0xFF16171D);
  static const surfaceSecondary = Color(0xFF1C1D24);
  static const accentLime = Color(0xFFD0F500);
  static const accentLimeAlt = Color(0xFFC8F902);
  static const accentLavender = Color(0xFFE5D4FF);
  static const accentSoftBlue = Color(0xFFB4E4FF);
  static const borderSubtle = Color(0xFF2A2B33);
  static const radius = 24.0;
  static const radiusPill = 999.0;
}

/// Semantic palette — mapped to Bento accents for minimal churn across the app.
abstract final class TacticalColors {
  static const background = BentoTokens.background;
  static const surface = BentoTokens.backgroundAlt;
  static const surfaceElevated = BentoTokens.surfaceSecondary;
  static const border = BentoTokens.borderSubtle;
  static const borderNeon = BentoTokens.accentSoftBlue;
  static const cyan = BentoTokens.accentSoftBlue;
  static const cyanGlow = Color(0x00000000);
  static const textPrimary = Color(0xFFF4F4F6);
  static const textSecondary = Color(0xFF9CA3AF);
  static const critical = Color(0xFFF87171);
  static const warning = Color(0xFFFBBF24);
  static const success = BentoTokens.accentLime;
  static const info = BentoTokens.accentLavender;
}

ThemeData buildTacticalTheme() {
  const scheme = ColorScheme.dark(
    surface: TacticalColors.surface,
    primary: TacticalColors.success,
    onPrimary: Color(0xFF0F1015),
    secondary: BentoTokens.accentLavender,
    onSecondary: Color(0xFF0F1015),
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
        letterSpacing: -0.2,
        color: TacticalColors.textPrimary,
      ),
      titleLarge: TextStyle(
        fontWeight: FontWeight.w700,
        letterSpacing: -0.3,
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
      labelLarge: TextStyle(
        fontWeight: FontWeight.w600,
        letterSpacing: 0.4,
        color: TacticalColors.textSecondary,
      ),
    ),
    appBarTheme: const AppBarTheme(
      backgroundColor: TacticalColors.background,
      foregroundColor: TacticalColors.textPrimary,
      elevation: 0,
      centerTitle: false,
    ),
    cardTheme: CardTheme(
      color: TacticalColors.surfaceElevated,
      elevation: 0,
      margin: EdgeInsets.zero,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(BentoTokens.radius),
        side: BorderSide(color: TacticalColors.border.withOpacity(0.85)),
      ),
    ),
    inputDecorationTheme: InputDecorationTheme(
      filled: true,
      fillColor: TacticalColors.surface,
      border: OutlineInputBorder(
        borderRadius: BorderRadius.circular(16),
        borderSide: const BorderSide(color: TacticalColors.border),
      ),
      enabledBorder: OutlineInputBorder(
        borderRadius: BorderRadius.circular(16),
        borderSide: const BorderSide(color: TacticalColors.border),
      ),
      focusedBorder: OutlineInputBorder(
        borderRadius: BorderRadius.circular(16),
        borderSide: const BorderSide(color: BentoTokens.accentSoftBlue, width: 1.5),
      ),
      labelStyle: const TextStyle(color: TacticalColors.textSecondary),
    ),
    filledButtonTheme: FilledButtonThemeData(
      style: FilledButton.styleFrom(
        backgroundColor: TacticalColors.success,
        foregroundColor: const Color(0xFF0F1015),
        padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 14),
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(BentoTokens.radiusPill),
        ),
      ),
    ),
    outlinedButtonTheme: OutlinedButtonThemeData(
      style: OutlinedButton.styleFrom(
        foregroundColor: TacticalColors.textPrimary,
        side: const BorderSide(color: TacticalColors.border),
        padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 14),
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(BentoTokens.radiusPill),
        ),
      ),
    ),
    dividerTheme:
        const DividerThemeData(color: TacticalColors.border, thickness: 1),
    navigationRailTheme: NavigationRailThemeData(
      backgroundColor: TacticalColors.surface,
      selectedIconTheme: const IconThemeData(color: TacticalColors.success),
      unselectedIconTheme: const IconThemeData(color: TacticalColors.textSecondary),
      selectedLabelTextStyle: const TextStyle(
        color: TacticalColors.success,
        fontWeight: FontWeight.w600,
      ),
      unselectedLabelTextStyle: const TextStyle(color: TacticalColors.textSecondary),
      indicatorColor: TacticalColors.success.withOpacity(0.12),
    ),
  );
}
