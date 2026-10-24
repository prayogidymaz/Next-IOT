import "package:flutter/material.dart";

class TacticalWarmCream {
  static const Color base = Color(0xFFF5EFE0);
  static const Color olive = Color(0xFF556B4A);
  static const Color clay = Color(0xFFD97757);
  static const Color critical = Color(0xFFB23A3A);

  static ThemeData theme() {
    const mono = "monospace";
    return ThemeData(
      useMaterial3: true,
      scaffoldBackgroundColor: base,
      colorScheme: ColorScheme.fromSeed(
        seedColor: olive,
        primary: olive,
        secondary: clay,
        error: critical,
        surface: base,
      ),
      textTheme: const TextTheme(
        headlineSmall: TextStyle(
          fontFamily: "Roboto",
          fontWeight: FontWeight.w600,
          color: Color(0xFF2C2C28),
        ),
        bodyMedium: TextStyle(color: Color(0xFF3D3D38)),
        labelLarge: TextStyle(fontFamily: mono, fontWeight: FontWeight.w500),
      ),
      cardTheme: CardTheme(
        color: Colors.white.withOpacity(0.72),
        elevation: 0,
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(16),
          side: const BorderSide(color: Color(0xFFE8DFCF)),
        ),
      ),
    );
  }
}
