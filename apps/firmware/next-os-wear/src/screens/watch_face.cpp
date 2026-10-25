#include "screens/watch_face.h"

#include "haptic.h"
#include "mesh_state.h"
#include "mqtt.h"
#include "layout.h"
#include "navigation/nav_stack.h"

#include <cstdint>
#include "runtime_theme.h"
#include "screens/common.h"
#include "screens/screen_manager.h"
#include "theme.h"

#include <cstdio>
#include <ctime>

static lv_obj_t *s_clock_label = nullptr;
static lv_obj_t *s_date_label = nullptr;
static lv_obj_t *s_wifi_label = nullptr;
static lv_obj_t *s_kpi_value_labels[3] = {nullptr, nullptr, nullptr};
static lv_timer_t *s_clock_timer = nullptr;
static lv_timer_t *s_long_press_timer = nullptr;
static int32_t s_press_y = 0;
static uint8_t s_variant = 0;
static lv_obj_t *s_variant_hint = nullptr;

static void watch_face_kpi_shortcut_cb(lv_event_t *event);
static void watch_face_long_press_cb(lv_timer_t *timer);
static void watch_face_pointer_cb(lv_event_t *event);

static void watch_face_format_time(char *buf, size_t len, uint8_t hour, uint8_t minute) {
    (void)std::snprintf(buf, len, "%02u:%02u", static_cast<unsigned>(hour), static_cast<unsigned>(minute));
}

static bool watch_face_local_tm(std::tm *out) {
    const std::time_t now = std::time(nullptr);
    if (now == static_cast<std::time_t>(-1)) {
        return false;
    }
#if defined(_WIN32)
    return localtime_s(out, &now) == 0;
#else
    std::tm *lt = std::localtime(&now);
    if (lt == nullptr) {
        return false;
    }
    *out = *lt;
    return true;
#endif
}

static void watch_face_format_date(char *buf, size_t len) {
    std::tm lt {};
    if (watch_face_local_tm(&lt)) {
        static const char *days[] = {"MIN", "SEN", "SEL", "RAB", "KAM", "JUM", "SAB"};
        const char *day = days[lt.tm_wday];
        (void)std::snprintf(buf, len, "%s, %02d OKT", day, lt.tm_mday);
        return;
    }
    (void)std::snprintf(buf, len, "SAB, 24 OKT");
}

static void watch_face_refresh_clock(void) {
    if (s_clock_label == nullptr || !lv_obj_is_in_widget_tree(s_clock_label)) {
        return;
    }

    uint8_t hour = 7;
    uint8_t minute = 42;

    std::tm lt {};
    if (watch_face_local_tm(&lt)) {
        hour = static_cast<uint8_t>(lt.tm_hour);
        minute = static_cast<uint8_t>(lt.tm_min);
    }

    char tbuf[8];
    watch_face_format_time(tbuf, sizeof(tbuf), hour, minute);
    lv_label_set_text(s_clock_label, tbuf);

    if (s_date_label != nullptr) {
        char dbuf[20];
        watch_face_format_date(dbuf, sizeof(dbuf));
        lv_label_set_text(s_date_label, dbuf);
    }
}

static void watch_face_timer_cb(lv_timer_t *timer) {
    (void)timer;
    watch_face_refresh_clock();
}

static void watch_face_on_delete(lv_event_t *event) {
    if (lv_event_get_code(event) != LV_EVENT_DELETE) {
        return;
    }
    if (s_clock_timer != nullptr) {
        lv_timer_delete(s_clock_timer);
        s_clock_timer = nullptr;
    }
    if (s_long_press_timer != nullptr) {
        lv_timer_delete(s_long_press_timer);
        s_long_press_timer = nullptr;
    }
    s_clock_label = nullptr;
    s_date_label = nullptr;
    s_wifi_label = nullptr;
    s_kpi_value_labels[0] = nullptr;
    s_kpi_value_labels[1] = nullptr;
    s_kpi_value_labels[2] = nullptr;
}

