/**
 * Event antar layar / modul aplikasi
 */
#ifndef NEXT_OS_EVENTS_H
#define NEXT_OS_EVENTS_H

#include <stdint.h>

typedef enum {
    NEXT_OS_EVT_NONE = 0,
    NEXT_OS_EVT_BOOT_FINISHED,
    NEXT_OS_EVT_TICK_1S,
    NEXT_OS_EVT_WIFI_CONNECTED,
    NEXT_OS_EVT_WIFI_DISCONNECTED,
    NEXT_OS_EVT_MQTT_CONNECTED,
    NEXT_OS_EVT_MQTT_MESSAGE,
    NEXT_OS_EVT_TOUCH_TAP,
    NEXT_OS_EVT_ALERT_NEW,
} next_os_event_id_t;

typedef struct {
    next_os_event_id_t id;
    int32_t value;
    void *payload;
} next_os_event_t;

#endif /* NEXT_OS_EVENTS_H */
