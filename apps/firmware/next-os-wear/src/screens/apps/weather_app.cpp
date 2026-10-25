#include "screens/apps/weather_app.h"

#include "mesh_state.h"
#include "layout.h"
#include "screens/common.h"
#include "theme.h"

#include <cstdio>

void next_os_weather_app_create(lv_obj_t *root) {
    next_os_apply_screen_style(root);
    next_os_common_create_header_label(root, "Weather");

    const next_os_mesh_sensor_t s = next_os_mesh_state_sensor();
    char main_line[32];
    (void)std::snprintf(main_line, sizeof(main_line), "%ld°C  %ld%% RH", static_cast<long>(s.temp_c),
                        static_cast<long>(s.humidity));
    lv_obj_t *now = lv_label_create(root);
    lv_label_set_text(now, main_line);
    lv_obj_set_style_text_font(now, &lv_font_montserrat_24, 0);
    lv_obj_align(now, LV_ALIGN_TOP_MID, 0, 48);

    lv_obj_t *cond = lv_label_create(root);
    lv_label_set_text(cond, LV_SYMBOL_OK " Partly cloudy");
    lv_obj_align(cond, LV_ALIGN_TOP_MID, 0, 78);

    lv_obj_t *rain = lv_label_create(root);
    lv_label_set_text(rain, "Rain 62% next 4h");
    lv_obj_set_style_text_color(rain, NEXTOS_ACCENT_SECONDARY, 0);
    lv_obj_align(rain, LV_ALIGN_TOP_MID, 0, 98);

    lv_obj_t *scroll = lv_obj_create(root);
    lv_obj_set_size(scroll, nextos_content_width(), 80);
    lv_obj_align(scroll, LV_ALIGN_BOTTOM_MID, 0, -20);
    lv_obj_set_flex_flow(scroll, LV_FLEX_FLOW_ROW);
    lv_obj_set_style_pad_column(scroll, 8, 0);
    lv_obj_set_scrollbar_mode(scroll, LV_SCROLLBAR_MODE_OFF);
    lv_obj_set_scroll_dir(scroll, LV_DIR_HOR);

    const char *cells[] = {"+4h 27°", "+8h 26°", "+12h 25°", "+16h 24°", "+20h 23°", "+24h 22°"};
    for (size_t i = 0; i < sizeof(cells) / sizeof(cells[0]); i++) {
        lv_obj_t *cell = lv_obj_create(scroll);
        lv_obj_set_size(cell, 56, 64);
        lv_obj_set_style_bg_color(cell, NEXTOS_SURFACE, 0);
        lv_obj_t *lbl = lv_label_create(cell);
        lv_label_set_text(lbl, cells[i]);
        lv_obj_center(lbl);
    }
}