static lv_obj_t *watch_face_create_kpi_tile(lv_obj_t *parent, const char *value, const char *unit,
                                            lv_color_t value_color, lv_obj_t **out_value_label) {
    lv_obj_t *col = lv_obj_create(parent);
    lv_obj_set_size(col, 56, LV_SIZE_CONTENT);
    lv_obj_set_style_bg_opa(col, LV_OPA_TRANSP, 0);
    lv_obj_set_style_border_width(col, 0, 0);
    lv_obj_set_style_pad_all(col, 0, 0);
    lv_obj_set_style_pad_row(col, 3, 0);
    lv_obj_set_flex_flow(col, LV_FLEX_FLOW_COLUMN);
    lv_obj_set_flex_align(col, LV_FLEX_ALIGN_CENTER, LV_FLEX_ALIGN_CENTER, LV_FLEX_ALIGN_CENTER);
    next_os_common_disable_scroll(col);

    lv_obj_t *val = lv_label_create(col);
    lv_label_set_text(val, value);
    lv_obj_set_style_text_font(val, &lv_font_montserrat_24, 0);
    lv_obj_set_style_text_color(val, value_color, 0);

    lv_obj_t *lbl = lv_label_create(col);
    lv_label_set_text(lbl, unit);
    lv_obj_set_style_text_font(lbl, &lv_font_montserrat_12, 0);
    lv_obj_set_style_text_color(lbl, next_os_color_muted(), 0);
    lv_obj_set_style_text_letter_space(lbl, 1, 0);

    if (out_value_label != nullptr) {
        *out_value_label = val;
    }
    return col;
}

void next_os_watch_face_refresh_from_mesh(void) {
    char buf[8];
    if (s_kpi_value_labels[0] != nullptr && lv_obj_is_in_widget_tree(s_kpi_value_labels[0])) {
        (void)std::snprintf(buf, sizeof(buf), "%u",
                            static_cast<unsigned>(next_os_mesh_state_farm_count()));
        lv_label_set_text(s_kpi_value_labels[0], buf);
    }
    if (s_kpi_value_labels[1] != nullptr && lv_obj_is_in_widget_tree(s_kpi_value_labels[1])) {
        (void)std::snprintf(buf, sizeof(buf), "%u",
                            static_cast<unsigned>(next_os_mesh_state_alert_count()));
        lv_label_set_text(s_kpi_value_labels[1], buf);
    }
    if (s_kpi_value_labels[2] != nullptr && lv_obj_is_in_widget_tree(s_kpi_value_labels[2])) {
        (void)std::snprintf(buf, sizeof(buf), "%u",
                            static_cast<unsigned>(next_os_mesh_state_irig_count()));
        lv_label_set_text(s_kpi_value_labels[2], buf);
    }
    if (s_wifi_label != nullptr && lv_obj_is_in_widget_tree(s_wifi_label)) {
        lv_obj_set_style_text_color(
            s_wifi_label,
            next_os_mqtt_is_connected() ? next_os_color_olive() : next_os_color_light_grey(), 0);
    }
}

