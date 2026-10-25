#include "mesh/handler.h"

#include "mesh_state.h"
#include "screens/mesh_ui_sync.h"

#include <ArduinoJson.h>

#include <cstring>

static void copy_str_field(char *dest, size_t dest_len, JsonVariantConst value) {
    if (dest_len == 0) {
        return;
    }
    if (value.isNull() || !value.is<const char *>()) {
        dest[0] = '\0';
        return;
    }
    const char *src = value.as<const char *>();
    if (src == nullptr) {
        dest[0] = '\0';
        return;
    }
    (void)strncpy(dest, src, dest_len - 1U);
    dest[dest_len - 1U] = '\0';
}

static void copy_json_key(char *dest, size_t dest_len, JsonObjectConst body, const char *key,
                          const char *fallback) {
    if (!body[key].isNull()) {
        copy_str_field(dest, dest_len, body[key]);
        if (dest[0] != '\0') {
            return;
        }
    }
    if (fallback != nullptr) {
        (void)strncpy(dest, fallback, dest_len - 1U);
        dest[dest_len - 1U] = '\0';
    }
}

void next_os_mesh_handler_init(void) {
    next_os_mesh_state_init();
}

void next_os_mesh_handler_on_message(const char *topic, const uint8_t *payload, size_t length) {
    if (payload == nullptr || length == 0) {
        return;
    }

    JsonDocument doc;
    const DeserializationError err = deserializeJson(doc, payload, length);
    if (err) {
        return;
    }

    const char *event_type = doc["event_type"] | doc["type"] | "";
    const char *domain = doc["domain"] | "";
    JsonObjectConst body = doc["payload"].as<JsonObjectConst>();
    if (body.isNull()) {
        body = doc.as<JsonObjectConst>();
    }

    (void)topic;
    (void)domain;

    if (strcmp(event_type, "sensor.reading_update") == 0 || strcmp(event_type, "sensor_update") == 0) {
        next_os_mesh_sensor_t reading = next_os_mesh_state_sensor();
        reading.moisture = body["moisture"] | body["moisture_pct"] | reading.moisture;
        reading.ph = body["ph"] | reading.ph;
        reading.temp_c = body["temp_c"] | body["temperature"] | reading.temp_c;
        reading.humidity = body["humidity"] | body["humidity_pct"] | reading.humidity;
        next_os_mesh_state_update_sensor(&reading);
        if (body["farm_count"].is<int>()) {
            next_os_mesh_state_set_farm_count(static_cast<uint8_t>(body["farm_count"].as<int>()));
        }
    } else if (strcmp(event_type, "alarm.created") == 0 || strcmp(event_type, "alert") == 0) {
        next_os_mesh_alert_t alert {};
        alert.unresolved = true;
        if (!body["title"].isNull()) {
            copy_str_field(alert.title, sizeof(alert.title), body["title"]);
        } else {
            copy_json_key(alert.title, sizeof(alert.title), body, "message", "Alert");
        }
        if (!body["subtitle"].isNull()) {
            copy_str_field(alert.subtitle, sizeof(alert.subtitle), body["subtitle"]);
        } else {
            copy_json_key(alert.subtitle, sizeof(alert.subtitle), body, "plot", "");
        }
        copy_json_key(alert.severity, sizeof(alert.severity), body, "severity", "CRITICAL");
        copy_json_key(alert.ago, sizeof(alert.ago), body, "ago", "now");
        next_os_mesh_state_push_alert(&alert);
        if (body["alert_count"].is<int>()) {
            next_os_mesh_state_set_alert_count(static_cast<uint8_t>(body["alert_count"].as<int>()));
        } else {
            next_os_mesh_state_set_alert_count(
                static_cast<uint8_t>(next_os_mesh_state_alert_count() + 1U));
        }
    } else if (strcmp(event_type, "actuator.state_changed") == 0 ||
               strcmp(event_type, "irrigation.state") == 0) {
        next_os_mesh_irrig_t ir = next_os_mesh_state_irrig();
        ir.active = body["active"] | ir.active;
        if (!body["countdown"].isNull()) {
            copy_str_field(ir.countdown, sizeof(ir.countdown), body["countdown"]);
        }
        if (!body["flow"].isNull()) {
            copy_str_field(ir.flow_label, sizeof(ir.flow_label), body["flow"]);
        }
        if (!body["valve"].isNull()) {
            copy_str_field(ir.valve_name, sizeof(ir.valve_name), body["valve"]);
        }
        next_os_mesh_state_update_irrig(&ir);
        if (body["irig_count"].is<int>()) {
            next_os_mesh_state_set_irig_count(static_cast<uint8_t>(body["irig_count"].as<int>()));
        }
    }

    next_os_mesh_ui_sync_refresh();
}
