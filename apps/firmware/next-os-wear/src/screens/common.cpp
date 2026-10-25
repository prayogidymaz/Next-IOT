#include "screens/common.h"

#include "screens/screen_manager.h"

#include <cstdint>

static lv_point_t s_swipe_start;
static bool s_swipe_tracking = false;

static void swipe_nav_event_cb(lv_event_t *event) {
    const lv_event_code_t code = lv_event_get_code(event);

    if (code == LV_EVENT_PRESSED) {
        lv_indev_t *indev = lv_indev_active();
        if (indev != nullptr) {
            lv_indev_get_point(indev, &s_swipe_start);
            s_swipe_tracking = true;
        }
        return;
    }

    if (code == LV_EVENT_GESTURE) {
        lv_indev_t *indev = lv_indev_active();
        if (indev == nullptr) {
            return;
        }
        const lv_dir_t dir = lv_indev_get_gesture_dir(indev);
        if (dir == LV_DIR_LEFT) {
            next_os_screen_manager_next();
        } else if (dir == LV_DIR_RIGHT) {
            next_os_screen_manager_prev();
        }
        return;
    }

    if (code == LV_EVENT_RELEASED && s_swipe_tracking) {
        s_swipe_tracking = false;
        lv_point_t end_pt;
        lv_indev_t *indev = lv_indev_active();
        if (indev == nullptr) {
            return;
        }
        lv_indev_get_point(indev, &end_pt);
        const int32_t dx = end_pt.x - s_swipe_start.x;
        constexpr int32_t k_swipe_threshold = 36;
        if (dx < -k_swipe_threshold) {
            next_os_screen_manager_next();
        } else if (dx > k_swipe_threshold) {
            next_os_screen_manager_prev();
        }
    }
}

void next_os_common_disable_scroll(lv_obj_t *obj) {
    lv_obj_set_scrollbar_mode(obj, LV_SCROLLBAR_MODE_OFF);
    lv_obj_set_scrollable(obj, false);
}

void next_os_common_attach_swipe_navigation(lv_obj_t *screen) {
    lv_obj_set_clickable(screen, true);
    lv_obj_add_event_cb(screen, swipe_nav_event_cb, LV_EVENT_ALL, nullptr);
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
