#include "screens/sensor_monitor.h"

#include "mesh_state.h"
#include "screens/common.h"
#include "theme.h"

#include <cstdio>

static lv_obj_t *s_moisture_label = nullptr;
static lv_obj_t *s_ph_value = nullptr;
static lv_obj_t *s_temp_value = nullptr;
static lv_obj_t *s_hum_value = nullptr;

static lv_obj_t *sensor_create_metric_tile(lv_obj_t *parent, const char *value, const char *unit,
                                         lv_obj_t **out_val) {
    lv_obj_t *col = lv_obj_create(parent);
    lv_obj_set_size(col, 58, 36);
    lv_obj_set_style_bg_opa(col, LV_OPA_TRANSP, 0);
    lv_obj_set_style_border_width(col, 0, 0);
    lv_obj_set_style_pad_all(col, 0, 0);
    next_os_common_disable_scroll(col);

    lv_obj_t *val = lv_label_create(col);
    lv_label_set_text(val, value);
    lv_obj_set_style_text_font(val, &lv_font_montserrat_12, 0);
    lv_obj_set_style_text_color(val, next_os_color_dark(), 0);
    lv_obj_align(val, LV_ALIGN_TOP_MID, 0, 0);

    lv_obj_t *lbl = lv_label_create(col);
    lv_label_set_text(lbl, unit);
    lv_obj_set_style_text_font(lbl, &lv_font_montserrat_12, 0);
    lv_obj_set_style_text_color(lbl, next_os_color_muted(), 0);
    lv_obj_align(lbl, LV_ALIGN_BOTTOM_MID, 0, 0);

    if (out_val != nullptr) {
        *out_val = val;
    }
    return col;
}

void next_os_sensor_monitor_refresh_from_mesh(void) {
    const next_os_mesh_sensor_t s = next_os_mesh_state_sensor();
    char buf[12];
    if (s_moisture_label != nullptr && lv_obj_is_in_widget_tree(s_moisture_label)) {
        (void)std::snprintf(buf, sizeof(buf), "%ld", static_cast<long>(s.moisture));
        lv_label_set_text(s_moisture_label, buf);
    }
    if (s_ph_value != nullptr && lv_obj_is_in_widget_tree(s_ph_value)) {
        (void)std::snprintf(buf, sizeof(buf), "%.1f", static_cast<double>(s.ph));
        lv_label_set_text(s_ph_value, buf);
    }
    if (s_temp_value != nullptr && lv_obj_is_in_widget_tree(s_temp_value)) {
        (void)std::snprintf(buf, sizeof(buf), "%ldC", static_cast<long>(s.temp_c));
        lv_label_set_text(s_temp_value, buf);
    }
    if (s_hum_value != nullptr && lv_obj_is_in_widget_tree(s_hum_value)) {
        (void)std::snprintf(buf, sizeof(buf), "%ld%%", static_cast<long>(s.humidity));
        lv_label_set_text(s_hum_value, buf);
    }
}

void next_os_sensor_monitor_create(lv_obj_t *root) {
    next_os_apply_screen_style(root);

    lv_obj_t *header = next_os_common_create_header_label(root, "PLOT A • KOPI");
    lv_obj_set_style_text_align(header, LV_TEXT_ALIGN_CENTER, 0);

    lv_obj_t *icon = lv_label_create(root);
    lv_label_set_text(icon, LV_SYMBOL_HOME);
    lv_obj_set_style_text_color(icon, next_os_color_olive(), 0);
    lv_obj_align(icon, LV_ALIGN_TOP_MID, 0, 28);

    const next_os_mesh_sensor_t reading = next_os_mesh_state_sensor();
    s_moisture_label = lv_label_create(root);
    char moist_buf[8];
    (void)std::snprintf(moist_buf, sizeof(moist_buf), "%ld", static_cast<long>(reading.moisture));
    lv_label_set_text(s_moisture_label, moist_buf);
    lv_obj_set_style_text_font(s_moisture_label, &lv_font_montserrat_48, 0);
    lv_obj_set_style_text_color(s_moisture_label, next_os_color_dark(), 0);
    lv_obj_align(s_moisture_label, LV_ALIGN_CENTER, -12, -8);

    lv_obj_t *pct = lv_label_create(root);
    lv_label_set_text(pct, "%");
    lv_obj_set_style_text_font(pct, &lv_font_montserrat_20, 0);
    lv_obj_set_style_text_color(pct, next_os_color_muted(), 0);
    lv_obj_align_to(pct, s_moisture_label, LV_ALIGN_OUT_RIGHT_BOTTOM, 4, -6);

    lv_obj_t *moist_lbl = lv_label_create(root);
    lv_label_set_text(moist_lbl, "MOISTURE");
    lv_obj_set_style_text_font(moist_lbl, &lv_font_montserrat_12, 0);
    lv_obj_set_style_text_color(moist_lbl, next_os_color_olive(), 0);
    lv_obj_align(moist_lbl, LV_ALIGN_CENTER, 0, 36);

    lv_obj_t *tiles = lv_obj_create(root);
    lv_obj_set_size(tiles, 220, 40);
    lv_obj_align(tiles, LV_ALIGN_BOTTOM_MID, 0, -36);
    lv_obj_set_style_bg_opa(tiles, LV_OPA_TRANSP, 0);
    lv_obj_set_style_border_width(tiles, 0, 0);
    lv_obj_set_flex_flow(tiles, LV_FLEX_FLOW_ROW);
    lv_obj_set_flex_align(tiles, LV_FLEX_ALIGN_SPACE_EVENLY, LV_FLEX_ALIGN_CENTER, LV_FLEX_ALIGN_CENTER);
    next_os_common_disable_scroll(tiles);

    char ph_buf[8];
    char temp_buf[8];
    char hum_buf[8];
    (void)std::snprintf(ph_buf, sizeof(ph_buf), "%.1f", static_cast<double>(reading.ph));
    (void)std::snprintf(temp_buf, sizeof(temp_buf), "%ldC", static_cast<long>(reading.temp_c));
    (void)std::snprintf(hum_buf, sizeof(hum_buf), "%ld%%", static_cast<long>(reading.humidity));

    sensor_create_metric_tile(tiles, ph_buf, "pH", &s_ph_value);
    next_os_common_create_v_separator(tiles);
    sensor_create_metric_tile(tiles, temp_buf, "TEMP", &s_temp_value);
    next_os_common_create_v_separator(tiles);
    sensor_create_metric_tile(tiles, hum_buf, "HUM", &s_hum_value);

    next_os_common_create_pagination_dots(root, 3, 0);
    next_os_common_create_nav_buttons(root);
}
