import "package:flutter/material.dart";
import "package:flutter_test/flutter_test.dart";
import "package:next_iot_wear/theme/tactical_warm_cream.dart";

void main() {
  test("default widget test defers to wear_screens_test", () {
    expect(TacticalWarmCream.critical, const Color(0xFFB23A3A));
  });
}
