#include "app.h"

#include "screens/boot.h"
#include "screens/screen_manager.h"

static lv_obj_t *s_boot_screen = nullptr;

static void on_boot_finished(void) {
    next_os_screen_manager_enter_from_boot(s_boot_screen);
    s_boot_screen = nullptr;
}

void next_os_app_init(void) {
    s_boot_screen = lv_obj_create(nullptr);
    lv_screen_load(s_boot_screen);
    next_os_boot_screen_create(s_boot_screen, on_boot_finished);
}

void next_os_app_tick(void) {
    /* Tick per layar lewat lv_timer internal (watch face, dll.) */
}
