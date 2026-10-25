#include "screens/irrigation_control.h"

#include "mesh_state.h"
#include "screens/common.h"
#include "theme.h"

static lv_obj_t *s_countdown_label = nullptr;
static lv_obj_t *s_status_label = nullptr;
static lv_obj_t *s_flow_label = nullptr;

void next_os_irrigation_control_refresh_from_mesh(void) {
    const next_os_mesh_irrig_t ir = next_os_mesh_state_irrig();
    if (s_countdown_label != nullptr && lv_obj_is_in_widget_tree(s_countdown_label)) {
        lv_label_set_text(s_countdown_label, ir.countdown);
    }
    if (s_status_label != nullptr && lv_obj_is_in_widget_tree(s_status_label)) {
        lv_label_set_text(s_status_label, ir.active ? "● ACTIVE" : "○ IDLE");
        lv_obj_set_style_text_color(s_status_label,
                                    ir.active ? next_os_color_olive() : next_os_color_muted(), 0);
    }
    if (s_flow_label != nullptr && lv_obj_is_in_widget_tree(s_flow_label)) {
        lv_label_set_text(s_flow_label, ir.flow_label);
    }
}

void next_os_irrigation_control_create(lv_obj_t *root) {
    next_os_apply_screen_style(root);

    const next_os_mesh_irrig_t ir = next_os_mesh_state_irrig();
    next_os_common_create_header_label(root, "IRIGASI • VALVE A1");

    lv_obj_t *ring = next_os_common_create_round_container(root, 120);
    lv_obj_set_style_bg_color(ring, next_os_color_clay(), 0);
    lv_obj_set_style_border_color(ring, next_os_color_clay(), 0);
    lv_obj_align(ring, LV_ALIGN_CENTER, 0, -12);

    lv_obj_t *drop = lv_label_create(ring);
    lv_label_set_text(drop, LV_SYMBOL_TINT);
    lv_obj_set_style_text_color(drop, next_os_color_cream(), 0);
    lv_obj_set_style_text_font(drop, &lv_font_montserrat_24, 0);
    lv_obj_align(drop, LV_ALIGN_CENTER, 0, -16);

    s_countdown_label = lv_label_create(ring);
    lv_label_set_text(s_countdown_label, ir.countdown);
    lv_obj_set_style_text_font(s_countdown_label, &lv_font_montserrat_24, 0);
    lv_obj_set_style_text_color(s_countdown_label, next_os_color_cream(), 0);
    lv_obj_align(s_countdown_label, LV_ALIGN_CENTER, 0, 18);

    lv_obj_t *remain = lv_label_create(root);
    lv_label_set_text(remain, "REMAINING");
    lv_obj_set_style_text_font(remain, &lv_font_montserrat_12, 0);
    lv_obj_set_style_text_color(remain, next_os_color_muted(), 0);
    lv_obj_align(remain, LV_ALIGN_CENTER, 0, 58);

    s_status_label = lv_label_create(root);
    lv_label_set_text(s_status_label, ir.active ? "● ACTIVE" : "○ IDLE");
    lv_obj_set_style_text_color(s_status_label, next_os_color_olive(), 0);
    lv_obj_set_style_text_font(s_status_label, &lv_font_montserrat_12, 0);
    lv_obj_align(s_status_label, LV_ALIGN_CENTER, 0, 78);

    s_flow_label = lv_label_create(root);
    lv_label_set_text(s_flow_label, ir.flow_label);
    lv_obj_set_style_text_font(s_flow_label, &lv_font_montserrat_12, 0);
    lv_obj_set_style_text_color(s_flow_label, next_os_color_dark(), 0);
    lv_obj_align(s_flow_label, LV_ALIGN_BOTTOM_MID, 0, -36);

    lv_obj_t *actions = lv_label_create(root);
    lv_label_set_text(actions, LV_SYMBOL_LEFT " CLOSE   EXTEND " LV_SYMBOL_RIGHT);
    lv_obj_set_style_text_font(actions, &lv_font_montserrat_12, 0);
    lv_obj_set_style_text_color(actions, next_os_color_olive(), 0);
    lv_obj_align(actions, LV_ALIGN_BOTTOM_MID, 0, -14);
    next_os_common_create_nav_buttons(root);
}
