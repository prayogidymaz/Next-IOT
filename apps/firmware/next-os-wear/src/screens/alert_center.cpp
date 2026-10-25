#include "screens/alert_center.h"

#include "screens/common.h"
#include "theme.h"

void next_os_alert_center_create(lv_obj_t *root) {
    next_os_apply_screen_style(root);

    lv_obj_t *top = lv_obj_create(root);
    lv_obj_set_size(top, 220, 24);
    lv_obj_align(top, LV_ALIGN_TOP_MID, 0, 12);
    lv_obj_set_style_bg_opa(top, LV_OPA_TRANSP, 0);
    lv_obj_set_style_border_width(top, 0, 0);
    next_os_common_disable_scroll(top);

    lv_obj_t *alert_icon = lv_label_create(top);
    lv_label_set_text(alert_icon, LV_SYMBOL_WARNING);
    lv_obj_set_style_text_color(alert_icon, next_os_color_critical(), 0);
    lv_obj_align(alert_icon, LV_ALIGN_LEFT_MID, 0, 0);

    lv_obj_t *title = lv_label_create(top);
    lv_label_set_text(title, "3 ALERT AKTIF");
    lv_obj_set_style_text_font(title, &lv_font_montserrat_12, 0);
    lv_obj_set_style_text_color(title, next_os_color_critical(), 0);
    lv_obj_align(title, LV_ALIGN_CENTER, 0, 0);

    lv_obj_t *card = lv_obj_create(root);
    lv_obj_set_size(card, 200, 130);
    lv_obj_align(card, LV_ALIGN_CENTER, 0, 0);
    lv_obj_set_style_bg_color(card, next_os_color_cream(), 0);
    lv_obj_set_style_border_color(card, next_os_color_light_grey(), 0);
    lv_obj_set_style_border_width(card, 2, 0);
    lv_obj_set_style_radius(card, 12, 0);
    lv_obj_set_style_pad_all(card, 10, 0);
    next_os_common_disable_scroll(card);

    lv_obj_t *badge = lv_label_create(card);
    lv_label_set_text(badge, "CRITICAL");
    lv_obj_set_style_text_font(badge, &lv_font_montserrat_12, 0);
    lv_obj_set_style_text_color(badge, next_os_color_critical(), 0);
    lv_obj_align(badge, LV_ALIGN_TOP_LEFT, 0, 0);

    lv_obj_t *headline = lv_label_create(card);
    lv_label_set_text(headline, "Sprayer tank 15%");
    lv_obj_set_style_text_font(headline, &lv_font_montserrat_14, 0);
    lv_obj_set_style_text_color(headline, next_os_color_dark(), 0);
    lv_obj_align(headline, LV_ALIGN_TOP_LEFT, 0, 22);

    lv_obj_t *sub = lv_label_create(card);
    lv_label_set_text(sub, "Plot B • Refill required");
    lv_obj_set_style_text_font(sub, &lv_font_montserrat_12, 0);
    lv_obj_set_style_text_color(sub, next_os_color_muted(), 0);
    lv_obj_align(sub, LV_ALIGN_TOP_LEFT, 0, 44);

    lv_obj_t *ts = lv_label_create(card);
    lv_label_set_text(ts, "2m ago");
    lv_obj_set_style_text_font(ts, &lv_font_montserrat_12, 0);
    lv_obj_set_style_text_color(ts, next_os_color_muted(), 0);
    lv_obj_align(ts, LV_ALIGN_TOP_LEFT, 0, 62);

    lv_obj_t *btn_row = lv_obj_create(card);
    lv_obj_set_size(btn_row, 180, 32);
    lv_obj_align(btn_row, LV_ALIGN_BOTTOM_MID, 0, 0);
    lv_obj_set_style_bg_opa(btn_row, LV_OPA_TRANSP, 0);
    lv_obj_set_style_border_width(btn_row, 0, 0);
    lv_obj_set_flex_flow(btn_row, LV_FLEX_FLOW_ROW);
    lv_obj_set_flex_align(btn_row, LV_FLEX_ALIGN_SPACE_EVENLY, LV_FLEX_ALIGN_CENTER, LV_FLEX_ALIGN_CENTER);
    next_os_common_disable_scroll(btn_row);

    lv_obj_t *ack = lv_button_create(btn_row);
    lv_obj_set_size(ack, 72, 28);
    lv_obj_set_style_bg_color(ack, next_os_color_cream(), 0);
    lv_obj_set_style_border_color(ack, next_os_color_light_grey(), 0);
    lv_obj_set_style_border_width(ack, 1, 0);
    lv_obj_t *ack_l = lv_label_create(ack);
    lv_label_set_text(ack_l, "ACK");
    lv_obj_set_style_text_color(ack_l, next_os_color_dark(), 0);
    lv_obj_center(ack_l);

    lv_obj_t *detail = lv_button_create(btn_row);
    lv_obj_set_size(detail, 72, 28);
    lv_obj_set_style_bg_color(detail, next_os_color_olive(), 0);
    lv_obj_t *det_l = lv_label_create(detail);
    lv_label_set_text(det_l, "DETAIL");
    lv_obj_set_style_text_color(det_l, next_os_color_cream(), 0);
    lv_obj_center(det_l);

    next_os_common_create_pagination_dots(root, 3, 2);
}
