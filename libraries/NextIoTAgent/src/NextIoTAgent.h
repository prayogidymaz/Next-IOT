#pragma once

#include <functional>

class NextIoTAgent {
 public:
  bool begin(const char* wifiSsid, const char* wifiPass, const char* mqttBroker, const char* deviceToken);
  bool registerDevice(const char* deviceType, const char* capabilitiesJson);
  bool publishSensor(const char* metric, float value, const char* unit);
  void subscribeActuator(std::function<void(const char* topic, const char* payload)> callback);
  bool checkOTA();
  void heartbeat(unsigned long intervalMs = 30000);

 private:
  const char* _deviceId = "";
};
