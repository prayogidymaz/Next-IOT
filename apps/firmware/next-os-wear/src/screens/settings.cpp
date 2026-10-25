#include "screens/settings.h"

#include "audio.h"
#include "config.h"
#include "haptic.h"
#include "layout.h"
#include "runtime_theme.h"
#include "screens/common.h"
#include "screens/screen_manager.h"
#include "theme.h"
#include "user_prefs.h"

#include <cstdio>

static lv_obj_t *s_theme_value = nullptr;
static lv_obj_t *s_bright_value = nullptr;
static lv_obj_t *s_notif_switch = nullptr;
static lv_obj_t *s_notif_knob = nullptr;
static lv_obj_t *s_haptic_switch = nullptr;
static lv_obj_t *s_haptic_knob = nullptr;
static lv_obj_t *s_audio_switch = nullptr;
static lv_obj_t *s_audio_knob = nullptr;
static lv_obj_t *s_brightness_modal = nullptr;

static void settings_update_toggle_visual(lv_obj_t *sw, lv_obj_t *knob, bool on) {
    if (sw == nullptr) {
        return;
    }
    lv_obj_set_style_bg_color(sw, on ? NEXTOS_SUCCESS : NEXTOS_BORDER, 0);
    if (knob != nullptr) {
        lv_obj_set_style_bg_color(knob, NEXTOS_SURFACE, 0);
        lv_obj_align(knob, on ? LV_ALIGN_RIGHT_MID : LV_ALIGN_LEFT_MID, on ? -2 : 2, 0);
    }
}

static void settings_update_notif_visual(void) {
    const bool on = next_os_user_prefs_notif_enabled();
    if (s_notif_switch == nullptr) {
        return;
    }
    settings_update_toggle_visual(s_notif_switch, s_notif_knob, on);
}

static void settings_theme_click_cb(lv_event_t *event) {
    if (lv_event_get_code(event) != LV_EVENT_CLICKED) {
        return;
    }
    nextos_haptic_pulse(NEXTOS_HAPTIC_LIGHT);
    next_os_runtime_theme_cycle();
    next_os_runtime_theme_apply_global_refresh();
    if (s_theme_value != nullptr) {
        const char *label =
            next_os_user_prefs_theme() == NEXT_OS_THEME_LIGHT ? "LIGHT ▸" : "DARK ▸";
        lv_label_set_text(s_theme_value, label);
    }
    next_os_screen_manager_reload_current();
}

static void settings_brightness_modal_close_cb(lv_event_t *event) {
    if (lv_event_get_code(event) != LV_EVENT_CLICKED) {
        return;
    }
    if (s_brightness_modal != nullptr) {
        lv_obj_delete(s_brightness_modal);
        s_brightness_modal = nullptr;
    }
}

static void settings_brightness_changed_cb(lv_event_t *event) {
    lv_obj_t *slider = static_cast<lv_obj_t *>(lv_event_get_target(event));
    const int32_t val = lv_slider_get_value(slider);
    next_os_user_prefs_set_brightness(static_cast<uint8_t>(val));
    if (s_bright_value != nullptr) {
        char buf[8];
        (void)std::snprintf(buf, sizeof(buf), "%ld", static_cast<long>(val));
        lv_label_set_text(s_bright_value, buf);
    }
}

