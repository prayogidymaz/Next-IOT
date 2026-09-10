import 'package:flutter_test/flutter_test.dart';
import 'package:next_iot_dashboard/core/theme/tactical_theme.dart';
import 'package:next_iot_dashboard/features/map/utils/signal_strength_utils.dart';

void main() {
  test('bandForRssi maps thresholds correctly', () {
    expect(bandForRssi(-80), SignalStrengthBand.strong);
    expect(bandForRssi(-95), SignalStrengthBand.marginal);
    expect(bandForRssi(-110), SignalStrengthBand.weak);
  });

  test('colorForRssi returns tactical palette colors', () {
    expect(colorForRssi(-80), TacticalColors.success);
    expect(colorForRssi(-95), TacticalColors.warning);
    expect(colorForRssi(-110), TacticalColors.critical);
  });
}
