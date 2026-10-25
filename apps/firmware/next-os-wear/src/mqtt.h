#ifndef NEXT_OS_MQTT_H
#define NEXT_OS_MQTT_H

#include <stddef.h>
#include <stdint.h>

void next_os_mqtt_init(void);
bool next_os_mqtt_start(void);
void next_os_mqtt_loop(void);
bool next_os_mqtt_is_connected(void);

bool next_os_mqtt_publish_ui_event(const char *event_type, const char *payload_json);
bool next_os_mqtt_publish_mesh_event(const char *domain, const char *event_type, const char *payload_json);

#endif /* NEXT_OS_MQTT_H */