static void settings_brightness_click_cb(lv_event_t *event) {
    if (lv_event_get_code(event) != LV_EVENT_CLICKED) {
        return;
    }
    lv_obj_t *root = lv_obj_get_parent(static_cast<lv_obj_t *>(lv_event_get_target(event)));
    while (root != nullptr && lv_obj_get_parent(root) != nullptr) {
        root = lv_obj_get_parent(root);
    }
    if (s_brightness_modal != nullptr) {
        return;
    }
    s_brightness_modal = lv_obj_create(root);
    lv_obj_set_size(s_brightness_modal, NEXTOS_W, NEXTOS_H);
    lv_obj_center(s_brightness_modal);
    lv_obj_set_style_bg_opa(s_brightness_modal, LV_OPA_70, 0);
    lv_obj_set_style_bg_color(s_brightness_modal, next_os_color_dark(), 0);

    lv_obj_t *panel = lv_obj_create(s_brightness_modal);
    lv_obj_set_size(panel, nextos_content_width(), 100);
    lv_obj_center(panel);

    lv_obj_t *slider = lv_slider_create(panel);
    lv_obj_set_width(slider, nextos_content_width() - 24);
    lv_obj_align(slider, LV_ALIGN_CENTER, 0, -8);
    lv_slider_set_range(slider, 10, 100);
    lv_slider_set_value(slider, static_cast<int32_t>(next_os_user_prefs_brightness()), LV_ANIM_OFF);
    lv_obj_add_event_cb(slider, settings_brightness_changed_cb, LV_EVENT_VALUE_CHANGED, nullptr);

    lv_obj_t *done = lv_button_create(panel);
    lv_obj_align(done, LV_ALIGN_BOTTOM_MID, 0, 0);
    lv_obj_add_event_cb(done, settings_brightness_modal_close_cb, LV_EVENT_CLICKED, nullptr);
    lv_obj_t *dl = lv_label_create(done);
    lv_label_set_text(dl, "Done");
    lv_obj_center(dl);
}

static void settings_notif_click_cb(lv_event_t *event) {
    if (lv_event_get_code(event) != LV_EVENT_CLICKED) {
        return;
    }
    nextos_haptic_pulse(NEXTOS_HAPTIC_LIGHT);
    next_os_user_prefs_set_notif_enabled(!next_os_user_prefs_notif_enabled());
    settings_update_notif_visual();
}

static void settings_haptic_click_cb(lv_event_t *event) {
    if (lv_event_get_code(event) != LV_EVENT_CLICKED) {
        return;
    }
    next_os_user_prefs_set_haptic_enabled(!next_os_user_prefs_haptic_enabled());
    settings_update_toggle_visual(s_haptic_switch, s_haptic_knob, next_os_user_prefs_haptic_enabled());
    nextos_haptic_pulse(NEXTOS_HAPTIC_LIGHT);
}

static void settings_audio_click_cb(lv_event_t *event) {
    if (lv_event_get_code(event) != LV_EVENT_CLICKED) {
        return;
    }
    next_os_user_prefs_set_audio_enabled(!next_os_user_prefs_audio_enabled());
    settings_update_toggle_visual(s_audio_switch, s_audio_knob, next_os_user_prefs_audio_enabled());
    nextos_audio_beep(NEXTOS_BEEP_SUCCESS);
}

static void settings_pair_click_cb(lv_event_t *event) {
    if (lv_event_get_code(event) != LV_EVENT_CLICKED) {
        return;
    }
    next_os_screen_manager_show_qr_pair_modal();
}

