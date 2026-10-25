#include "wifi.h"

#include "config.h"

#if defined(NEXT_OS_HARDWARE)
#include <WiFi.h>

static bool s_connected = false;

bool next_os_wifi_begin(void) {
    WiFi.mode(WIFI_STA);
    WiFi.begin(NEXT_OS_WIFI_SSID, NEXT_OS_WIFI_PASSWORD);
    const unsigned long start = millis();
    while (WiFi.status() != WL_CONNECTED && millis() - start < 15000UL) {
        delay(200);
    }
    s_connected = WiFi.status() == WL_CONNECTED;
    return s_connected;
}

bool next_os_wifi_is_connected(void) {
    return s_connected;
}

#else

bool next_os_wifi_begin(void) {
    return false;
}

bool next_os_wifi_is_connected(void) {
    return false;
}

#endif
