#include "app.h"

#include "screens/boot.h"
#include "screens/hello_world.h"

static lv_obj_t *s_root = nullptr;
static bool s_on_hello = false;

static void show_hello(void) {
    if (s_root == nullptr) {
        return;
    }
    lv_obj_clean(s_root);
    next_os_hello_world_screen_create(s_root);
    s_on_hello = true;
}

void next_os_app_init(void) {
    s_root = lv_screen_active();
    next_os_boot_screen_create(s_root, show_hello);
}

void next_os_app_tick(void) {
    static uint8_t minute = 15;
    static uint8_t hour = 10;
    if (!s_on_hello) {
        return;
    }
    minute++;
    if (minute >= 60) {
        minute = 0;
        hour = static_cast<uint8_t>((hour + 1) % 24);
    }
    next_os_hello_world_update_clock(hour, minute);
}
