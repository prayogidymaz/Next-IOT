#include "screens/sensor_radial.h"

#include "mesh_state.h"
#include "screens/common.h"
#include "theme.h"

#include <cstdio>

static lv_obj_t *s_center_pct = nullptr;
static lv_obj_t *s_arc_outer = nullptr;
static lv_obj_t *s_arc_mid = nullptr;
static lv_obj_t *s_arc_inner = nullptr;

static int32_t sensor_pct_to_angle(int32_t pct, int32_t span_deg) {
    if (pct < 0) {
        pct = 0;
    }
    if (pct > 100) {
        pct = 100;
    }
    return (pct * span_deg) / 100;
}

static void sensor_set_arc(lv_obj_t *arc, int32_t span_deg, int32_t value_pct) {
    const int32_t end = sensor_pct_to_angle(value_pct, span_deg);
    lv_arc_set_bg_angles(arc, 0, span_deg);
    lv_arc_set_angles(arc, 0, end);
}

static void radial_on_delete(lv_event_t *event) {
    if (lv_event_get_code(event) != LV_EVENT_DELETE) {
        return;
    }
    s_center_pct = nullptr;
    s_arc_outer = nullptr;
    s_arc_mid = nullptr;
    s_arc_inner = nullptr;
}

void next_os_sensor_radial_refresh_from_mesh(void) {
    const next_os_mesh_sensor_t s = next_os_mesh_state_sensor();
    if (s_center_pct != nullptr && lv_obj_is_in_widget_tree(s_center_pct)) {
        char buf[8];
        (void)std::snprintf(buf, sizeof(buf), "%ld%%", static_cast<long>(s.moisture));
        lv_label_set_text(s_center_pct, buf);
    }
    if (s_arc_outer != nullptr && lv_obj_is_in_widget_tree(s_arc_outer)) {
        sensor_set_arc(s_arc_outer, 320, s.moisture);
    }
    if (s_arc_mid != nullptr && lv_obj_is_in_widget_tree(s_arc_mid)) {
        const int32_t ph_pct = static_cast<int32_t>((s.ph / 14.0F) * 100.0F);
        sensor_set_arc(s_arc_mid, 240, ph_pct);
    }
    if (s_arc_inner != nullptr && lv_obj_is_in_widget_tree(s_arc_inner)) {
        const int32_t temp_pct = static_cast<int32_t>((static_cast<float>(s.temp_c) / 50.0F) * 100.0F);
        sensor_set_arc(s_arc_inner, 200, temp_pct);
    }
}

static lv_obj_t *sensor_create_arc_layer(lv_obj_t *parent, int32_t size, lv_color_t color) {
    lv_obj_t *arc = lv_arc_create(parent);
    lv_obj_set_size(arc, size, size);
    lv_obj_center(arc);
    lv_arc_set_rotation(arc, 200);
    lv_obj_remove_style(arc, nullptr, LV_PART_KNOB);
    lv_obj_set_style_arc_color(arc, color, LV_PART_INDICATOR);
    lv_obj_set_style_arc_color(arc, next_os_color_dark_separator(), LV_PART_MAIN);
    lv_obj_set_style_arc_width(arc, 6, LV_PART_MAIN);
    lv_obj_set_style_arc_width(arc, 6, LV_PART_INDICATOR);
    lv_obj_remove_flag(arc, LV_OBJ_FLAG_CLICKABLE); /* LVGL deprecates; arc non-interactive */
    return arc;
}

