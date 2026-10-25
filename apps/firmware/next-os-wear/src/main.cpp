#include "app.h"
#include "config.h"
#include "display.h"
#include "touch.h"
#include "wifi.h"

#include "screens/screen_manager.h"

#include <Arduino.h>

void setup() {
    Serial.begin(115200);
    delay(100);
    Serial.println("Next-OS Wear v1 boot");

    if (!next_os_display_init()) {
        Serial.println("Display init gagal");
        return;
    }
    next_os_touch_init();
    next_os_app_init();
    next_os_screen_manager_tune_pointer_gesture();

    if (next_os_wifi_begin()) {
        Serial.println("WiFi terhubung");
    } else {
        Serial.println("WiFi offline (lanjut UI lokal)");
    }
}

void loop() {
    next_os_display_lvgl_handler();
    static uint32_t last_second = 0;
    const uint32_t now_ms = millis();
    if (now_ms - last_second >= 1000U) {
        last_second = now_ms;
        next_os_app_tick();
    }
    delay(5);
}
