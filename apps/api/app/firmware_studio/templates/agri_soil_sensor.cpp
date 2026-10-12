// Next-IoT Agriculture — LoRa soil moisture node (ESP32-S3 + SX1262)
#include <Arduino.h>
// OTAA LoRaWAN join, deep sleep 15 min, payload: moisture(1B), temp(2B), battery(1B)

void setup() {
  Serial.begin(115200);
  // TODO: loraWanInit(), sensorInit(), bleCommissioningStart()
}

void loop() {
  // read sensors, uplink, enter deep sleep <50uA
  esp_deep_sleep(15 * 60 * 1000000ULL);
}
