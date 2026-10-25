#include "screens/apps/barometer_app.h"

#include "layout.h"
#include "screens/common.h"
#include "theme.h"

#include <cstdio>

void next_os_barometer_app_create(lv_obj_t *root) {
    next_os_apply_screen_style(root);
    next_os_common_create_header_label(root, "Barometer");

    lv_obj_t *pressure = lv_label_create(root);
    lv_label_set_text(pressure, "1013 hPa");
    lv_obj_set_style_text_font(pressure, &lv_font_montserrat_36, 0);
    lv_obj_align(pressure, LV_ALIGN_TOP_MID, 0, 48);

    lv_obj_t *alt = lv_label_create(root);
    lv_label_set_text(alt, "Alt ~1240 m");
    lv_obj_set_style_text_color(alt, NEXTOS_TEXT_MUTED, 0);
    lv_obj_align(alt, LV_ALIGN_TOP_MID, 0, 88);

    lv_obj_t *trend = lv_obj_create(root);
    lv_obj_set_size(trend, nextos_content_width() - 10, 90);
    lv_obj_align(trend, LV_ALIGN_BOTTOM_MID, 0, -24);
    lv_obj_set_style_bg_color(trend, NEXTOS_SURFACE_DIM, 0);
    lv_obj_set_flex_flow(trend, LV_FLEX_FLOW_ROW);
    lv_obj_set_flex_align(trend, LV_FLEX_ALIGN_SPACE_EVENLY, LV_FLEX_ALIGN_END, LV_FLEX_ALIGN_CENTER);
    const int32_t pts[] = {1015, 1014, 1013, 1012, 1013, 1013};
    for (uint8_t i = 0; i < 6U; i++) {
        lv_obj_t *bar = lv_obj_create(trend);
        lv_obj_set_width(bar, 8);
        lv_obj_set_height(bar, 20 + (pts[i] - 1010) * 8);
        lv_obj_set_style_bg_color(bar, NEXTOS_ACCENT_PRIMARY, 0);
    }
}
