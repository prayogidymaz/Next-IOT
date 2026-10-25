#include "screens/apps/flashlight_app.h"

#include "layout.h"
#include "navigation/nav_stack.h"
#include "theme.h"

static void flashlight_tap_cb(lv_event_t *event) {
    if (lv_event_get_code(event) != LV_EVENT_CLICKED) {
        return;
    }
    next_os_nav_stack_pop();
}

void next_os_flashlight_app_create(lv_obj_t *root) {
    lv_obj_set_size(root, NEXTOS_W, NEXTOS_H);
    lv_obj_set_style_bg_color(root, lv_color_hex(0xFFFFFF), 0);
    lv_obj_set_style_bg_opa(root, LV_OPA_COVER, 0);
    lv_obj_add_event_cb(root, flashlight_tap_cb, LV_EVENT_CLICKED, nullptr);

    lv_obj_t *hint = lv_label_create(root);
    lv_label_set_text(hint, "Tap to exit");
    lv_obj_set_style_text_color(hint, lv_color_hex(0x333333), 0);
    lv_obj_align(hint, LV_ALIGN_BOTTOM_MID, 0, -20);
}
