#include <NextIoTAgent.h>

NextIoTAgent agent;

void setup() {
  agent.begin(WIFI_SSID, WIFI_PASS, MQTT_BROKER, DEVICE_TOKEN);
  agent.registerDevice("esp32_sensor", "[\"temp\",\"humidity\"]");
}

void loop() {
  agent.publishSensor("temp", 28.4, "C");
  agent.publishSensor("humidity", 71.0, "%");
  agent.checkOTA();
  delay(15000);
}
