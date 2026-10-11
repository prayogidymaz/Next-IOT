#pragma once

#include <ArduinoJson.h>
#include <functional>

#include "NextIotConfig.h"

class NextIotClient {
 public:
  explicit NextIotClient(const NextIotConfig& config);

  void begin();
  void loop();

  void publishTelemetry(const JsonObject& values);
  void publishTelemetry(const char* key, float value);
  void publishClientAttribute(const char* key, const JsonVariant& value);

  void onSharedAttributeUpdate(std::function<void(JsonObject)> callback);
  void onRpcRequest(
      std::function<void(const char* method, JsonObject params, JsonObject& response)> callback);
  void onConnected(std::function<void()> callback);
  void onDisconnected(std::function<void()> callback);

  void enableOta();

  bool isConnected();
  uint32_t uptimeSeconds();
  const char* lastError();

 private:
  NextIotConfig _config;
  bool _connected;
  uint32_t _startedMs;
  char _lastError[128];
  std::function<void()> _onConnected;
  std::function<void()> _onDisconnected;
  std::function<void(JsonObject)> _onSharedAttr;
  std::function<void(const char*, JsonObject, JsonObject&)> _onRpc;
  bool _otaEnabled;
  void _ensureMqtt();
  void _mqttCallback(char* topic, byte* payload, unsigned int length);
  static NextIotClient* _instance;
};
