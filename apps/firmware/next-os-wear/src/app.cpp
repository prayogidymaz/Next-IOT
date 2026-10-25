#include "app.h"

#include "audio.h"
#include "haptic.h"
#include "mqtt.h"
#include "runtime_theme.h"
#include "screens/boot.h"
#include "screens/screen_manager.h"
#include "user_prefs.h"

static lv_obj_t *s_boot_screen = nullptr;

static void on_boot_finished(void) {
    next_os_mqtt_init();
    (void)next_os_mqtt_start();
    next_os_screen_manager_enter_from_boot(s_boot_screen);
    s_boot_screen = nullptr;
}

void next_os_app_init(void) {
    next_os_user_prefs_init();
    next_os_runtime_theme_init();
    nextos_haptic_init();
    nextos_audio_init();
    s_boot_screen = lv_obj_create(nullptr);
    lv_screen_load(s_boot_screen);
    next_os_boot_screen_create(s_boot_screen, on_boot_finished);
}

void next_os_app_tick(void) {
    next_os_mqtt_loop();
}
