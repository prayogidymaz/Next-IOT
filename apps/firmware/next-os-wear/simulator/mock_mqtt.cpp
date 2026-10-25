/**
 * Mock MQTT untuk simulator PC — produksi event mesh periodik.
 */
#include "mqtt.h"

#include "config.h"
#include "mesh/handler.h"

#include <ArduinoJson.h>

#include <cstdio>

#include <lvgl.h>

static bool s_connected = false;
static lv_timer_t *s_sensor_timer = nullptr;
static lv_timer_t *s_alert_timer = nullptr;
static uint8_t s_mock_tick = 0;

static void mock_publish_json(const char *topic, JsonDocument &doc) {
    char buffer[384];
    const size_t len = serializeJson(doc, buffer, sizeof(buffer));
    next_os_mesh_handler_on_message(topic, reinterpret_cast<const uint8_t *>(buffer), len);
}

static void mock_emit_sensor(lv_timer_t *timer) {
    (void)timer;
    s_mock_tick++;

    JsonDocument doc;
    doc["event_type"] = "sensor.reading_update";
    doc["domain"] = "sensor";
    JsonObject payload = doc["payload"].to<JsonObject>();
    payload["moisture"] = 60 + static_cast<int>(s_mock_tick % 15);
    payload["ph"] = 6.2 + static_cast<double>(s_mock_tick % 5) * 0.1;
    payload["temp_c"] = 22 + static_cast<int>(s_mock_tick % 6);
    payload["humidity"] = 65 + static_cast<int>(s_mock_tick % 20);
    payload["farm_count"] = 3;

    mock_publish_json("tenants/tenant-dev/mesh/events/sensor/reading", doc);
    (void)std::printf("[MOCK MQTT] publish sensor_update moisture=%d\n",
                      static_cast<int>(payload["moisture"].as<int>()));
}

static void mock_emit_alert(lv_timer_t *timer) {
    (void)timer;

    JsonDocument doc;
    doc["event_type"] = "alarm.created";
    doc["domain"] = "security";
    JsonObject payload = doc["payload"].to<JsonObject>();
    payload["title"] = "Sprayer tank 15%";
    payload["subtitle"] = "Plot B • Refill required";
    payload["severity"] = "CRITICAL";
    payload["ago"] = "2m ago";
    payload["alert_count"] = 3;

    mock_publish_json("tenants/tenant-dev/mesh/events/security/alarm", doc);
    (void)std::printf("[MOCK MQTT] publish alarm.created\n");
}

void next_os_mqtt_init(void) {
    next_os_mesh_handler_init();
}

bool next_os_mqtt_start(void) {
    s_connected = true;
    (void)std::printf("[MOCK MQTT] subscribed to tenants/+/mesh/events/#\n");
    (void)std::printf("[MOCK MQTT] broker=%s:%d device=%s\n", NEXT_OS_MQTT_BROKER_HOST,
                      NEXT_OS_MQTT_BROKER_PORT, NEXT_OS_DEVICE_ID);

    if (s_sensor_timer == nullptr) {
        s_sensor_timer = lv_timer_create(mock_emit_sensor, 10000, nullptr);
    }
    if (s_alert_timer == nullptr) {
        s_alert_timer = lv_timer_create(mock_emit_alert, 60000, nullptr);
    }
    return true;
}

void next_os_mqtt_loop(void) {
    /* Event mesh via lv_timer mock */
}

bool next_os_mqtt_is_connected(void) {
    return s_connected;
}

bool next_os_mqtt_publish_ui_event(const char *event_type, const char *payload_json) {
    (void)std::printf("[MOCK MQTT] ui/%s %s\n", event_type, payload_json != nullptr ? payload_json : "{}");
    return s_connected;
}

bool next_os_mqtt_publish_mesh_event(const char *domain, const char *event_type,
                                     const char *payload_json) {
    (void)std::printf("[MOCK MQTT] mesh/%s/%s %s\n", domain, event_type,
                      payload_json != nullptr ? payload_json : "{}");
    return s_connected;
}
