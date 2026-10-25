#include "screens/irrigation_control.h"

#include "layout.h"
#include "mesh_state.h"
#include "screens/common.h"
#include "theme.h"

#include <cstdio>

static lv_obj_t *s_countdown_label = nullptr;
static lv_obj_t *s_flow_value_label = nullptr;

static void irrigation_on_delete(lv_event_t *event) {
    if (lv_event_get_code(event) != LV_EVENT_DELETE) {
        return;
    }
    s_countdown_label = nullptr;
    s_flow_value_label = nullptr;
}

void next_os_irrigation_control_refresh_from_mesh(void) {
    const next_os_mesh_irrig_t ir = next_os_mesh_state_irrig();
    if (nextos_ui_obj_alive(s_countdown_label)) {
        lv_label_set_text(s_countdown_label, ir.countdown);
    }
    if (nextos_ui_obj_alive(s_flow_value_label)) {
        lv_label_set_text(s_flow_value_label, ir.flow_label);
    }
}

void next_os_irrigation_control_create(lv_obj_t *root) {
    next_os_apply_screen_style(root);
    lv_obj_add_event_cb(root, irrigation_on_delete, LV_EVENT_DELETE, nullptr);

    const next_os_mesh_irrig_t ir = next_os_mesh_state_irrig();
    next_os_common_create_header_label(root, "IRIGASI • VALVE A1");

    lv_obj_t *col = lv_obj_create(root);
    lv_obj_set_size(col, nextos_content_width(), LV_SIZE_CONTENT);
    lv_obj_align(col, LV_ALIGN_TOP_MID, 0, nextos_inset_header_y() + 28);
    lv_obj_set_style_bg_opa(col, LV_OPA_TRANSP, 0);
    lv_obj_set_style_border_width(col, 0, 0);
    lv_obj_set_style_pad_all(col, 0, 0);
    lv_obj_set_flex_flow(col, LV_FLEX_FLOW_COLUMN);
    lv_obj_set_flex_align(col, LV_FLEX_ALIGN_START, LV_FLEX_ALIGN_CENTER, LV_FLEX_ALIGN_CENTER);
    next_os_common_disable_scroll(col);

    lv_obj_t *wave = lv_obj_create(col);
    lv_obj_set_width(wave, nextos_content_width());
    lv_obj_set_height(wave, 120);
    lv_obj_set_style_bg_color(wave, NEXTOS_SURFACE_DIM, 0);
    lv_obj_set_style_border_color(wave, NEXTOS_BORDER, 0);
    lv_obj_set_style_border_width(wave, 1, 0);
    lv_obj_set_style_radius(wave, 12, 0);
    next_os_common_disable_scroll(wave);

    lv_obj_t *wave_bar = lv_obj_create(wave);
    lv_obj_set_size(wave_bar, nextos_content_width() - 24, 28);
    lv_obj_align(wave_bar, LV_ALIGN_CENTER, 0, 12);
    lv_obj_set_style_bg_color(wave_bar, NEXTOS_ACCENT_PRIMARY, 0);
    lv_obj_set_style_bg_opa(wave_bar, LV_OPA_20, 0);
    lv_obj_set_style_radius(wave_bar, 14, 0);

    s_countdown_label = lv_label_create(wave);
    lv_label_set_text(s_countdown_label, ir.countdown);
    lv_obj_set_style_text_font(s_countdown_label, &lv_font_montserrat_24, 0);
    lv_obj_set_style_text_color(s_countdown_label, NEXTOS_TEXT_PRIMARY, 0);
    lv_obj_align(s_countdown_label, LV_ALIGN_CENTER, 0, -8);

    lv_obj_t *remain = lv_label_create(wave);
    lv_label_set_text(remain, "REMAINING");
    lv_obj_set_style_text_font(remain, &lv_font_montserrat_12, 0);
    lv_obj_set_style_text_color(remain, NEXTOS_TEXT_MUTED, 0);
    lv_obj_align(remain, LV_ALIGN_CENTER, 0, 18);

    lv_obj_t *flow_title = lv_label_create(col);
    lv_label_set_text(flow_title, "FLOW RATE");
    lv_obj_set_style_text_font(flow_title, &lv_font_montserrat_12, 0);
    lv_obj_set_style_text_color(flow_title, NEXTOS_TEXT_SECONDARY, 0);
    lv_obj_set_style_margin_top(flow_title, 12, 0);

    s_flow_value_label = lv_label_create(col);
    lv_label_set_text(s_flow_value_label, ir.flow_label);
    lv_obj_set_style_text_font(s_flow_value_label, &lv_font_montserrat_12, 0);
    lv_obj_set_style_text_color(s_flow_value_label, NEXTOS_TEXT_PRIMARY, 0);
    lv_obj_set_width(s_flow_value_label, nextos_content_width() - 8);
    lv_label_set_long_mode(s_flow_value_label, LV_LABEL_LONG_WRAP);
    lv_obj_set_style_margin_top(s_flow_value_label, 4, 0);

    lv_obj_t *used = lv_label_create(col);
    lv_label_set_text(used, "USED TODAY 148 L");
    lv_obj_set_style_text_color(used, NEXTOS_TEXT_SECONDARY, 0);
    lv_obj_set_style_margin_top(used, 8, 0);

    lv_obj_t *btn_row = lv_obj_create(col);
    lv_obj_set_size(btn_row, nextos_content_width(), 32);
    lv_obj_set_style_bg_opa(btn_row, LV_OPA_TRANSP, 0);
    lv_obj_set_style_border_width(btn_row, 0, 0);
    lv_obj_set_flex_flow(btn_row, LV_FLEX_FLOW_ROW);
    lv_obj_set_flex_align(btn_row, LV_FLEX_ALIGN_SPACE_EVENLY, LV_FLEX_ALIGN_CENTER, LV_FLEX_ALIGN_CENTER);
    lv_obj_set_style_margin_top(btn_row, 8, 0);
    next_os_common_disable_scroll(btn_row);

    lv_obj_t *close = lv_button_create(btn_row);
    lv_obj_set_size(close, 88, 28);
    lv_obj_set_style_bg_color(close, NEXTOS_SURFACE_DIM, 0);
    lv_obj_t *cl = lv_label_create(close);
    lv_label_set_text(cl, "CLOSE");
    lv_obj_center(cl);

    lv_obj_t *ext = lv_button_create(btn_row);
    lv_obj_set_size(ext, 88, 28);
    lv_obj_set_style_bg_color(ext, NEXTOS_ACCENT_SECONDARY, 0);
    lv_obj_t *ex = lv_label_create(ext);
    lv_label_set_text(ex, "+15 MIN");
    lv_obj_set_style_text_color(ex, NEXTOS_SURFACE, 0);
    lv_obj_center(ex);
}
