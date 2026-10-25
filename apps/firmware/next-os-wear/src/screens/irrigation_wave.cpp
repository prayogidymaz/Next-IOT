#include "screens/irrigation_wave.h"

#include "mesh_state.h"
#include "screens/common.h"
#include "theme.h"

#include <cstdio>

static lv_obj_t *s_countdown = nullptr;
static lv_obj_t *s_flow_rate = nullptr;
static lv_obj_t *s_used = nullptr;

static void wave_on_delete(lv_event_t *event) {
    if (lv_event_get_code(event) != LV_EVENT_DELETE) {
        return;
    }
    s_countdown = nullptr;
    s_flow_rate = nullptr;
    s_used = nullptr;
}

void next_os_irrigation_wave_refresh_from_mesh(void) {
    const next_os_mesh_irrig_t ir = next_os_mesh_state_irrig();
    if (s_countdown != nullptr && lv_obj_is_in_widget_tree(s_countdown)) {
        lv_label_set_text(s_countdown, ir.countdown);
    }
    if (s_flow_rate != nullptr && lv_obj_is_in_widget_tree(s_flow_rate)) {
        char buf[32];
        (void)std::snprintf(buf, sizeof(buf), "FLOW RATE %s", ir.flow_label);
        lv_label_set_text(s_flow_rate, buf);
    }
}

void next_os_irrigation_wave_create(lv_obj_t *root) {
    next_os_apply_dark_tactical_style(root);
    lv_obj_add_event_cb(root, wave_on_delete, LV_EVENT_DELETE, nullptr);

    const next_os_mesh_irrig_t ir = next_os_mesh_state_irrig();

    lv_obj_t *header = next_os_common_create_inset_header_row(root, 22);
    lv_obj_t *ht = lv_label_create(header);
    lv_label_set_text(ht, "VALVE A1 • PLOT A");
    lv_obj_set_style_text_color(ht, next_os_color_clay(), 0);
    lv_obj_align(ht, LV_ALIGN_LEFT_MID, 0, 0);
    lv_obj_t *open_dot = lv_obj_create(header);
    lv_obj_set_size(open_dot, 6, 6);
    lv_obj_align(open_dot, LV_ALIGN_RIGHT_MID, -36, 0);
    lv_obj_set_style_radius(open_dot, LV_RADIUS_CIRCLE, 0);
    lv_obj_set_style_bg_color(open_dot, next_os_color_live_green(), 0);
    lv_obj_t *open = lv_label_create(header);
    lv_label_set_text(open, "OPEN");
    lv_obj_set_style_text_color(open, next_os_color_live_green(), 0);
    lv_obj_align(open, LV_ALIGN_RIGHT_MID, 0, 0);

    lv_obj_t *box = lv_obj_create(root);
    lv_obj_set_size(box, 210, 120);
    lv_obj_align(box, LV_ALIGN_CENTER, 0, -18);
    lv_obj_set_style_bg_color(box, next_os_color_dark(), 0);
    lv_obj_set_style_border_width(box, 0, 0);
    lv_obj_set_style_radius(box, 10, 0);
    next_os_common_disable_scroll(box);

    for (uint8_t i = 0; i < 6; i++) {
        lv_obj_t *p = lv_obj_create(box);
        lv_obj_set_size(p, 4, 4);
        lv_obj_set_style_radius(p, LV_RADIUS_CIRCLE, 0);
        lv_obj_set_style_bg_color(p, next_os_color_blue(), 0);
        lv_obj_set_pos(p, static_cast<int32_t>(20 + i * 28), static_cast<int32_t>(30 + (i % 3) * 12));
    }

    lv_obj_t *wave1 = lv_obj_create(box);
    lv_obj_set_size(wave1, 180, 24);
    lv_obj_align(wave1, LV_ALIGN_CENTER, 0, 10);
    lv_obj_set_style_bg_color(wave1, next_os_color_blue(), 0);
    lv_obj_set_style_bg_opa(wave1, LV_OPA_30, 0);
    lv_obj_set_style_radius(wave1, 12, 0);

    s_countdown = lv_label_create(box);
    lv_label_set_text(s_countdown, ir.countdown);
    lv_obj_set_style_text_font(s_countdown, &lv_font_montserrat_24, 0);
    lv_obj_set_style_text_color(s_countdown, next_os_color_cream(), 0);
    lv_obj_align(s_countdown, LV_ALIGN_CENTER, 0, -8);

    lv_obj_t *rem = lv_label_create(box);
    lv_label_set_text(rem, "REMAINING");
    lv_obj_set_style_text_font(rem, &lv_font_montserrat_12, 0);
    lv_obj_set_style_text_color(rem, next_os_color_muted(), 0);
    lv_obj_align(rem, LV_ALIGN_CENTER, 0, 16);

    s_flow_rate = lv_label_create(root);
    lv_label_set_text(s_flow_rate, "FLOW RATE 2.4 L/min");
    lv_obj_set_style_text_font(s_flow_rate, &lv_font_montserrat_12, 0);
    lv_obj_set_style_text_color(s_flow_rate, next_os_color_blue(), 0);
    lv_obj_align(s_flow_rate, LV_ALIGN_BOTTOM_MID, 0, -56);

    s_used = lv_label_create(root);
    lv_label_set_text(s_used, "USED TODAY 148 L");
    lv_obj_set_style_text_color(s_used, next_os_color_cream(), 0);
    lv_obj_align(s_used, LV_ALIGN_BOTTOM_MID, 0, -40);

    lv_obj_t *btn_row = lv_obj_create(root);
    lv_obj_set_size(btn_row, 200, 32);
    lv_obj_align(btn_row, LV_ALIGN_BOTTOM_MID, 0, -8);
    lv_obj_set_style_bg_opa(btn_row, LV_OPA_TRANSP, 0);
    lv_obj_set_style_border_width(btn_row, 0, 0);
    lv_obj_set_flex_flow(btn_row, LV_FLEX_FLOW_ROW);
    lv_obj_set_flex_align(btn_row, LV_FLEX_ALIGN_SPACE_EVENLY, LV_FLEX_ALIGN_CENTER, LV_FLEX_ALIGN_CENTER);
    next_os_common_disable_scroll(btn_row);

    lv_obj_t *close = lv_button_create(btn_row);
    lv_obj_set_size(close, 88, 28);
    lv_obj_set_style_bg_color(close, next_os_color_dark_separator(), 0);
    lv_obj_t *cl = lv_label_create(close);
    lv_label_set_text(cl, "CLOSE");
    lv_obj_set_style_text_color(cl, next_os_color_cream(), 0);
    lv_obj_center(cl);

    lv_obj_t *ext = lv_button_create(btn_row);
    lv_obj_set_size(ext, 88, 28);
    lv_obj_set_style_bg_color(ext, next_os_color_clay(), 0);
    lv_obj_t *ex = lv_label_create(ext);
    lv_label_set_text(ex, "+15 MIN");
    lv_obj_set_style_text_color(ex, next_os_color_cream(), 0);
    lv_obj_center(ex);

    next_os_irrigation_wave_refresh_from_mesh();
}
