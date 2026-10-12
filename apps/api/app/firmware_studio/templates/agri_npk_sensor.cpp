// Next-IoT Agriculture — LoRa NPK + pH (RS485), wake hourly
#include <Arduino.h>

void setup() {
  Serial.begin(115200);
  Serial2.begin(9600, SERIAL_8N1, RX_PIN, TX_PIN);
}

void loop() {
  // read N,P,K,pH; uplink; sleep 1h
  esp_deep_sleep(3600 * 1000000ULL);
}
