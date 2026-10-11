#include "NextIotClient.h"

#include <PubSubClient.h>
#include <WiFi.h>
#include <time.h>

#include "NextIotOta.h"

namespace {
WiFiClient wifiClient;
PubSubClient mqttClient(wifiClient);
NextIotClient* activeClient = nullptr;

String topicTelemetry(const NextIotConfig& cfg) {
  return String("tenants/") + cfg.tenant_id + "/devices/" + cfg.device_id + "/telemetry";
}

String topicAttributes(const NextIotConfig& cfg) {
  return String("tenants/") + cfg.tenant_id + "/devices/" + cfg.device_id + "/attributes";
}

String topicSharedSub(const NextIotConfig& cfg) {
  return String("tenants/") + cfg.tenant_id + "/devices/" + cfg.device_id + "/attributes/shared/update";
}

String topicRpcSub(const NextIotConfig& cfg) {
  return String("tenants/") + cfg.tenant_id + "/devices/" + cfg.device_id + "/commands/+/request";
}

String topicOtaSub(const NextIotConfig& cfg) {
  return String("tenants/") + cfg.tenant_id + "/devices/" + cfg.device_id + "/ota/update";
}

void syncTimeNtp() {
  configTime(0, 0, "pool.ntp.org", "time.nist.gov");
  for (int i = 0; i < 20; ++i) {
    time_t now = time(nullptr);
    if (now > 1700000000) {
      return;
    }
    delay(250);
  }
}

String isoTimestampUtc() {
  time_t now = time(nullptr);
  struct tm timeinfo;
  gmtime_r(&now, &timeinfo);
  char buffer[32];
  strftime(buffer, sizeof(buffer), "%Y-%m-%dT%H:%M:%SZ", &timeinfo);
  return String(buffer);
}
}  // namespace

NextIotClient* NextIotClient::_instance = nullptr;

NextIotClient::NextIotClient(const NextIotConfig& config)
    : _config(config),
      _connected(false),
      _startedMs(millis()),
      _otaEnabled(false) {
  _lastError[0] = '\0';
  _instance = this;
  activeClient = this;
}

void NextIotClient::_mqttCallback(char* topic, byte* payload, unsigned int length) {
  if (activeClient == nullptr) {
    return;
  }
  StaticJsonDocument<768> doc;
  DeserializationError err = deserializeJson(doc, payload, length);
  if (err) {
    return;
  }
  String topicStr(topic);
  if (topicStr.indexOf("/attributes/shared/update") >= 0) {
    if (activeClient->_onSharedAttr) {
      activeClient->_onSharedAttr(doc.as<JsonObject>());
    }
    return;
  }
  if (topicStr.indexOf("/commands/") >= 0 && topicStr.endsWith("/request")) {
    const char* method = doc["method"] | "unknown";
    JsonObject params = doc["params"].as<JsonObject>();
    StaticJsonDocument<256> responseDoc;
    JsonObject response = responseDoc.to<JsonObject>();
    if (activeClient->_onRpc) {
      activeClient->_onRpc(method, params, response);
    }
    int reqStart = topicStr.lastIndexOf('/') + 1;
    int reqEnd = topicStr.indexOf("/request");
    String reqId = topicStr.substring(reqStart, reqEnd);
    String respTopic = String("tenants/") + activeClient->_config.tenant_id + "/devices/" +
                       activeClient->_config.device_id + "/commands/" + reqId + "/response";
    StaticJsonDocument<384> envelope;
    envelope["response"] = response;
    String out;
    serializeJson(envelope, out);
    mqttClient.publish(respTopic.c_str(), out.c_str());
    return;
  }
  if (topicStr.indexOf("/ota/update") >= 0 && activeClient->_otaEnabled) {
    nextiotOtaHandleMessage(activeClient->_config, doc.as<JsonObject>());
  }
}

void NextIotClient::_ensureMqtt() {
  if (WiFi.status() != WL_CONNECTED) {
    WiFi.begin(_config.wifi_ssid, _config.wifi_password);
    uint32_t start = millis();
    while (WiFi.status() != WL_CONNECTED && millis() - start < 20000) {
      delay(200);
    }
    if (WiFi.status() != WL_CONNECTED) {
      snprintf(_lastError, sizeof(_lastError), "WiFi connect failed");
      return;
    }
    syncTimeNtp();
  }
  if (!mqttClient.connected()) {
    mqttClient.setServer(_config.broker_host, _config.broker_port);
    mqttClient.setCallback(_mqttCallback);
    mqttClient.setBufferSize(1024);
    String clientId = String("next-iot-") + _config.device_id;
    String user = _config.access_token;
    String pass = "";
    if (mqttClient.connect(clientId.c_str(), user.c_str(), pass.c_str())) {
      mqttClient.subscribe(topicSharedSub(_config).c_str());
      mqttClient.subscribe(topicRpcSub(_config).c_str());
      if (_otaEnabled) {
        mqttClient.subscribe(topicOtaSub(_config).c_str());
      }
      _connected = true;
      if (_onConnected) {
        _onConnected();
      }
    } else {
      _connected = false;
      snprintf(_lastError, sizeof(_lastError), "MQTT connect failed rc=%d", mqttClient.state());
      if (_onDisconnected) {
        _onDisconnected();
      }
    }
  }
}

void NextIotClient::begin() {
  _startedMs = millis();
  _ensureMqtt();
}

void NextIotClient::loop() {
  _ensureMqtt();
  mqttClient.loop();
}

void NextIotClient::publishTelemetry(const JsonObject& values) {
  StaticJsonDocument<512> doc;
  doc["ts"] = isoTimestampUtc();
  JsonObject outValues = doc["values"].to<JsonObject>();
  for (JsonPair kv : values) {
    outValues[kv.key()] = kv.value();
  }
  String payload;
  serializeJson(doc, payload);
  _ensureMqtt();
  mqttClient.publish(topicTelemetry(_config).c_str(), payload.c_str());
}

void NextIotClient::publishTelemetry(const char* key, float value) {
  StaticJsonDocument<128> doc;
  JsonObject values = doc.to<JsonObject>();
  values[key] = value;
  publishTelemetry(values);
}

void NextIotClient::publishClientAttribute(const char* key, const JsonVariant& value) {
  StaticJsonDocument<128> doc;
  doc[key] = value;
  String payload;
  serializeJson(doc, payload);
  _ensureMqtt();
  mqttClient.publish(topicAttributes(_config).c_str(), payload.c_str());
}

void NextIotClient::onSharedAttributeUpdate(std::function<void(JsonObject)> callback) {
  _onSharedAttr = callback;
}

void NextIotClient::onRpcRequest(
    std::function<void(const char* method, JsonObject params, JsonObject& response)> callback) {
  _onRpc = callback;
}

void NextIotClient::onConnected(std::function<void()> callback) {
  _onConnected = callback;
}

void NextIotClient::onDisconnected(std::function<void()> callback) {
  _onDisconnected = callback;
}

void NextIotClient::enableOta() {
  _otaEnabled = true;
  _config.enable_ota = true;
}

bool NextIotClient::isConnected() {
  return _connected && mqttClient.connected();
}

uint32_t NextIotClient::uptimeSeconds() {
  return (millis() - _startedMs) / 1000U;
}

const char* NextIotClient::lastError() {
  return _lastError;
}
