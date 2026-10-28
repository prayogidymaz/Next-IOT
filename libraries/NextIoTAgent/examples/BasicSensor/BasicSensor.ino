#include <NextIoTAgent.h>

NextIoTAgent agent;

void setup() {
  agent.begin(WIFI_SSID, WIFI_PASS, MQTT_BROKER, DEVICE_TOKEN);
  agent.registerDevice("esp32_sensor", "[\"soil_moisture\"]");
}

void loop() {
  agent.publishSensor("soil_moisture", 42.5, "%");
  agent.heartbeat();
  delay(10000);
}
