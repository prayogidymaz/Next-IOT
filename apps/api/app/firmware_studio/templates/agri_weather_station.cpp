// Next-IoT Agriculture — LoRa weather station (BME280 + anemometer + rain)
#include <Arduino.h>

void setup() {
  Serial.begin(115200);
}

void loop() {
  // every 5 min: temp, humidity, pressure, wind, rainfall_mm
  delay(300000);
}
