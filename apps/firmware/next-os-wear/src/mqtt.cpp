#include "mqtt.h"

#include "config.h"
#include "mesh/handler.h"

#if defined(NEXT_OS_HARDWARE)

#include <PubSubClient.h>
#include <WiFi.h>

#include <cstring>

static WiFiClient s_wifi_client;
static PubSubClient s_mqtt(s_wifi_client);
static char s_topic_mesh_sub[96];
static char s_topic_ui_base[96];
static char s_topic_lwt[96];

static void mqtt_message_callback(char *topic, uint8_t *payload, unsigned int length) {
    next_os_mesh_handler_on_message(topic, payload, static_cast<size_t>(length));
}

static void mqtt_build_topics(void) {
    (void)snprintf(s_topic_mesh_sub, sizeof(s_topic_mesh_sub), "tenants/%s/mesh/events/#",
                   NEXT_OS_DEVICE_TENANT_ID);
    (void)snprintf(s_topic_ui_base, sizeof(s_topic_ui_base), "tenants/%s/devices/%s/ui/",
                   NEXT_OS_DEVICE_TENANT_ID, NEXT_OS_DEVICE_ID);
    (void)snprintf(s_topic_lwt, sizeof(s_topic_lwt), "%sdevice_offline", s_topic_ui_base);
}

void next_os_mqtt_init(void) {
    next_os_mesh_handler_init();
    s_mqtt.setServer(NEXT_OS_MQTT_BROKER_HOST, NEXT_OS_MQTT_BROKER_PORT);
    s_mqtt.setCallback(mqtt_message_callback);
    s_mqtt.setBufferSize(512);
    mqtt_build_topics();
}

bool next_os_mqtt_start(void) {
    if (!WiFi.isConnected()) {
        return false;
    }
    const char *client_id = NEXT_OS_DEVICE_ID;
    const char *user = NEXT_OS_MQTT_USERNAME;
    const char *pass = NEXT_OS_MQTT_PASSWORD;
    const char *lwt_payload = "{\"status\":\"offline\"}";

    bool ok = false;
    if (pass[0] != '\0') {
        ok = s_mqtt.connect(client_id, user, pass, s_topic_lwt, 1, true, lwt_payload);
    } else {
        ok = s_mqtt.connect(client_id, user, pass, s_topic_lwt, 1, true, lwt_payload);
    }
    if (!ok) {
        return false;
    }
    s_mqtt.subscribe(s_topic_mesh_sub, 1);
    return true;
}

void next_os_mqtt_loop(void) {
    if (s_mqtt.connected()) {
        s_mqtt.loop();
    }
}

bool next_os_mqtt_is_connected(void) {
    return s_mqtt.connected();
}

bool next_os_mqtt_publish_ui_event(const char *event_type, const char *payload_json) {
    if (!s_mqtt.connected() || event_type == nullptr) {
        return false;
    }
    char topic[128];
    (void)snprintf(topic, sizeof(topic), "%s%s", s_topic_ui_base, event_type);
    const char *body = payload_json != nullptr ? payload_json : "{}";
    return s_mqtt.publish(topic, body, true);
}

bool next_os_mqtt_publish_mesh_event(const char *domain, const char *event_type,
                                     const char *payload_json) {
    if (!s_mqtt.connected() || domain == nullptr || event_type == nullptr) {
        return false;
    }
    char topic[128];
    (void)snprintf(topic, sizeof(topic), "tenants/%s/mesh/events/%s/%s", NEXT_OS_DEVICE_TENANT_ID,
                   domain, event_type);
    const char *body = payload_json != nullptr ? payload_json : "{}";
    return s_mqtt.publish(topic, body, false);
}

#endif /* NEXT_OS_HARDWARE */
