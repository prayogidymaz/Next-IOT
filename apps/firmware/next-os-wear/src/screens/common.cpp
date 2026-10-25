#include "screens/common.h"

#include "screens/screen_manager.h"

#include <cstdint>

/** Drag manual — SDL mouse tidak mengirim LV_EVENT_GESTURE */
static int32_t s_drag_start_x = 0;
static bool s_drag_active = false;

static void enable_swipe_event_bubble(lv_obj_t *obj) {
    const uint32_t count = lv_obj_get_child_count(obj);
    for (uint32_t i = 0; i < count; i++) {
        lv_obj_t *child = lv_obj_get_child(obj, i);
        if (!lv_obj_has_flag(child, LV_OBJ_FLAG_CLICKABLE)) {
            lv_obj_add_flag(child, LV_OBJ_FLAG_EVENT_BUBBLE);
        }
        enable_swipe_event_bubble(child);
    }
}

static void swipe_pressed_cb(lv_event_t *event) {
    lv_indev_t *indev = lv_event_get_indev(event);
    if (indev == nullptr) {
        return;
    }
    lv_point_t p;
    lv_indev_get_point(indev, &p);
    s_drag_start_x = p.x;
    s_drag_active = true;
}

static void swipe_released_cb(lv_event_t *event) {
    if (!s_drag_active) {
        return;
    }
    lv_indev_t *indev = lv_event_get_indev(event);
    if (indev == nullptr) {
        s_drag_active = false;
        return;
    }
    lv_point_t p;
    lv_indev_get_point(indev, &p);
    const int32_t delta_x = p.x - s_drag_start_x;
    s_drag_active = false;

    constexpr int32_t k_swipe_threshold = 40;
    if (delta_x < -k_swipe_threshold) {
        next_os_screen_manager_next();
    } else if (delta_x > k_swipe_threshold) {
        next_os_screen_manager_prev();
    }
}

void next_os_common_disable_scroll(lv_obj_t *obj) {
    lv_obj_set_scrollbar_mode(obj, LV_SCROLLBAR_MODE_OFF);
    lv_obj_set_scrollable(obj, false);
}

void next_os_common_attach_swipe_navigation(lv_obj_t *screen) {
    enable_swipe_event_bubble(screen);
    lv_obj_set_clickable(screen, true);
    lv_obj_add_event_cb(screen, swipe_pressed_cb, LV_EVENT_PRESSED, nullptr);
    lv_obj_add_event_cb(screen, swipe_released_cb, LV_EVENT_RELEASED, nullptr);
}

lv_obj_t *next_os_common_create_header_label(lv_obj_t *parent, const char *text) {
    lv_obj_t *label = lv_label_create(parent);
    lv_label_set_text(label, text);
    lv_obj_set_style_text_font(label, &lv_font_montserrat_12, 0);
    lv_obj_set_style_text_color(label, next_os_color_olive(), 0);
    lv_obj_align(label, LV_ALIGN_TOP_MID, 0, NEXT_OS_SCREEN_SAFE_TOP);
    return label;
}

lv_obj_t *next_os_common_create_round_container(lv_obj_t *parent, int32_t size) {
    lv_obj_t *box = lv_obj_create(parent);
    lv_obj_set_size(box, size, size);
    lv_obj_set_style_radius(box, LV_RADIUS_CIRCLE, 0);
    lv_obj_set_style_bg_color(box, next_os_color_cream(), 0);
    lv_obj_set_style_border_color(box, next_os_color_olive(), 0);
    lv_obj_set_style_border_width(box, 2, 0);
    lv_obj_set_style_pad_all(box, 0, 0);
    next_os_common_disable_scroll(box);
    return box;
}

lv_obj_t *next_os_common_create_v_separator(lv_obj_t *parent) {
    lv_obj_t *sep = lv_obj_create(parent);
    lv_obj_set_size(sep, 1, 28);
    lv_obj_set_style_bg_color(sep, next_os_color_separator(), 0);
    lv_obj_set_style_border_width(sep, 0, 0);
    lv_obj_set_style_radius(sep, 0, 0);
    next_os_common_disable_scroll(sep);
    return sep;
}

void next_os_common_create_pagination_dots(lv_obj_t *parent, uint8_t dot_count, uint8_t active_index) {
    lv_obj_t *row = lv_obj_create(parent);
    lv_obj_set_size(row, LV_SIZE_CONTENT, LV_SIZE_CONTENT);
    lv_obj_set_style_bg_opa(row, LV_OPA_TRANSP, 0);
    lv_obj_set_style_border_width(row, 0, 0);
    lv_obj_set_style_pad_column(row, 8, 0);
    lv_obj_set_flex_flow(row, LV_FLEX_FLOW_ROW);
    lv_obj_set_flex_align(row, LV_FLEX_ALIGN_CENTER, LV_FLEX_ALIGN_CENTER, LV_FLEX_ALIGN_CENTER);
    lv_obj_align(row, LV_ALIGN_BOTTOM_MID, 0, -10);
    next_os_common_disable_scroll(row);

    for (uint8_t i = 0; i < dot_count; i++) {
        lv_obj_t *dot = lv_obj_create(row);
        lv_obj_set_size(dot, 8, 8);
        lv_obj_set_style_radius(dot, LV_RADIUS_CIRCLE, 0);
        next_os_common_disable_scroll(dot);
        if (i == active_index) {
            lv_obj_set_style_bg_color(dot, next_os_color_olive(), 0);
        } else {
            lv_obj_set_style_bg_color(dot, next_os_color_light_grey(), 0);
        }
    }
}
