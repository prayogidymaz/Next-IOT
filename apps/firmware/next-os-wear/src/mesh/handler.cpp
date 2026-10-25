#include "mesh/handler.h"

#include "mesh_state.h"
#include "screens/mesh_ui_sync.h"

#include <ArduinoJson.h>

#include <cstdio>
#include <cstring>
#include <ctime>

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

static void mesh_format_time_hms(char *buf, size_t len) {
    const std::time_t now = std::time(nullptr);
    std::tm lt {};
#if defined(_WIN32)
    if (now == static_cast<std::time_t>(-1) || localtime_s(&lt, &now) != 0) {
        (void)std::snprintf(buf, len, "%s", "00:00:00");
        return;
    }
#else
    std::tm *p = std::localtime(&now);
    if (p == nullptr) {
        (void)std::snprintf(buf, len, "%s", "00:00:00");
        return;
    }
    lt = *p;
#endif
    (void)std::snprintf(buf, len, "%02d:%02d:%02d", lt.tm_hour, lt.tm_min, lt.tm_sec);
}

static void mesh_push_event_log(const char *domain, const char *event_type, JsonObjectConst body) {
    next_os_mesh_log_entry_t entry {};
    mesh_format_time_hms(entry.time, sizeof(entry.time));
    if (domain != nullptr) {
        (void)strncpy(entry.domain, domain, sizeof(entry.domain) - 1U);
        entry.domain[sizeof(entry.domain) - 1U] = '\0';
    }
    if (event_type != nullptr) {
        (void)strncpy(entry.event_type, event_type, sizeof(entry.event_type) - 1U);
    }
    char payload[72];
    if (!body.isNull() && body["summary"].is<const char *>()) {
        copy_str_field(payload, sizeof(payload), body["summary"]);
    } else if (!body.isNull() && body["title"].is<const char *>()) {
        copy_str_field(payload, sizeof(payload), body["title"]);
    } else {
        (void)std::snprintf(payload, sizeof(payload), "%s", event_type != nullptr ? event_type : "event");
    }
    (void)strncpy(entry.payload, payload, sizeof(entry.payload) - 1U);
    if (!body.isNull() && body["correlation_id"].is<const char *>()) {
        copy_str_field(entry.correlation_id, sizeof(entry.correlation_id), body["correlation_id"]);
    }
    if (event_type != nullptr && strcmp(event_type, "execution_step") == 0) {
        char wf_name[32] = "mesh";
        copy_json_key(wf_name, sizeof(wf_name), body, "workflow_name", wf_name);
        const int step = body["step"] | 0;
        const int total = body["total"] | 0;
        (void)std::snprintf(entry.payload, sizeof(entry.payload), "WF %s STEP %d/%d", wf_name, step, total);
    }
    next_os_mesh_state_push_log(&entry);
}

static void mesh_route_node_activity(const char *domain, const char *event_type, JsonObjectConst body) {
    if (domain != nullptr && strcmp(domain, "sensor") == 0) {
        next_os_mesh_state_touch_node_by_name("S2");
    }
    if (domain != nullptr && strcmp(domain, "vision") == 0) {
        next_os_mesh_state_touch_node_by_name("CAM");
    }
    if (strcmp(event_type, "dispatch_requested") == 0) {
        next_os_mesh_state_touch_node_by_name("DRN");
    }
    if (strcmp(event_type, "flight_completed") == 0) {
        next_os_mesh_topology_t topo = next_os_mesh_state_topology();
        topo.drn_dispatch_pulse = false;
        next_os_mesh_state_update_topology(&topo);
    }
    if (domain != nullptr && strcmp(domain, "actuator") == 0) {
        next_os_mesh_state_touch_node_by_name("SPR");
    }
    if (!body.isNull() && body["node"].is<const char *>()) {
        const char *node = body["node"].as<const char *>();
        if (node != nullptr) {
            next_os_mesh_state_touch_node_by_name(node);
        }
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

    if (topic != nullptr && strstr(topic, "workflow_executions") != nullptr) {
        if (doc["event_type"].is<const char *>()) {
            event_type = doc["event_type"].as<const char *>();
        }
        if (doc["domain"].is<const char *>()) {
            domain = doc["domain"].as<const char *>();
        }
    }

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
    } else if (strcmp(event_type, "motion_detected") == 0) {
        next_os_mesh_cctv_t cctv = next_os_mesh_state_cctv();
        cctv.live = true;
        if (body["pest_pct"].is<int>()) {
            cctv.pest_pct = static_cast<uint8_t>(body["pest_pct"].as<int>());
        }
        copy_json_key(cctv.title, sizeof(cctv.title), body, "title", cctv.title);
        copy_json_key(cctv.subtitle, sizeof(cctv.subtitle), body, "subtitle", cctv.subtitle);
        mesh_format_time_hms(cctv.timestamp, sizeof(cctv.timestamp));
        next_os_mesh_state_update_cctv(&cctv);
    } else if (strcmp(event_type, "image_captured") == 0) {
        next_os_mesh_state_randomize_ndvi();
    } else if (strcmp(event_type, "dispatch_requested") == 0) {
        next_os_mesh_topology_t topo = next_os_mesh_state_topology();
        topo.drn_dispatch_pulse = true;
        topo.dispatch_nodes = 1;
        topo.live_nodes = 5;
        topo.idle_nodes = 2;
        next_os_mesh_state_update_topology(&topo);
    } else if (strcmp(event_type, "execution_started") == 0) {
        next_os_mesh_workflow_t wf {};
        wf.active = true;
        wf.failed = false;
        wf.step = 0;
        wf.total = body["total"] | 3;
        copy_json_key(wf.workflow_name, sizeof(wf.workflow_name), body, "workflow_name", "irrigate");
        copy_json_key(wf.correlation_id, sizeof(wf.correlation_id), body, "correlation_id", "wf-1");
        next_os_mesh_state_update_workflow(&wf);
        next_os_mesh_state_touch_node_by_name("HUB");
    } else if (strcmp(event_type, "action_completed") == 0 || strcmp(event_type, "execution_step") == 0) {
        next_os_mesh_workflow_t wf = next_os_mesh_state_workflow();
        wf.active = true;
        wf.step = static_cast<uint8_t>(body["step"] | static_cast<int>(wf.step + 1U));
        wf.total = static_cast<uint8_t>(body["total"] | wf.total);
        copy_json_key(wf.workflow_name, sizeof(wf.workflow_name), body, "workflow_name", wf.workflow_name);
        next_os_mesh_state_update_workflow(&wf);
    } else if (strcmp(event_type, "execution_completed") == 0) {
        next_os_mesh_workflow_t wf = next_os_mesh_state_workflow();
        wf.active = false;
        wf.failed = false;
        wf.step = wf.total;
        next_os_mesh_state_update_workflow(&wf);
    } else if (strcmp(event_type, "execution_failed") == 0) {
        next_os_mesh_workflow_t wf = next_os_mesh_state_workflow();
        wf.active = false;
        wf.failed = true;
        next_os_mesh_state_update_workflow(&wf);
    }

    mesh_route_node_activity(domain, event_type, body);
    mesh_push_event_log(domain, event_type, body);
    next_os_mesh_ui_sync_refresh();
}
