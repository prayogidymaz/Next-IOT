#include "screens/apps/timer_app.h"

#include "layout.h"
#include "screens/common.h"
#include "theme.h"

#include <cstdio>

static lv_obj_t *s_display = nullptr;
static lv_timer_t *s_tick = nullptr;
static int32_t s_seconds = 300;
static bool s_running = false;

static void timer_refresh_label(void) {
    if (!nextos_ui_obj_alive(s_display)) {
        return;
    }
    const int32_t mm = s_seconds / 60;
    const int32_t ss = s_seconds % 60;
    char buf[16];
    (void)std::snprintf(buf, sizeof(buf), "%02ld:%02ld", static_cast<long>(mm), static_cast<long>(ss));
    lv_label_set_text(s_display, buf);
}

static void timer_tick_cb(lv_timer_t *timer) {
    (void)timer;
    if (!nextos_ui_obj_alive(s_display)) {
        return;
    }
    if (!s_running || s_seconds <= 0) {
        return;
    }
    s_seconds--;
    timer_refresh_label();
}

static void timer_btn_cb(lv_event_t *event) {
    const auto action = static_cast<int>(reinterpret_cast<intptr_t>(lv_event_get_user_data(event)));
    if (action == 0) {
        s_running = !s_running;
    } else if (action == 1) {
        s_running = false;
        s_seconds = 300;
    } else {
        s_seconds = action;
        s_running = false;
        timer_refresh_label();
    }
    timer_refresh_label();
}

void next_os_timer_app_dispose(void) {
    if (s_tick != nullptr) {
        lv_timer_delete(s_tick);
        s_tick = nullptr;
    }
    s_display = nullptr;
}

static void timer_on_delete(lv_event_t *event) {
    if (lv_event_get_code(event) != LV_EVENT_DELETE) {
        return;
    }
    next_os_timer_app_dispose();
}

void next_os_timer_app_create(lv_obj_t *root) {
    next_os_timer_app_dispose();
    next_os_apply_screen_style(root);
    lv_obj_add_event_cb(root, timer_on_delete, LV_EVENT_DELETE, nullptr);
    next_os_common_create_header_label(root, "Timer");

    s_display = lv_label_create(root);
    lv_obj_set_style_text_font(s_display, &lv_font_montserrat_48, 0);
    lv_obj_align(s_display, LV_ALIGN_CENTER, 0, -20);
    timer_refresh_label();

    lv_obj_t *row = lv_obj_create(root);
    lv_obj_set_size(row, nextos_content_width(), 40);
    lv_obj_align(row, LV_ALIGN_BOTTOM_MID, 0, -60);
    lv_obj_set_style_bg_opa(row, LV_OPA_TRANSP, 0);
    lv_obj_set_style_border_width(row, 0, 0);
    lv_obj_set_flex_flow(row, LV_FLEX_FLOW_ROW);
    lv_obj_set_style_pad_column(row, 6, 0);
    next_os_common_disable_scroll(row);

    const char *presets[] = {"1m", "5m", "10m", "25m"};
    const int preset_sec[] = {60, 300, 600, 1500};
    for (int i = 0; i < 4; i++) {
        lv_obj_t *btn = lv_button_create(row);
        lv_obj_add_event_cb(btn, timer_btn_cb, LV_EVENT_CLICKED,
                            reinterpret_cast<void *>(static_cast<intptr_t>(preset_sec[i])));
        lv_obj_t *lbl = lv_label_create(btn);
        lv_label_set_text(lbl, presets[i]);
        lv_obj_center(lbl);
    }

    lv_obj_t *start = lv_button_create(root);
    lv_obj_align(start, LV_ALIGN_BOTTOM_MID, -40, -16);
    lv_obj_add_event_cb(start, timer_btn_cb, LV_EVENT_CLICKED, reinterpret_cast<void *>(0));
    lv_label_set_text(lv_label_create(start), "Start");

    lv_obj_t *reset = lv_button_create(root);
    lv_obj_align(reset, LV_ALIGN_BOTTOM_MID, 40, -16);
    lv_obj_add_event_cb(reset, timer_btn_cb, LV_EVENT_CLICKED, reinterpret_cast<void *>(1));
    lv_label_set_text(lv_label_create(reset), "Reset");

    s_tick = lv_timer_create(timer_tick_cb, 1000, nullptr);
}
