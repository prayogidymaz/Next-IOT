#include "app.h"

#include "screens/boot.h"
#include "screens/hello_world.h"

static lv_obj_t *s_boot_screen = nullptr;
static bool s_on_hello = false;

static void show_hello_async(void *user_data) {
    (void)user_data;

    lv_obj_t *hello = lv_obj_create(nullptr);
    next_os_hello_world_screen_create(hello);
    lv_screen_load_anim(hello, LV_SCREEN_LOAD_ANIM_FADE_IN, 300, 0, true);
    s_boot_screen = nullptr;
    s_on_hello = true;
}

static void show_hello(void) {
    /* Jangan hapus layar boot dari dalam callback anim — defer ke async (LVGL 9.6) */
    lv_async_call(show_hello_async, nullptr);
}

void next_os_app_init(void) {
    s_boot_screen = lv_obj_create(nullptr);
    lv_screen_load(s_boot_screen);
    next_os_boot_screen_create(s_boot_screen, show_hello);
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
