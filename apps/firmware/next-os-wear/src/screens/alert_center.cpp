#include "screens/alert_center.h"

#include "layout.h"
#include "mesh_state.h"
#include "screens/common.h"
#include "theme.h"

#include <cstdio>

static lv_obj_t *s_title_label = nullptr;
static lv_obj_t *s_badge_label = nullptr;
static lv_obj_t *s_headline_label = nullptr;
static lv_obj_t *s_sub_label = nullptr;
static lv_obj_t *s_ts_label = nullptr;

static void alert_center_on_delete(lv_event_t *event) {
    if (lv_event_get_code(event) != LV_EVENT_DELETE) {
        return;
    }
    s_title_label = nullptr;
    s_badge_label = nullptr;
    s_headline_label = nullptr;
    s_sub_label = nullptr;
    s_ts_label = nullptr;
}

void next_os_alert_center_refresh_from_mesh(void) {
    char buf[24];
    if (s_title_label != nullptr && lv_obj_is_in_widget_tree(s_title_label)) {
        (void)std::snprintf(buf, sizeof(buf), "%u ALERT AKTIF",
                            static_cast<unsigned>(next_os_mesh_state_alert_count()));
        lv_label_set_text(s_title_label, buf);
    }
    next_os_mesh_alert_t alert {};
    if (!next_os_mesh_state_top_alert(&alert)) {
        return;
    }
    if (s_badge_label != nullptr && lv_obj_is_in_widget_tree(s_badge_label)) {
        lv_label_set_text(s_badge_label, alert.severity);
    }
    if (s_headline_label != nullptr && lv_obj_is_in_widget_tree(s_headline_label)) {
        lv_label_set_text(s_headline_label, alert.title);
    }
    if (s_sub_label != nullptr && lv_obj_is_in_widget_tree(s_sub_label)) {
        lv_label_set_text(s_sub_label, alert.subtitle);
    }
    if (s_ts_label != nullptr && lv_obj_is_in_widget_tree(s_ts_label)) {
        lv_label_set_text(s_ts_label, alert.ago);
    }
}

void next_os_alert_center_create(lv_obj_t *root) {
    next_os_apply_screen_style(root);
    lv_obj_add_event_cb(root, alert_center_on_delete, LV_EVENT_DELETE, nullptr);

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

    s_title_label = lv_label_create(top);
    char title_buf[24];
    (void)std::snprintf(title_buf, sizeof(title_buf), "%u ALERT AKTIF",
                        static_cast<unsigned>(next_os_mesh_state_alert_count()));
    lv_label_set_text(s_title_label, title_buf);
    lv_obj_set_style_text_font(s_title_label, &lv_font_montserrat_12, 0);
    lv_obj_set_style_text_color(s_title_label, next_os_color_critical(), 0);
    lv_obj_align(s_title_label, LV_ALIGN_CENTER, 0, 0);

    lv_obj_t *card = lv_obj_create(root);
    lv_obj_set_size(card, 200, 130);
    lv_obj_align(card, LV_ALIGN_CENTER, 0, 0);
    lv_obj_set_style_bg_color(card, next_os_color_cream(), 0);
    lv_obj_set_style_border_color(card, next_os_color_light_grey(), 0);
    lv_obj_set_style_border_width(card, 2, 0);
    lv_obj_set_style_radius(card, 12, 0);
    lv_obj_set_style_pad_all(card, 10, 0);
    next_os_common_disable_scroll(card);

    next_os_mesh_alert_t alert {};
    if (!next_os_mesh_state_top_alert(&alert)) {
        alert.unresolved = true;
        (void)std::snprintf(alert.title, sizeof(alert.title), "%s", "Sprayer tank 15%");
        (void)std::snprintf(alert.subtitle, sizeof(alert.subtitle), "%s", "Plot B • Refill required");
        (void)std::snprintf(alert.severity, sizeof(alert.severity), "%s", "CRITICAL");
        (void)std::snprintf(alert.ago, sizeof(alert.ago), "%s", "2m ago");
    }

    s_badge_label = lv_label_create(card);
    lv_label_set_text(s_badge_label, alert.severity);
    lv_obj_set_style_text_font(s_badge_label, &lv_font_montserrat_12, 0);
    lv_obj_set_style_text_color(s_badge_label, next_os_color_critical(), 0);
    lv_obj_align(s_badge_label, LV_ALIGN_TOP_LEFT, 0, 0);

    s_headline_label = lv_label_create(card);
    lv_label_set_text(s_headline_label, alert.title);
    lv_obj_set_style_text_font(s_headline_label, &lv_font_montserrat_14, 0);
    lv_obj_set_style_text_color(s_headline_label, next_os_color_dark(), 0);
    lv_obj_align(s_headline_label, LV_ALIGN_TOP_LEFT, 0, 22);

    s_sub_label = lv_label_create(card);
    lv_label_set_text(s_sub_label, alert.subtitle);
    lv_obj_set_style_text_font(s_sub_label, &lv_font_montserrat_12, 0);
    lv_obj_set_style_text_color(s_sub_label, next_os_color_muted(), 0);
    lv_obj_align(s_sub_label, LV_ALIGN_TOP_LEFT, 0, 44);

    s_ts_label = lv_label_create(card);
    lv_label_set_text(s_ts_label, alert.ago);
    lv_obj_set_style_text_font(s_ts_label, &lv_font_montserrat_12, 0);
    lv_obj_set_style_text_color(s_ts_label, next_os_color_muted(), 0);
    lv_obj_align(s_ts_label, LV_ALIGN_TOP_LEFT, 0, 62);

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

    if (!NEXTOS_IS_ROUND) {
        lv_obj_t *card2 = lv_obj_create(root);
        lv_obj_set_size(card2, nextos_content_width(), 72);
        lv_obj_align(card2, LV_ALIGN_BOTTOM_MID, 0, -36);
        lv_obj_set_style_bg_color(card2, next_os_color_cream(), 0);
        lv_obj_set_style_border_color(card2, next_os_color_light_grey(), 0);
        lv_obj_set_style_border_width(card2, 1, 0);
        lv_obj_set_style_radius(card2, 12, 0);
        lv_obj_set_style_pad_all(card2, 10, 0);
        next_os_common_disable_scroll(card2);
        lv_obj_t *t2 = lv_label_create(card2);
        lv_label_set_text(t2, "Tank level low • Plot C");
        lv_obj_set_style_text_font(t2, &lv_font_montserrat_12, 0);
        lv_obj_set_style_text_color(t2, next_os_color_dark(), 0);
        lv_obj_align(t2, LV_ALIGN_TOP_LEFT, 0, 0);
        lv_obj_t *s2 = lv_label_create(card2);
        lv_label_set_text(s2, "WARNING • 12m ago");
        lv_obj_set_style_text_color(s2, next_os_color_clay(), 0);
        lv_obj_align(s2, LV_ALIGN_TOP_LEFT, 0, 20);
    }

    next_os_common_create_pagination_dots(root, 3, 2);
}