static lv_obj_t *settings_create_row(lv_obj_t *parent, const char *label, const char *value,
                                     lv_color_t value_color, lv_event_cb_t on_click) {
    lv_obj_t *card = lv_button_create(parent);
    lv_obj_set_size(card, nextos_content_width(), 36);
    lv_obj_set_style_radius(card, 10, 0);
    lv_obj_set_style_bg_color(card, NEXTOS_SURFACE, 0);
    lv_obj_set_style_border_color(card, NEXTOS_BORDER, 0);
    lv_obj_set_style_border_width(card, 1, 0);
    lv_obj_set_style_pad_hor(card, 10, 0);
    if (on_click != nullptr) {
        lv_obj_add_event_cb(card, on_click, LV_EVENT_CLICKED, nullptr);
    }

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

    next_os_common_create_settings_title_row(root);

    lv_obj_t *list = lv_obj_create(root);
    const int32_t list_h = NEXTOS_IS_ROUND ? 168 : nextos_content_height() - 96;
    lv_obj_set_size(list, nextos_content_width(), list_h);
    lv_obj_align(list, LV_ALIGN_TOP_MID, 0, nextos_settings_title_y() + 30);
    lv_obj_set_style_bg_opa(list, LV_OPA_TRANSP, 0);
    lv_obj_set_style_border_width(list, 0, 0);
    lv_obj_set_style_pad_row(list, 8, 0);
    lv_obj_set_flex_flow(list, LV_FLEX_FLOW_COLUMN);
    lv_obj_set_flex_align(list, LV_FLEX_ALIGN_CENTER, LV_FLEX_ALIGN_CENTER, LV_FLEX_ALIGN_CENTER);
    next_os_common_disable_scroll(list);

    const char *theme_label =
        next_os_user_prefs_theme() == NEXT_OS_THEME_LIGHT ? "LIGHT ▸" : "DARK ▸";
    lv_obj_t *theme_row = settings_create_row(list, "Theme", theme_label, next_os_color_clay(),
                                               settings_theme_click_cb);
    s_theme_value = lv_obj_get_child(theme_row, 1);

    char bright_buf[8];
    (void)std::snprintf(bright_buf, sizeof(bright_buf), "%u",
                        static_cast<unsigned>(next_os_user_prefs_brightness()));
    lv_obj_t *bright_row =
        settings_create_row(list, "Brightness", bright_buf, next_os_color_olive(), settings_brightness_click_cb);
    s_bright_value = lv_obj_get_child(bright_row, 1);

    lv_obj_t *notif = settings_create_row(list, "Notif", "", next_os_color_olive(), settings_notif_click_cb);
    s_notif_switch = lv_obj_create(notif);
    lv_obj_set_size(s_notif_switch, 32, 16);
    lv_obj_align(s_notif_switch, LV_ALIGN_RIGHT_MID, 0, 0);
    lv_obj_set_style_radius(s_notif_switch, 8, 0);
    s_notif_knob = lv_obj_create(s_notif_switch);
    lv_obj_set_size(s_notif_knob, 12, 12);
    lv_obj_set_style_bg_color(s_notif_knob, next_os_color_cream(), 0);
    lv_obj_set_style_radius(s_notif_knob, LV_RADIUS_CIRCLE, 0);
    settings_update_notif_visual();

    lv_obj_t *haptic = settings_create_row(list, "Haptic", "", next_os_color_olive(), settings_haptic_click_cb);
    s_haptic_switch = lv_obj_create(haptic);
    lv_obj_set_size(s_haptic_switch, 32, 16);
    lv_obj_align(s_haptic_switch, LV_ALIGN_RIGHT_MID, 0, 0);
    lv_obj_set_style_radius(s_haptic_switch, 8, 0);
    s_haptic_knob = lv_obj_create(s_haptic_switch);
    lv_obj_set_size(s_haptic_knob, 12, 12);
    lv_obj_set_style_radius(s_haptic_knob, LV_RADIUS_CIRCLE, 0);
    settings_update_toggle_visual(s_haptic_switch, s_haptic_knob, next_os_user_prefs_haptic_enabled());

    lv_obj_t *audio = settings_create_row(list, "Audio", "", next_os_color_olive(), settings_audio_click_cb);
    s_audio_switch = lv_obj_create(audio);
    lv_obj_set_size(s_audio_switch, 32, 16);
    lv_obj_align(s_audio_switch, LV_ALIGN_RIGHT_MID, 0, 0);
    lv_obj_set_style_radius(s_audio_switch, 8, 0);
    s_audio_knob = lv_obj_create(s_audio_switch);
    lv_obj_set_size(s_audio_knob, 12, 12);
    lv_obj_set_style_radius(s_audio_knob, LV_RADIUS_CIRCLE, 0);
    settings_update_toggle_visual(s_audio_switch, s_audio_knob, next_os_user_prefs_audio_enabled());

    settings_create_row(list, "Pair device", "QR ▸", next_os_color_clay(), settings_pair_click_cb);

    char ver[32];
    (void)std::snprintf(ver, sizeof(ver), "NEXT-OS WEAR v%s", NEXT_OS_FIRMWARE_VERSION);
    lv_obj_t *footer = lv_label_create(root);
    lv_label_set_text(footer, ver);
    lv_obj_set_style_text_font(footer, &lv_font_montserrat_12, 0);
    lv_obj_set_style_text_color(footer, next_os_color_muted(), 0);
    lv_obj_align(footer, LV_ALIGN_BOTTOM_MID, 0, -nextos_safe_padding_bottom());
}
