#include "screens/irrigation_control.h"

#include "screens/common.h"
#include "theme.h"

void next_os_irrigation_control_create(lv_obj_t *root) {
    next_os_apply_screen_style(root);

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

    lv_obj_t *countdown = lv_label_create(ring);
    lv_label_set_text(countdown, "14:23");
    lv_obj_set_style_text_font(countdown, &lv_font_montserrat_24, 0);
    lv_obj_set_style_text_color(countdown, next_os_color_cream(), 0);
    lv_obj_align(countdown, LV_ALIGN_CENTER, 0, 18);

    lv_obj_t *remain = lv_label_create(root);
    lv_label_set_text(remain, "REMAINING");
    lv_obj_set_style_text_font(remain, &lv_font_montserrat_12, 0);
    lv_obj_set_style_text_color(remain, next_os_color_muted(), 0);
    lv_obj_align(remain, LV_ALIGN_CENTER, 0, 58);

    lv_obj_t *status = lv_label_create(root);
    lv_label_set_text(status, "● ACTIVE");
    lv_obj_set_style_text_color(status, next_os_color_olive(), 0);
    lv_obj_set_style_text_font(status, &lv_font_montserrat_12, 0);
    lv_obj_align(status, LV_ALIGN_CENTER, 0, 78);

    lv_obj_t *flow = lv_label_create(root);
    lv_label_set_text(flow, "Flow 2.4 L/min • Plot A");
    lv_obj_set_style_text_font(flow, &lv_font_montserrat_12, 0);
    lv_obj_set_style_text_color(flow, next_os_color_dark(), 0);
    lv_obj_align(flow, LV_ALIGN_BOTTOM_MID, 0, -36);

    lv_obj_t *actions = lv_label_create(root);
    lv_label_set_text(actions, LV_SYMBOL_LEFT " CLOSE   EXTEND " LV_SYMBOL_RIGHT);
    lv_obj_set_style_text_font(actions, &lv_font_montserrat_12, 0);
    lv_obj_set_style_text_color(actions, next_os_color_olive(), 0);
    lv_obj_align(actions, LV_ALIGN_BOTTOM_MID, 0, -14);
}
