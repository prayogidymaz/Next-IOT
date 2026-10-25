#include "screens/sensor_monitor.h"

#include "screens/common.h"
#include "theme.h"

#include <cstdio>

/* Mock sensor — Week 7–10 MQTT */
static constexpr int k_mock_moisture = 68;
static constexpr float k_mock_ph = 6.4F;
static constexpr int k_mock_temp = 24;
static constexpr int k_mock_humidity = 72;

static lv_obj_t *sensor_create_metric_tile(lv_obj_t *parent, const char *value, const char *unit) {
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

    return col;
}

void next_os_sensor_monitor_create(lv_obj_t *root) {
    next_os_apply_screen_style(root);

    lv_obj_t *header = next_os_common_create_header_label(root, "PLOT A • KOPI");
    lv_obj_set_style_text_align(header, LV_TEXT_ALIGN_CENTER, 0);

    lv_obj_t *icon = lv_label_create(root);
    lv_label_set_text(icon, LV_SYMBOL_HOME);
    lv_obj_set_style_text_color(icon, next_os_color_olive(), 0);
    lv_obj_align(icon, LV_ALIGN_TOP_MID, 0, 28);

    lv_obj_t *big = lv_label_create(root);
    char moist_buf[8];
    (void)std::snprintf(moist_buf, sizeof(moist_buf), "%d", k_mock_moisture);
    lv_label_set_text(big, moist_buf);
    lv_obj_set_style_text_font(big, &lv_font_montserrat_48, 0);
    lv_obj_set_style_text_color(big, next_os_color_dark(), 0);
    lv_obj_align(big, LV_ALIGN_CENTER, -12, -8);

    lv_obj_t *pct = lv_label_create(root);
    lv_label_set_text(pct, "%");
    lv_obj_set_style_text_font(pct, &lv_font_montserrat_20, 0);
    lv_obj_set_style_text_color(pct, next_os_color_muted(), 0);
    lv_obj_align_to(pct, big, LV_ALIGN_OUT_RIGHT_BOTTOM, 4, -6);

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
    (void)std::snprintf(ph_buf, sizeof(ph_buf), "%.1f", static_cast<double>(k_mock_ph));
    (void)std::snprintf(temp_buf, sizeof(temp_buf), "%dC", k_mock_temp);
    (void)std::snprintf(hum_buf, sizeof(hum_buf), "%d%%", k_mock_humidity);

    sensor_create_metric_tile(tiles, ph_buf, "pH");
    next_os_common_create_v_separator(tiles);
    sensor_create_metric_tile(tiles, temp_buf, "TEMP");
    next_os_common_create_v_separator(tiles);
    sensor_create_metric_tile(tiles, hum_buf, "HUM");

    next_os_common_create_pagination_dots(root, 3, 0);
}