void next_os_watch_face_create(lv_obj_t *root) {
    next_os_apply_screen_style(root);
    lv_obj_add_event_cb(root, watch_face_on_delete, LV_EVENT_DELETE, nullptr);

    /* Bar atas: inset 36px kiri/kanan + di bawah nav 28×8 (y≤36) */
    lv_obj_t *top_row = lv_obj_create(root);
    lv_obj_set_size(top_row, nextos_inset_header_width(), 24);
    lv_obj_align(top_row, LV_ALIGN_TOP_MID, 0, nextos_status_header_y());
    lv_obj_set_style_bg_opa(top_row, LV_OPA_TRANSP, 0);
    lv_obj_set_style_border_width(top_row, 0, 0);
    lv_obj_set_style_pad_all(top_row, 0, 0);
    next_os_common_disable_scroll(top_row);

    lv_obj_t *farm = lv_label_create(top_row);
    lv_label_set_text(farm, "KEBUN KOPI");
    lv_obj_set_style_text_font(farm, &lv_font_montserrat_12, 0);
    lv_obj_set_style_text_color(farm, next_os_color_olive(), 0);
    lv_obj_align(farm, LV_ALIGN_LEFT_MID, 0, 0);

    s_wifi_label = lv_label_create(top_row);
    lv_label_set_text(s_wifi_label, LV_SYMBOL_WIFI);
    lv_obj_set_style_text_color(s_wifi_label, next_os_color_olive(), 0);
    lv_obj_align(s_wifi_label, LV_ALIGN_CENTER, 0, 0);

    lv_obj_t *bat = lv_label_create(top_row);
    lv_label_set_text(bat, "78%");
    lv_obj_set_style_text_font(bat, &lv_font_montserrat_12, 0);
    lv_obj_set_style_text_color(bat, next_os_color_dark(), 0);
    lv_obj_align(bat, LV_ALIGN_RIGHT_MID, 0, 0);

    s_clock_label = lv_label_create(root);
    lv_obj_set_style_text_font(s_clock_label, next_os_font_clock_large(), 0);
    lv_obj_set_style_text_color(s_clock_label, next_os_color_dark(), 0);
    lv_obj_align(s_clock_label, LV_ALIGN_CENTER, 0, -18);

    s_date_label = lv_label_create(root);
    lv_obj_set_style_text_font(s_date_label, &lv_font_montserrat_12, 0);
    lv_obj_set_style_text_color(s_date_label, next_os_color_olive(), 0);
    lv_obj_align(s_date_label, LV_ALIGN_CENTER, 0, 28);

    /* KPI bawah */
    lv_obj_t *kpi_row = lv_obj_create(root);
    lv_obj_set_size(kpi_row, 210, 52);
    lv_obj_align(kpi_row, LV_ALIGN_BOTTOM_MID, 0, -14);
    lv_obj_set_style_bg_opa(kpi_row, LV_OPA_TRANSP, 0);
    lv_obj_set_style_border_width(kpi_row, 0, 0);
    lv_obj_set_flex_flow(kpi_row, LV_FLEX_FLOW_ROW);
    lv_obj_set_flex_align(kpi_row, LV_FLEX_ALIGN_SPACE_EVENLY, LV_FLEX_ALIGN_CENTER, LV_FLEX_ALIGN_CENTER);
    next_os_common_disable_scroll(kpi_row);

    char farm_buf[4];
    char alert_buf[4];
    char irig_buf[4];
    (void)std::snprintf(farm_buf, sizeof(farm_buf), "%u",
                        static_cast<unsigned>(next_os_mesh_state_farm_count()));
    (void)std::snprintf(alert_buf, sizeof(alert_buf), "%u",
                        static_cast<unsigned>(next_os_mesh_state_alert_count()));
    (void)std::snprintf(irig_buf, sizeof(irig_buf), "%u",
                        static_cast<unsigned>(next_os_mesh_state_irig_count()));

    lv_obj_t *kpi0 = watch_face_create_kpi_tile(kpi_row, farm_buf, "FARM", next_os_color_olive(),
                                                &s_kpi_value_labels[0]);
    lv_obj_set_clickable(kpi0, true);
    lv_obj_add_event_cb(kpi0, watch_face_kpi_shortcut_cb, LV_EVENT_CLICKED, reinterpret_cast<void *>(0));
    next_os_common_create_v_separator(kpi_row);
    lv_obj_t *kpi1 = watch_face_create_kpi_tile(kpi_row, alert_buf, "ALERT", next_os_color_critical(),
                                                &s_kpi_value_labels[1]);
    lv_obj_set_clickable(kpi1, true);
    lv_obj_add_event_cb(kpi1, watch_face_kpi_shortcut_cb, LV_EVENT_CLICKED, reinterpret_cast<void *>(1));
    next_os_common_create_v_separator(kpi_row);
    lv_obj_t *kpi2 = watch_face_create_kpi_tile(kpi_row, irig_buf, "IRIG", next_os_color_clay(),
                                                &s_kpi_value_labels[2]);
    lv_obj_set_clickable(kpi2, true);
    lv_obj_add_event_cb(kpi2, watch_face_kpi_shortcut_cb, LV_EVENT_CLICKED, reinterpret_cast<void *>(2));

    s_variant_hint = lv_label_create(root);
    lv_label_set_text(s_variant_hint, s_variant == 0U ? "Classic" : "Compact");
    lv_obj_set_style_text_font(s_variant_hint, &lv_font_montserrat_12, 0);
    lv_obj_set_style_text_color(s_variant_hint, next_os_color_muted(), 0);
    lv_obj_align(s_variant_hint, LV_ALIGN_TOP_MID, 0, nextos_status_header_y() - 12);

    watch_face_refresh_clock();
    next_os_watch_face_refresh_from_mesh();
    s_clock_timer = lv_timer_create(watch_face_timer_cb, 1000, nullptr);
}

