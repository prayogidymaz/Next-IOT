#include "screens/qr_pair.h"

#include "audio.h"
#include "config.h"
#include "haptic.h"
#include "layout.h"
#include "screens/common.h"
#include "theme.h"

#include <cstdio>
#include <cstring>

static next_os_qr_pair_dismiss_fn s_on_dismiss = nullptr;
static lv_timer_t *s_expire_timer = nullptr;
static lv_timer_t *s_sim_pair_timer = nullptr;
static lv_obj_t *s_countdown_label = nullptr;
static int32_t s_seconds_left = 120;

static void qr_pair_cleanup_timers(void) {
    if (s_expire_timer != nullptr) {
        lv_timer_delete(s_expire_timer);
        s_expire_timer = nullptr;
    }
    if (s_sim_pair_timer != nullptr) {
        lv_timer_delete(s_sim_pair_timer);
        s_sim_pair_timer = nullptr;
    }
    s_countdown_label = nullptr;
}

static void qr_pair_finish(void) {
    qr_pair_cleanup_timers();
    if (s_on_dismiss != nullptr) {
        s_on_dismiss();
    }
}

static void qr_pair_tick_cb(lv_timer_t *timer) {
    (void)timer;
    s_seconds_left--;
    if (nextos_ui_obj_alive(s_countdown_label)) {
        char buf[16];
        (void)std::snprintf(buf, sizeof(buf), "%lds", static_cast<long>(s_seconds_left));
        lv_label_set_text(s_countdown_label, buf);
    }
    if (s_seconds_left <= 0) {
        qr_pair_finish();
    }
}

static void qr_pair_second_pulse_cb(lv_timer_t *timer) {
    (void)timer;
    nextos_haptic_pulse(NEXTOS_HAPTIC_MEDIUM);
}

static void qr_pair_sim_success_cb(lv_timer_t *timer) {
    (void)timer;
    (void)std::printf("[QR PAIR] simulator auto-success token stored (mock)\n");
    nextos_haptic_pulse(NEXTOS_HAPTIC_MEDIUM);
    lv_timer_create(qr_pair_second_pulse_cb, 150, nullptr);
    nextos_audio_beep(NEXTOS_BEEP_SUCCESS);
    qr_pair_finish();
}

static void qr_pair_overlay_delete_cb(lv_event_t *event) {
    if (lv_event_get_code(event) != LV_EVENT_DELETE) {
        return;
    }
    qr_pair_cleanup_timers();
}

static void qr_pair_cancel_cb(lv_event_t *event) {
    if (lv_event_get_code(event) != LV_EVENT_CLICKED) {
        return;
    }
    qr_pair_finish();
}

static void qr_pair_draw_matrix(lv_obj_t *parent) {
    lv_obj_t *grid = lv_obj_create(parent);
    const int32_t grid_size = NEXTOS_IS_ROUND ? 140 : 160;
    lv_obj_set_size(grid, grid_size, grid_size);
    lv_obj_center(grid);
    lv_obj_set_style_bg_color(grid, next_os_color_cream(), 0);
    lv_obj_set_style_pad_all(grid, 6, 0);
    lv_obj_set_style_pad_row(grid, 2, 0);
    lv_obj_set_style_pad_column(grid, 2, 0);
    lv_obj_set_flex_flow(grid, LV_FLEX_FLOW_ROW_WRAP);
    lv_obj_set_flex_align(grid, LV_FLEX_ALIGN_START, LV_FLEX_ALIGN_START, LV_FLEX_ALIGN_START);

    for (int i = 0; i < 21 * 21; i++) {
        lv_obj_t *dot = lv_obj_create(grid);
        lv_obj_set_size(dot, 4, 4);
        const bool on = (i % 7 != 0) && ((i + static_cast<int>(NEXT_OS_DEVICE_ID[0])) % 5 != 0);
        lv_obj_set_style_bg_color(dot, on ? next_os_color_dark() : next_os_color_cream(), 0);
        lv_obj_set_style_border_width(dot, 0, 0);
    }
}

void next_os_qr_pair_show(lv_obj_t *overlay, next_os_qr_pair_dismiss_fn on_dismiss) {
    s_on_dismiss = on_dismiss;
    s_seconds_left = 120;
    qr_pair_cleanup_timers();
    next_os_apply_screen_style(overlay);
    lv_obj_set_size(overlay, NEXTOS_W, NEXTOS_H);
    lv_obj_add_event_cb(overlay, qr_pair_overlay_delete_cb, LV_EVENT_DELETE, nullptr);
    lv_obj_center(overlay);
    lv_obj_set_style_bg_opa(overlay, LV_OPA_90, 0);

    lv_obj_t *cancel = lv_button_create(overlay);
    lv_obj_set_size(cancel, 64, 28);
    lv_obj_align(cancel, LV_ALIGN_TOP_LEFT, nextos_safe_padding_side(), nextos_safe_padding_top());
    lv_obj_add_event_cb(cancel, qr_pair_cancel_cb, LV_EVENT_CLICKED, nullptr);
    lv_obj_t *cl = lv_label_create(cancel);
    lv_label_set_text(cl, LV_SYMBOL_LEFT " Cancel");
    lv_obj_center(cl);

    s_countdown_label = lv_label_create(overlay);
    lv_label_set_text(s_countdown_label, "120s");
    lv_obj_align(s_countdown_label, LV_ALIGN_TOP_RIGHT, -nextos_safe_padding_side(),
                 nextos_safe_padding_top());

    qr_pair_draw_matrix(overlay);

    lv_obj_t *hint = lv_label_create(overlay);
    lv_label_set_text(hint, "Scan QR dengan Next-IOT mobile app");
    lv_obj_set_style_text_font(hint, &lv_font_montserrat_12, 0);
    lv_obj_set_style_text_color(hint, next_os_color_olive(), 0);
    lv_obj_align(hint, LV_ALIGN_BOTTOM_MID, 0, -nextos_safe_padding_bottom() - 8);

    char dev[48];
    (void)std::snprintf(dev, sizeof(dev), "device: %s", NEXT_OS_DEVICE_ID);
    lv_obj_t *dev_l = lv_label_create(overlay);
    lv_label_set_text(dev_l, dev);
    lv_obj_set_style_text_color(dev_l, next_os_color_muted(), 0);
    lv_obj_align(dev_l, LV_ALIGN_BOTTOM_MID, 0, -nextos_safe_padding_bottom());

    s_expire_timer = lv_timer_create(qr_pair_tick_cb, 1000, nullptr);
#if defined(SIMULATOR) || defined(NEXT_OS_SIMULATOR)
    s_sim_pair_timer = lv_timer_create(qr_pair_sim_success_cb, 10000, nullptr);
#endif
}
