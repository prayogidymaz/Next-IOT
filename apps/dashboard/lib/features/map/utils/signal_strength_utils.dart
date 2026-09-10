import 'package:flutter/material.dart';

import '../../../core/theme/tactical_theme.dart';

enum SignalStrengthBand { strong, marginal, weak }

SignalStrengthBand bandForRssi(double rssi) {
  if (rssi > -85) return SignalStrengthBand.strong;
  if (rssi >= -105) return SignalStrengthBand.marginal;
  return SignalStrengthBand.weak;
}

Color colorForRssi(double rssi) {
  switch (bandForRssi(rssi)) {
    case SignalStrengthBand.strong:
      return TacticalColors.success;
    case SignalStrengthBand.marginal:
      return TacticalColors.warning;
    case SignalStrengthBand.weak:
      return TacticalColors.critical;
  }
}

String labelForBand(SignalStrengthBand band) {
  switch (band) {
    case SignalStrengthBand.strong:
      return 'Strong (> -85 dBm)';
    case SignalStrengthBand.marginal:
      return 'Marginal (-85 to -105 dBm)';
    case SignalStrengthBand.weak:
      return 'Weak (< -105 dBm)';
  }
}