void next_os_sensor_radial_create(lv_obj_t *root) {
    next_os_apply_dark_tactical_style(root);
    lv_obj_add_event_cb(root, radial_on_delete, LV_EVENT_DELETE, nullptr);

    const next_os_mesh_sensor_t reading = next_os_mesh_state_sensor();

    lv_obj_t *header = next_os_common_create_inset_header_row(root, 22);
    lv_obj_t *ht = lv_label_create(header);
    lv_label_set_text(ht, "PLOT A • KOPI");
    lv_obj_set_style_text_color(ht, next_os_color_clay(), 0);
    lv_obj_align(ht, LV_ALIGN_LEFT_MID, 0, 0);
    lv_obj_t *tm = lv_label_create(header);
    lv_label_set_text(tm, "07:42");
    lv_obj_set_style_text_color(tm, next_os_color_muted(), 0);
    lv_obj_align(tm, LV_ALIGN_RIGHT_MID, 0, 0);

    lv_obj_t *rings = lv_obj_create(root);
    lv_obj_set_size(rings, 180, 180);
    lv_obj_align(rings, LV_ALIGN_CENTER, 0, -8);
    lv_obj_set_style_bg_opa(rings, LV_OPA_TRANSP, 0);
    lv_obj_set_style_border_width(rings, 0, 0);
    next_os_common_disable_scroll(rings);

    s_arc_outer = sensor_create_arc_layer(rings, 176, next_os_color_olive());
    s_arc_mid = sensor_create_arc_layer(rings, 140, next_os_color_amber());
    s_arc_inner = sensor_create_arc_layer(rings, 104, next_os_color_clay());

    s_center_pct = lv_label_create(rings);
    char moist[8];
    (void)std::snprintf(moist, sizeof(moist), "%ld%%", static_cast<long>(reading.moisture));
    lv_label_set_text(s_center_pct, moist);
    lv_obj_set_style_text_font(s_center_pct, &lv_font_montserrat_24, 0);
    lv_obj_set_style_text_color(s_center_pct, next_os_color_cream(), 0);
    lv_obj_align(s_center_pct, LV_ALIGN_CENTER, 0, -6);

    lv_obj_t *sub = lv_label_create(rings);
    lv_label_set_text(sub, "MOISTURE");
    lv_obj_set_style_text_font(sub, &lv_font_montserrat_12, 0);
    lv_obj_set_style_text_color(sub, next_os_color_muted(), 0);
    lv_obj_align(sub, LV_ALIGN_CENTER, 0, 18);

    lv_obj_t *tiles = lv_obj_create(root);
    lv_obj_set_size(tiles, 210, 32);
    lv_obj_align(tiles, LV_ALIGN_BOTTOM_MID, 0, -14);
    lv_obj_set_style_bg_opa(tiles, LV_OPA_TRANSP, 0);
    lv_obj_set_style_border_width(tiles, 0, 0);
    lv_obj_set_flex_flow(tiles, LV_FLEX_FLOW_ROW);
    lv_obj_set_flex_align(tiles, LV_FLEX_ALIGN_SPACE_EVENLY, LV_FLEX_ALIGN_CENTER, LV_FLEX_ALIGN_CENTER);
    next_os_common_disable_scroll(tiles);

    char t1[16];
    char t2[16];
    char t3[16];
    (void)std::snprintf(t1, sizeof(t1), "SOIL %ld%%", static_cast<long>(reading.moisture));
    (void)std::snprintf(t2, sizeof(t2), "pH %.1f", static_cast<double>(reading.ph));
    (void)std::snprintf(t3, sizeof(t3), "TEMP %ld°", static_cast<long>(reading.temp_c));

    const struct {
        const char *txt;
        lv_color_t dot;
    } tile_data[3] = {{t1, next_os_color_live_green()},
                      {t2, next_os_color_amber()},
                      {t3, next_os_color_clay()}};
    for (uint8_t i = 0; i < 3; i++) {
        lv_obj_t *col = lv_obj_create(tiles);
        lv_obj_set_size(col, 64, LV_SIZE_CONTENT);
        lv_obj_set_style_bg_opa(col, LV_OPA_TRANSP, 0);
        lv_obj_set_style_border_width(col, 0, 0);
        lv_obj_t *d = lv_obj_create(col);
        lv_obj_set_size(d, 6, 6);
        lv_obj_set_style_radius(d, LV_RADIUS_CIRCLE, 0);
        lv_obj_set_style_bg_color(d, tile_data[i].dot, 0);
        lv_obj_align(d, LV_ALIGN_TOP_MID, 0, 0);
        lv_obj_t *l = lv_label_create(col);
        lv_label_set_text(l, tile_data[i].txt);
        lv_obj_set_style_text_font(l, &lv_font_montserrat_12, 0);
        lv_obj_set_style_text_color(l, next_os_color_cream(), 0);
        lv_obj_align(l, LV_ALIGN_TOP_MID, 0, 10);
    }

    next_os_sensor_radial_refresh_from_mesh();
}
