#include "app.h"

#include "screens/boot.h"
#include "screens/hello_world.h"

static lv_obj_t *s_boot_screen = nullptr;
static bool s_on_hello = false;
static lv_timer_t *s_second_timer = nullptr;

static void show_hello_async(void *user_data) {
    (void)user_data;

    if (s_boot_screen != nullptr) {
        lv_anim_delete(s_boot_screen, nullptr);
    }

    lv_obj_t *hello = lv_obj_create(nullptr);
    next_os_hello_world_screen_create(hello);
    lv_screen_load_anim(hello, LV_SCREEN_LOAD_ANIM_FADE_IN, 300, 0, true);
    s_boot_screen = nullptr;
    s_on_hello = true;
}

static void show_hello(void) {
    lv_async_call(show_hello_async, nullptr);
}

static void app_second_timer_cb(lv_timer_t *timer) {
    (void)timer;
    if (lv_display_get_default() == nullptr || !s_on_hello) {
        return;
    }
    next_os_app_tick();
}

void next_os_app_init(void) {
    s_boot_screen = lv_obj_create(nullptr);
    lv_screen_load(s_boot_screen);
    next_os_boot_screen_create(s_boot_screen, show_hello);

    s_second_timer = lv_timer_create(app_second_timer_cb, 1000, nullptr);
}

void next_os_app_tick(void) {
    static uint8_t minute = 15;
    static uint8_t hour = 10;

    minute++;
    if (minute >= 60) {
        minute = 0;
        hour = static_cast<uint8_t>((hour + 1) % 24);
    }
    next_os_hello_world_update_clock(hour, minute);
}
