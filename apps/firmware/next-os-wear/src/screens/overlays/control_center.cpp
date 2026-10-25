#include "screens/overlays/control_center.h"

#include "haptic.h"
#include "layout.h"
#include "mqtt.h"
#include "navigation/nav_stack.h"
#include "runtime_theme.h"
#include "screens/screen_manager.h"
#include "theme.h"
#include "user_prefs.h"

#include <cstdio>

static next_os_overlay_dismiss_fn s_dismiss = nullptr;

static void control_dismiss_cb(lv_event_t *event) {
    if (lv_event_get_code(event) != LV_EVENT_CLICKED) {
        return;
    }
    if (s_dismiss != nullptr) {
        s_dismiss();
    }
}

static void control_brightness_cb(lv_event_t *event) {
    lv_obj_t *slider = static_cast<lv_obj_t *>(lv_event_get_target(event));
    next_os_user_prefs_set_brightness(static_cast<uint8_t>(lv_slider_get_value(slider)));
}

static void control_theme_cb(lv_event_t *event) {
    if (lv_event_get_code(event) != LV_EVENT_CLICKED) {
        return;
    }
    next_os_runtime_theme_cycle();
    next_os_runtime_theme_apply_global_refresh();
    next_os_screen_manager_reload_current();
}

static void control_dnd_cb(lv_event_t *event) {
    if (lv_event_get_code(event) != LV_EVENT_CLICKED) {
        return;
    }
    next_os_user_prefs_set_dnd_enabled(!next_os_user_prefs_dnd_enabled());
}

static void control_flash_cb(lv_event_t *event) {
    if (lv_event_get_code(event) != LV_EVENT_CLICKED) {
        return;
    }
    if (s_dismiss != nullptr) {
        s_dismiss();
    }
    next_os_nav_stack_push(NEXT_OS_SCREEN_APP_FLASHLIGHT, true);
}

void next_os_control_center_show(lv_obj_t *parent, next_os_overlay_dismiss_fn on_dismiss) {
    s_dismiss = on_dismiss;
    lv_obj_set_size(parent, NEXTOS_W, NEXTOS_H);
    lv_obj_set_style_bg_color(parent, NEXTOS_TEXT_PRIMARY, 0);
    lv_obj_set_style_bg_opa(parent, LV_OPA_50, 0);

    lv_obj_t *panel = lv_obj_create(parent);
    lv_obj_set_size(panel, NEXTOS_W, NEXTOS_IS_ROUND ? 150 : 180);
    lv_obj_align(panel, LV_ALIGN_TOP_MID, 0, 0);
    lv_obj_set_style_bg_color(panel, NEXTOS_SURFACE, 0);
    lv_obj_set_style_radius(panel, 0, 0);

    lv_obj_t *slider = lv_slider_create(panel);
    lv_obj_set_width(slider, nextos_content_width() - 20);
    lv_obj_align(slider, LV_ALIGN_TOP_MID, 0, 16);
    lv_slider_set_range(slider, 10, 100);
    lv_slider_set_value(slider, static_cast<int32_t>(next_os_user_prefs_brightness()), LV_ANIM_OFF);
    lv_obj_add_event_cb(slider, control_brightness_cb, LV_EVENT_VALUE_CHANGED, nullptr);

    lv_obj_t *grid = lv_obj_create(panel);
    lv_obj_set_size(grid, nextos_content_width(), 70);
    lv_obj_align(grid, LV_ALIGN_CENTER, 0, 8);
    lv_obj_set_style_bg_opa(grid, LV_OPA_TRANSP, 0);
    lv_obj_set_style_border_width(grid, 0, 0);
    lv_obj_set_flex_flow(grid, LV_FLEX_FLOW_ROW_WRAP);
    lv_obj_set_style_pad_column(grid, 8, 0);
    lv_obj_set_style_pad_row(grid, 8, 0);

    lv_obj_t *flash = lv_button_create(grid);
    lv_obj_add_event_cb(flash, control_flash_cb, LV_EVENT_CLICKED, nullptr);
    lv_label_set_text(lv_label_create(flash), LV_SYMBOL_CHARGE);

    lv_obj_t *dnd = lv_button_create(grid);
    lv_obj_add_event_cb(dnd, control_dnd_cb, LV_EVENT_CLICKED, nullptr);
    lv_label_set_text(lv_label_create(dnd), "DND");

    lv_obj_t *theme = lv_button_create(grid);
    lv_obj_add_event_cb(theme, control_theme_cb, LV_EVENT_CLICKED, nullptr);
    lv_label_set_text(lv_label_create(theme), "Theme");

    char status[48];
    (void)std::snprintf(status, sizeof(status), "Bat 78%%  WiFi %s  MQTT %s", LV_SYMBOL_WIFI,
                        next_os_mqtt_is_connected() ? "OK" : "OFF");
    lv_obj_t *footer = lv_label_create(panel);
    lv_label_set_text(footer, status);
    lv_obj_set_style_text_font(footer, &lv_font_montserrat_12, 0);
    lv_obj_align(footer, LV_ALIGN_BOTTOM_MID, 0, -8);

    lv_obj_add_event_cb(parent, control_dismiss_cb, LV_EVENT_CLICKED, nullptr);
    nextos_haptic_pulse(NEXTOS_HAPTIC_LIGHT);
}