static void watch_face_long_press_cb(lv_timer_t *timer) {
    (void)timer;
    s_long_press_timer = nullptr;
    if (!next_os_nav_stack_is_ready()) {
        return;
    }
    nextos_haptic_pulse(NEXTOS_HAPTIC_MEDIUM);
    next_os_nav_stack_push(NEXT_OS_SCREEN_APP_LAUNCHER, true);
}

static void watch_face_kpi_shortcut_cb(lv_event_t *event) {
    if (lv_event_get_code(event) != LV_EVENT_CLICKED) {
        return;
    }
    if (!next_os_nav_stack_is_ready()) {
        return;
    }
    const auto slot = static_cast<int>(reinterpret_cast<intptr_t>(lv_event_get_user_data(event)));
    if (slot == 0) {
        next_os_nav_stack_push(NEXT_OS_SCREEN_FARMING_HUB, true);
    } else if (slot == 1) {
        next_os_screen_manager_show_notification_center();
    } else if (slot == 2) {
        next_os_nav_stack_push(NEXT_OS_SCREEN_FARMING_IRRIGATION, true);
    }
}

static void watch_face_pointer_cb(lv_event_t *event) {
    const lv_event_code_t code = lv_event_get_code(event);
    lv_indev_t *indev = lv_event_get_indev(event);
    if (indev == nullptr) {
        return;
    }
    lv_point_t pt {};
    lv_indev_get_point(indev, &pt);
    if (code == LV_EVENT_PRESSED) {
        s_press_y = pt.y;
        if (s_long_press_timer != nullptr) {
            lv_timer_delete(s_long_press_timer);
        }
        s_long_press_timer = lv_timer_create(watch_face_long_press_cb, 3000, nullptr);
        lv_timer_set_repeat_count(s_long_press_timer, 1);
        return;
    }
    if (code == LV_EVENT_RELEASED || code == LV_EVENT_PRESS_LOST) {
        if (s_long_press_timer != nullptr) {
            lv_timer_delete(s_long_press_timer);
            s_long_press_timer = nullptr;
        }
        const int32_t delta = pt.y - s_press_y;
        if (delta < -50) {
            nextos_haptic_pulse(NEXTOS_HAPTIC_LIGHT);
            next_os_screen_manager_show_control_center();
        } else if (delta > 50) {
            nextos_haptic_pulse(NEXTOS_HAPTIC_LIGHT);
            next_os_screen_manager_show_notification_center();
        }
    }
}

void next_os_watch_face_install_input(lv_obj_t *root) {
    lv_obj_add_event_cb(root, watch_face_pointer_cb, LV_EVENT_PRESSED, nullptr);
    lv_obj_add_event_cb(root, watch_face_pointer_cb, LV_EVENT_RELEASED, nullptr);
    lv_obj_add_event_cb(root, watch_face_pointer_cb, LV_EVENT_PRESS_LOST, nullptr);
}

void next_os_watch_face_variant_next(void) {
    s_variant = static_cast<uint8_t>((s_variant + 1U) % 2U);
    next_os_screen_manager_reload_current();
}

void next_os_watch_face_variant_prev(void) {
    s_variant = static_cast<uint8_t>((s_variant + 1U) % 2U);
    next_os_screen_manager_reload_current();
}
