#include "screens/overlays/notification_center.h"

#include "haptic.h"
#include "layout.h"
#include "mesh_state.h"
#include "navigation/nav_stack.h"
#include "theme.h"

static next_os_overlay_dismiss_fn s_dismiss = nullptr;

static void notif_dismiss_cb(lv_event_t *event) {
    if (lv_event_get_code(event) != LV_EVENT_CLICKED) {
        return;
    }
    if (s_dismiss != nullptr) {
        s_dismiss();
    }
}

static void notif_open_alert_cb(lv_event_t *event) {
    if (lv_event_get_code(event) != LV_EVENT_CLICKED) {
        return;
    }
    if (s_dismiss != nullptr) {
        s_dismiss();
    }
    next_os_nav_stack_push(NEXT_OS_SCREEN_ALERT_CENTER, true);
}

void next_os_notification_center_show(lv_obj_t *parent, next_os_overlay_dismiss_fn on_dismiss) {
    s_dismiss = on_dismiss;
    lv_obj_set_size(parent, NEXTOS_W, NEXTOS_H);
    lv_obj_set_style_bg_color(parent, NEXTOS_TEXT_PRIMARY, 0);
    lv_obj_set_style_bg_opa(parent, LV_OPA_50, 0);

    lv_obj_t *panel = lv_obj_create(parent);
    lv_obj_set_size(panel, NEXTOS_W, NEXTOS_IS_ROUND ? 170 : 220);
    lv_obj_align(panel, LV_ALIGN_BOTTOM_MID, 0, 0);
    lv_obj_set_style_bg_color(panel, NEXTOS_SURFACE, 0);

    lv_obj_t *list = lv_obj_create(panel);
    lv_obj_set_size(list, nextos_content_width(), NEXTOS_IS_ROUND ? 130 : 180);
    lv_obj_align(list, LV_ALIGN_TOP_MID, 0, 8);
    lv_obj_set_flex_flow(list, LV_FLEX_FLOW_COLUMN);
    lv_obj_set_style_pad_row(list, 6, 0);
    lv_obj_set_scroll_dir(list, LV_DIR_VER);

    const uint8_t count = next_os_mesh_state_alert_buffer_size();
    if (count == 0U) {
        lv_obj_t *empty = lv_label_create(list);
        lv_label_set_text(empty, "No alerts");
    } else {
        for (uint8_t i = 0; i < count && i < 6U; i++) {
            next_os_mesh_alert_t alert {};
            if (!next_os_mesh_state_alert_at(i, &alert)) {
                continue;
            }
            lv_obj_t *row = lv_button_create(list);
            lv_obj_set_width(row, nextos_content_width());
            lv_obj_set_height(row, 44);
            lv_obj_add_event_cb(row, notif_open_alert_cb, LV_EVENT_CLICKED, nullptr);
            lv_obj_t *title = lv_label_create(row);
            lv_label_set_text(title, alert.title);
            lv_obj_align(title, LV_ALIGN_LEFT_MID, 8, -6);
            lv_obj_t *meta = lv_label_create(row);
            lv_label_set_text(meta, alert.ago);
            lv_obj_set_style_text_font(meta, &lv_font_montserrat_12, 0);
            lv_obj_align(meta, LV_ALIGN_LEFT_MID, 8, 8);
        }
    }

    lv_obj_add_event_cb(parent, notif_dismiss_cb, LV_EVENT_CLICKED, nullptr);
    nextos_haptic_pulse(NEXTOS_HAPTIC_LIGHT);
}
