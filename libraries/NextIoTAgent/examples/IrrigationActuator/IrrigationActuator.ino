#include <NextIoTAgent.h>

NextIoTAgent agent;

void setup() {
  agent.begin(WIFI_SSID, WIFI_PASS, MQTT_BROKER, DEVICE_TOKEN);
  agent.registerDevice("esp32_actuator", "[\"valve\"]");
  agent.subscribeActuator([](const char* topic, const char* payload) {
    (void)topic;
    (void)payload;
  });
}

void loop() {
  agent.heartbeat();
  delay(30000);
}
