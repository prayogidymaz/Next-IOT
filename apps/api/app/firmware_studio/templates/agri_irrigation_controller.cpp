// Next-IoT Agriculture — LoRa irrigation valve controller (relay + solenoid)
#include <Arduino.h>

void setup() {
  pinMode(RELAY_PIN, OUTPUT);
  digitalWrite(RELAY_PIN, LOW);
}

void loop() {
  // listen downlink open/close; fail-safe close after 2h idle
  delay(1000);
}
