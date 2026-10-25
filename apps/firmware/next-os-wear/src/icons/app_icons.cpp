#include "icons/app_icons.h"

#include <lvgl.h>

static const next_os_app_icon_entry_t s_icons[] = {
    {NEXT_OS_SCREEN_FARMING_HUB, LV_SYMBOL_HOME, "Farming"},
    {NEXT_OS_SCREEN_MESH_HUB, LV_SYMBOL_LOOP, "Mesh Ops"},
    {NEXT_OS_SCREEN_ALERT_CENTER, LV_SYMBOL_BELL, "Alerts"},
    {NEXT_OS_SCREEN_APP_TIMER, LV_SYMBOL_REFRESH, "Timer"},
    {NEXT_OS_SCREEN_APP_WEATHER, LV_SYMBOL_WIFI, "Weather"},
    {NEXT_OS_SCREEN_APP_COMPASS, LV_SYMBOL_GPS, "Compass"},
    {NEXT_OS_SCREEN_APP_FLASHLIGHT, LV_SYMBOL_CHARGE, "Light"},
    {NEXT_OS_SCREEN_APP_HEALTH, LV_SYMBOL_OK, "Health"},
    {NEXT_OS_SCREEN_APP_BAROMETER, LV_SYMBOL_EJECT, "Baro"},
    {NEXT_OS_SCREEN_SETTINGS, LV_SYMBOL_SETTINGS, "Settings"},
    {NEXT_OS_SCREEN_ABOUT, LV_SYMBOL_WARNING, "About"},
    {NEXT_OS_SCREEN_QR_PAIR, LV_SYMBOL_CALL, "Pair"},
};

uint8_t next_os_app_icon_count(void) {
    return static_cast<uint8_t>(sizeof(s_icons) / sizeof(s_icons[0]));
}

const next_os_app_icon_entry_t *next_os_app_icon_at(uint8_t index) {
    if (index >= next_os_app_icon_count()) {
        return nullptr;
    }
    return &s_icons[index];
}
