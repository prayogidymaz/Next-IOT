#include "screens/apps/compass_app.h"

#include "layout.h"
#include "screens/common.h"
#include "theme.h"

#include <cstdio>

static lv_obj_t *s_heading_label = nullptr;
static lv_obj_t *s_needle = nullptr;
static int32_t s_heading = 0;
static lv_timer_t *s_spin = nullptr;

static void compass_tick(lv_timer_t *timer) {
    (void)timer;
    s_heading = (s_heading + 2) % 360;
    if (s_needle != nullptr) {
        lv_obj_set_style_transform_angle(s_needle, static_cast<int32_t>(s_heading * 10), 0);
    }
    if (s_heading_label != nullptr) {
        char buf[16];
        (void)std::snprintf(buf, sizeof(buf), "%ld°", static_cast<long>(s_heading));
        lv_label_set_text(s_heading_label, buf);
    }
}

void next_os_compass_app_create(lv_obj_t *root) {
    next_os_apply_screen_style(root);
    next_os_common_create_header_label(root, "Compass");

    lv_obj_t *dial = next_os_common_create_round_container(root, 140);
    lv_obj_align(dial, LV_ALIGN_CENTER, 0, 0);
    lv_label_set_text(lv_label_create(dial), "N");
    lv_obj_align(lv_obj_get_child(dial, 0), LV_ALIGN_TOP_MID, 0, 6);

    s_needle = lv_label_create(dial);
    lv_label_set_text(s_needle, LV_SYMBOL_UP);
    lv_obj_set_style_text_color(s_needle, NEXTOS_CRITICAL, 0);
    lv_obj_set_style_text_font(s_needle, &lv_font_montserrat_24, 0);
    lv_obj_center(s_needle);

    s_heading_label = lv_label_create(root);
    lv_label_set_text(s_heading_label, "0°");
    lv_obj_set_style_text_font(s_heading_label, &lv_font_montserrat_24, 0);
    lv_obj_align(s_heading_label, LV_ALIGN_BOTTOM_MID, 0, -24);

    s_spin = lv_timer_create(compass_tick, 200, nullptr);
}
