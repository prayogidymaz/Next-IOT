#include "haptic.h"

#include "layout.h"
#include "screens/screen_manager.h"
#include "theme.h"
#include "user_prefs.h"

#include <lvgl.h>

static lv_obj_t *s_flash = nullptr;
static lv_timer_t *s_flash_timer = nullptr;

static void haptic_flash_end(lv_timer_t *timer) {
    (void)timer;
    if (s_flash != nullptr) {
        lv_obj_delete(s_flash);
        s_flash = nullptr;
    }
    s_flash_timer = nullptr;
}

void nextos_haptic_init(void) {}

void nextos_haptic_pulse(nextos_haptic_intensity_t intensity) {
    if (!next_os_user_prefs_haptic_enabled()) {
        return;
    }

#if defined(NEXT_OS_HARDWARE)
    (void)intensity;
    /* TODO: ledcWrite vibration motor pin on T-Watch S3 */
#else
    lv_obj_t *content = next_os_screen_manager_get_content_root();
    if (content == nullptr) {
        return;
    }
    if (s_flash != nullptr) {
        lv_obj_delete(s_flash);
        s_flash = nullptr;
    }
    s_flash = lv_obj_create(content);
    lv_obj_set_size(s_flash, NEXTOS_W, NEXTOS_H);
    lv_obj_center(s_flash);
    lv_obj_set_style_bg_color(s_flash, NEXTOS_TEXT_PRIMARY, 0);
    lv_obj_set_style_bg_opa(s_flash, intensity == NEXTOS_HAPTIC_STRONG ? LV_OPA_30 : LV_OPA_20, 0);
    lv_obj_set_style_border_width(s_flash, 0, 0);
    lv_obj_set_clickable(s_flash, false);
    lv_obj_move_foreground(s_flash);

    uint32_t ms = 100;
    if (intensity == NEXTOS_HAPTIC_MEDIUM) {
        ms = 200;
    } else if (intensity == NEXTOS_HAPTIC_STRONG) {
        ms = 500;
    }
    if (s_flash_timer != nullptr) {
        lv_timer_delete(s_flash_timer);
    }
    s_flash_timer = lv_timer_create(haptic_flash_end, ms, nullptr);
    lv_timer_set_repeat_count(s_flash_timer, 1);
#endif
}
