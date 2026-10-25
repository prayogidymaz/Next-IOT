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
static lv_timer_t *s_motion_timer = nullptr;
static lv_timer_t *s_vision_timer = nullptr;
static lv_timer_t *s_dispatch_timer = nullptr;
static lv_timer_t *s_workflow_timer = nullptr;
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
    payload["summary"] = "sensor reading";

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
    payload["summary"] = "alarm created";

    mock_publish_json("tenants/tenant-dev/mesh/events/security/alarm", doc);
    (void)std::printf("[MOCK MQTT] publish alarm.created\n");
}

static void mock_emit_motion(lv_timer_t *timer) {
    (void)timer;

    JsonDocument doc;
    doc["event_type"] = "motion_detected";
    doc["domain"] = "vision";
    JsonObject payload = doc["payload"].to<JsonObject>();
    payload["title"] = "Ulat grayak terdeteksi";
    payload["subtitle"] = "Plot B • Edge AI YOLO v8";
    payload["pest_pct"] = 80 + static_cast<int>(s_mock_tick % 10);
    payload["summary"] = "motion_detected";

    mock_publish_json("tenants/tenant-dev/mesh/events/vision/motion", doc);
    (void)std::printf("[MOCK MQTT] publish vision/motion_detected\n");
}

static void mock_emit_vision_capture(lv_timer_t *timer) {
    (void)timer;

    JsonDocument doc;
    doc["event_type"] = "image_captured";
    doc["domain"] = "vision";
    JsonObject payload = doc["payload"].to<JsonObject>();
    payload["summary"] = "ndvi frame captured";

    mock_publish_json("tenants/tenant-dev/mesh/events/vision/capture", doc);
    (void)std::printf("[MOCK MQTT] publish vision/image_captured\n");
}

static void mock_publish_workflow_event(const char *event_type, int step, int total) {
    JsonDocument doc;
    doc["event_type"] = event_type;
    doc["domain"] = "workflow";
    JsonObject payload = doc["payload"].to<JsonObject>();
    payload["workflow_name"] = "irrigate_plot_a";
    payload["correlation_id"] = "corr-mock-1";
    payload["step"] = step;
    payload["total"] = total;
    payload["summary"] = event_type;
    mock_publish_json("tenants/tenant-dev/mesh/workflow_executions/corr-mock-1", doc);
}

static void mock_emit_workflow(lv_timer_t *timer) {
    (void)timer;
    mock_publish_workflow_event("execution_started", 0, 3);
    mock_publish_workflow_event("execution_step", 1, 3);
    mock_publish_workflow_event("execution_step", 2, 3);
    mock_publish_workflow_event("execution_step", 3, 3);
    mock_publish_workflow_event("execution_completed", 3, 3);
    (void)std::printf("[MOCK MQTT] publish workflow execution chain\n");
}

static void mock_emit_dispatch(lv_timer_t *timer) {
    (void)timer;

    JsonDocument doc;
    doc["event_type"] = "dispatch_requested";
    doc["domain"] = "motion";
    JsonObject payload = doc["payload"].to<JsonObject>();
    payload["node"] = "DRN";
    payload["summary"] = "drone dispatch";

    mock_publish_json("tenants/tenant-dev/mesh/events/motion/dispatch", doc);
    (void)std::printf("[MOCK MQTT] publish motion/dispatch_requested\n");
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
    if (s_motion_timer == nullptr) {
        s_motion_timer = lv_timer_create(mock_emit_motion, 90000, nullptr);
    }
    if (s_vision_timer == nullptr) {
        s_vision_timer = lv_timer_create(mock_emit_vision_capture, 120000, nullptr);
    }
    if (s_dispatch_timer == nullptr) {
        s_dispatch_timer = lv_timer_create(mock_emit_dispatch, 150000, nullptr);
    }
    if (s_workflow_timer == nullptr) {
        s_workflow_timer = lv_timer_create(mock_emit_workflow, 60000, nullptr);
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
