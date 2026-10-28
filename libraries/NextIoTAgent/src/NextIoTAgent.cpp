#include "NextIoTAgent.h"

#include <WiFi.h>
#include <HTTPClient.h>
#include <PubSubClient.h>

#include "MeshProtocol.h"
#include "OTAUpdater.h"

static WiFiClient wifiClient;
static PubSubClient mqttClient(wifiClient);

bool NextIoTAgent::begin(const char* wifiSsid, const char* wifiPass, const char* mqttBroker, const char* deviceToken) {
  (void)deviceToken;
  WiFi.begin(wifiSsid, wifiPass);
  mqttClient.setServer(mqttBroker, 1883);
  return WiFi.status() == WL_CONNECTED;
}

bool NextIoTAgent::registerDevice(const char* deviceType, const char* capabilitiesJson) {
  (void)deviceType;
  (void)capabilitiesJson;
  return true;
}

bool NextIoTAgent::publishSensor(const char* metric, float value, const char* unit) {
  char topic[96];
  snprintf(topic, sizeof(topic), NEXT_IOT_MQTT_SENSOR_TOPIC, _deviceId, metric);
  char payload[64];
  snprintf(payload, sizeof(payload), "{\"value\":%.3f,\"unit\":\"%s\"}", value, unit);
  return mqttClient.publish(topic, payload);
}

void NextIoTAgent::subscribeActuator(std::function<void(const char*, const char*)> callback) {
  (void)callback;
}

bool NextIoTAgent::checkOTA() {
  OTAUpdater updater;
  return updater.checkAndUpdate("http://localhost:8000", "esp32_sensor", "0.0.0");
}

void NextIoTAgent::heartbeat(unsigned long intervalMs) {
  (void)intervalMs;
  publishSensor("heartbeat", 1.0f, "bool");
}
