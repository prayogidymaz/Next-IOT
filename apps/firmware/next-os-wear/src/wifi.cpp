#include "wifi.h"

#include "config.h"

#if defined(NEXT_OS_HARDWARE)

#include <Preferences.h>
#include <WiFi.h>

static Preferences s_wifi_prefs;
static bool s_connected = false;
static uint32_t s_last_reconnect_ms = 0;

static bool wifi_connect_with_timeout(const char *ssid, const char *password, uint32_t timeout_ms) {
    WiFi.mode(WIFI_STA);
    WiFi.begin(ssid, password);
    const uint32_t start = millis();
    while (WiFi.status() != WL_CONNECTED && (millis() - start) < timeout_ms) {
        delay(200);
    }
    s_connected = WiFi.status() == WL_CONNECTED;
    return s_connected;
}

bool next_os_wifi_has_stored_credentials(void) {
    s_wifi_prefs.begin("next_os_wifi", true);
    const bool has = s_wifi_prefs.isKey("ssid");
    s_wifi_prefs.end();
    return has;
}

bool next_os_wifi_load_and_connect(uint32_t timeout_ms) {
    s_wifi_prefs.begin("next_os_wifi", true);
    const String ssid = s_wifi_prefs.getString("ssid", "");
    const String pass = s_wifi_prefs.getString("pass", "");
    s_wifi_prefs.end();
    if (ssid.length() == 0) {
        return wifi_connect_with_timeout(NEXT_OS_WIFI_SSID, NEXT_OS_WIFI_PASSWORD, timeout_ms);
    }
    return wifi_connect_with_timeout(ssid.c_str(), pass.c_str(), timeout_ms);
}

bool next_os_wifi_begin(void) {
    return next_os_wifi_load_and_connect(30000U);
}

bool next_os_wifi_is_connected(void) {
    s_connected = WiFi.status() == WL_CONNECTED;
    return s_connected;
}

void next_os_wifi_loop(void) {
    if (WiFi.status() == WL_CONNECTED) {
        s_connected = true;
        return;
    }
    s_connected = false;
    const uint32_t now = millis();
    if (now - s_last_reconnect_ms > 10000U) {
        s_last_reconnect_ms = now;
        (void)next_os_wifi_load_and_connect(8000U);
    }
}

void next_os_wifi_disconnect(void) {
    WiFi.disconnect(true);
    s_connected = false;
}

int32_t next_os_wifi_rssi(void) {
    if (!next_os_wifi_is_connected()) {
        return 0;
    }
    return WiFi.RSSI();
}

#else

bool next_os_wifi_has_stored_credentials(void) {
    return true;
}

bool next_os_wifi_load_and_connect(uint32_t timeout_ms) {
    (void)timeout_ms;
    return true;
}

bool next_os_wifi_begin(void) {
    return true;
}

bool next_os_wifi_is_connected(void) {
    return true;
}

void next_os_wifi_loop(void) {}

void next_os_wifi_disconnect(void) {}

int32_t next_os_wifi_rssi(void) {
    return -55;
}

#endif
