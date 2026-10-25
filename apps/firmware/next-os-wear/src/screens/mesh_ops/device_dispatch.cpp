#include "screens/mesh_ops/device_dispatch.h"

#include "haptic.h"
#include "layout.h"
#include "screens/common.h"
#include "theme.h"

#include <cstdio>

static void dispatch_btn_cb(lv_event_t *event) {
    if (lv_event_get_code(event) != LV_EVENT_CLICKED) {
        return;
    }
    nextos_haptic_pulse(NEXTOS_HAPTIC_LIGHT);
    lv_obj_t *btn = static_cast<lv_obj_t *>(lv_event_get_target(event));
    lv_obj_set_style_bg_color(btn, NEXTOS_ACCENT_SECONDARY, 0);
    (void)std::printf("[MESH] dispatch_requested (simulator mock)\n");
}

void next_os_device_dispatch_create(lv_obj_t *root) {
    next_os_apply_screen_style(root);
    next_os_common_create_header_label(root, "Device Dispatch");

    const char *labels[] = {"Drone fly_to", "Capture NDVI", "Sprayer ON", "Gate lock"};
    lv_obj_t *list = lv_obj_create(root);
    lv_obj_set_size(list, nextos_content_width(), NEXTOS_IS_ROUND ? 160 : 220);
    lv_obj_align(list, LV_ALIGN_CENTER, 0, 12);
    lv_obj_set_style_bg_opa(list, LV_OPA_TRANSP, 0);
    lv_obj_set_style_border_width(list, 0, 0);
    lv_obj_set_flex_flow(list, LV_FLEX_FLOW_COLUMN);
    lv_obj_set_style_pad_row(list, 8, 0);
    next_os_common_disable_scroll(list);

    for (size_t i = 0; i < sizeof(labels) / sizeof(labels[0]); i++) {
        lv_obj_t *btn = lv_button_create(list);
        lv_obj_set_width(btn, nextos_content_width());
        lv_obj_set_height(btn, 36);
        lv_obj_set_style_bg_color(btn, NEXTOS_SURFACE, 0);
        lv_obj_set_style_border_color(btn, NEXTOS_BORDER, 0);
        lv_obj_set_style_border_width(btn, 1, 0);
        lv_obj_add_event_cb(btn, dispatch_btn_cb, LV_EVENT_CLICKED, nullptr);
        lv_obj_t *lbl = lv_label_create(btn);
        lv_label_set_text(lbl, labels[i]);
        lv_obj_center(lbl);
    }
}
