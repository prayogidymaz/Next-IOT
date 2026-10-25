#include "screens/settings.h"

#include "config.h"
#include "screens/common.h"
#include "theme.h"

#include <cstdio>

static lv_obj_t *settings_create_row(lv_obj_t *parent, const char *label, const char *value,
                                     lv_color_t value_color) {
    lv_obj_t *card = lv_obj_create(parent);
    lv_obj_set_size(card, 200, 36);
    lv_obj_set_style_radius(card, 10, 0);
    lv_obj_set_style_bg_color(card, next_os_color_cream(), 0);
    lv_obj_set_style_border_color(card, next_os_color_separator(), 0);
    lv_obj_set_style_border_width(card, 1, 0);
    lv_obj_set_style_pad_hor(card, 10, 0);
    next_os_common_disable_scroll(card);

    lv_obj_t *left = lv_label_create(card);
    lv_label_set_text(left, label);
    lv_obj_set_style_text_font(left, &lv_font_montserrat_12, 0);
    lv_obj_set_style_text_color(left, next_os_color_dark(), 0);
    lv_obj_align(left, LV_ALIGN_LEFT_MID, 0, 0);

    lv_obj_t *right = lv_label_create(card);
    lv_label_set_text(right, value);
    lv_obj_set_style_text_font(right, &lv_font_montserrat_12, 0);
    lv_obj_set_style_text_color(right, value_color, 0);
    lv_obj_align(right, LV_ALIGN_RIGHT_MID, 0, 0);
    return card;
}

void next_os_settings_create(lv_obj_t *root) {
    next_os_apply_screen_style(root);

    lv_obj_t *header = next_os_common_create_inset_header_row(root, 24);
    lv_obj_t *gear = lv_label_create(header);
    lv_label_set_text(gear, LV_SYMBOL_SETTINGS);
    lv_obj_set_style_text_color(gear, next_os_color_olive(), 0);
    lv_obj_align(gear, LV_ALIGN_LEFT_MID, 0, 0);

    lv_obj_t *title = lv_label_create(header);
    lv_label_set_text(title, "SETTINGS");
    lv_obj_set_style_text_font(title, &lv_font_montserrat_12, 0);
    lv_obj_set_style_text_color(title, next_os_color_olive(), 0);
    lv_obj_align(title, LV_ALIGN_CENTER, 0, 0);

    lv_obj_t *list = lv_obj_create(root);
    lv_obj_set_size(list, 210, 150);
    lv_obj_align(list, LV_ALIGN_CENTER, 0, 8);
    lv_obj_set_style_bg_opa(list, LV_OPA_TRANSP, 0);
    lv_obj_set_style_border_width(list, 0, 0);
    lv_obj_set_style_pad_row(list, 8, 0);
    lv_obj_set_flex_flow(list, LV_FLEX_FLOW_COLUMN);
    lv_obj_set_flex_align(list, LV_FLEX_ALIGN_CENTER, LV_FLEX_ALIGN_CENTER, LV_FLEX_ALIGN_CENTER);
    next_os_common_disable_scroll(list);

    settings_create_row(list, "Theme", "CREAM ▸", next_os_color_clay());

    lv_obj_t *bright = settings_create_row(list, "Brightness", "70", next_os_color_olive());
    lv_obj_t *slider = lv_obj_create(bright);
    lv_obj_set_size(slider, 48, 4);
    lv_obj_align(slider, LV_ALIGN_RIGHT_MID, -28, 0);
    lv_obj_set_style_bg_color(slider, next_os_color_separator(), 0);
    lv_obj_set_style_radius(slider, 2, 0);
    lv_obj_t *knob = lv_obj_create(bright);
    lv_obj_set_size(knob, 8, 8);
    lv_obj_align_to(knob, slider, LV_ALIGN_LEFT_MID, 30, 0);
    lv_obj_set_style_bg_color(knob, next_os_color_olive(), 0);
    lv_obj_set_style_radius(knob, LV_RADIUS_CIRCLE, 0);

    lv_obj_t *notif = settings_create_row(list, "Notif", "", next_os_color_olive());
    lv_obj_t *sw = lv_obj_create(notif);
    lv_obj_set_size(sw, 32, 16);
    lv_obj_align(sw, LV_ALIGN_RIGHT_MID, 0, 0);
    lv_obj_set_style_radius(sw, 8, 0);
    lv_obj_set_style_bg_color(sw, next_os_color_live_green(), 0);
    lv_obj_t *dot = lv_obj_create(sw);
    lv_obj_set_size(dot, 12, 12);
    lv_obj_align(dot, LV_ALIGN_RIGHT_MID, -2, 0);
    lv_obj_set_style_bg_color(dot, next_os_color_cream(), 0);
    lv_obj_set_style_radius(dot, LV_RADIUS_CIRCLE, 0);

    settings_create_row(list, "Pair device", "QR ▸", next_os_color_clay());

    char ver[32];
    (void)std::snprintf(ver, sizeof(ver), "NEXT-OS WEAR v%s", NEXT_OS_FIRMWARE_VERSION);
    lv_obj_t *footer = lv_label_create(root);
    lv_label_set_text(footer, ver);
    lv_obj_set_style_text_font(footer, &lv_font_montserrat_12, 0);
    lv_obj_set_style_text_color(footer, next_os_color_muted(), 0);
    lv_obj_align(footer, LV_ALIGN_BOTTOM_MID, 0, -12);
}
