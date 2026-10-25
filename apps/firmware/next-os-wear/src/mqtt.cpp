#include "mqtt.h"

#include "config.h"

/**
 * Stub MQTT — implementasi penuh Week 7-10 (mesh topic + JSON payload).
 */
#if defined(NEXT_OS_HARDWARE)
#include <PubSubClient.h>
#include <WiFi.h>

static WiFiClient s_wifi_client;
static PubSubClient s_mqtt(s_wifi_client);

bool next_os_mqtt_connect(void) {
    s_mqtt.setServer(NEXT_OS_MQTT_BROKER, NEXT_OS_MQTT_PORT);
    if (NEXT_OS_MQTT_USERNAME[0] != '\0') {
        return s_mqtt.connect(NEXT_OS_DEVICE_NAME, NEXT_OS_MQTT_USERNAME, NEXT_OS_MQTT_PASSWORD);
    }
    return s_mqtt.connect(NEXT_OS_DEVICE_NAME);
}

void next_os_mqtt_loop(void) {
    if (s_mqtt.connected()) {
        s_mqtt.loop();
    }
}

#else

bool next_os_mqtt_connect(void) {
    return false;
}

void next_os_mqtt_loop(void) {}

#endif
