#include "screens/common.h"

#include "layout.h"
#include "screens/screen_manager.h"

#include <cmath>
#include <cstdint>

static void nav_btn_apply_default(lv_obj_t *btn, lv_obj_t *icon) {
    lv_obj_set_style_bg_opa(btn, LV_OPA_TRANSP, 0);
    if (icon != nullptr) {
        lv_obj_set_style_text_color(icon, next_os_color_olive(), 0);
    }
}

static void nav_btn_event_cb(lv_event_t *event) {
    lv_obj_t *btn = static_cast<lv_obj_t *>(lv_event_get_current_target(event));
    lv_obj_t *icon = lv_obj_get_child(btn, 0);
    const lv_event_code_t code = lv_event_get_code(event);
    const auto dir = reinterpret_cast<intptr_t>(lv_event_get_user_data(event));

    if (code == LV_EVENT_PRESSED) {
        lv_obj_set_style_bg_color(btn, next_os_color_olive(), 0);
        lv_obj_set_style_bg_opa(btn, LV_OPA_COVER, 0);
        if (icon != nullptr) {
            lv_obj_set_style_text_color(icon, next_os_color_cream(), 0);
        }
        return;
    }
    if (code == LV_EVENT_RELEASED || code == LV_EVENT_PRESS_LOST) {
        nav_btn_apply_default(btn, icon);
        return;
    }
    if (code == LV_EVENT_CLICKED) {
        if (dir == 0) {
            next_os_screen_manager_prev();
        } else {
            next_os_screen_manager_next();
        }
    }
}

static lv_obj_t *nav_btn_create(lv_obj_t *screen, bool is_prev) {
    lv_obj_t *btn = lv_button_create(screen);
    lv_obj_set_size(btn, 28, 28);
    lv_obj_set_style_radius(btn, LV_RADIUS_CIRCLE, 0);
    lv_obj_set_style_bg_opa(btn, LV_OPA_TRANSP, 0);
    lv_obj_set_style_border_color(btn, next_os_color_olive(), 0);
    lv_obj_set_style_border_width(btn, 1, 0);
    lv_obj_set_style_shadow_width(btn, 0, 0);
    lv_obj_set_style_pad_all(btn, 0, 0);
    next_os_common_disable_scroll(btn);

    lv_obj_t *icon = lv_label_create(btn);
    lv_label_set_text(icon, is_prev ? LV_SYMBOL_LEFT : LV_SYMBOL_RIGHT);
    lv_obj_set_style_text_font(icon, &lv_font_montserrat_12, 0);
    lv_obj_set_style_text_color(icon, next_os_color_olive(), 0);
    lv_obj_center(icon);

    const intptr_t dir = is_prev ? 0 : 1;
    lv_obj_add_event_cb(btn, nav_btn_event_cb, LV_EVENT_ALL, reinterpret_cast<void *>(dir));
    return btn;
}

static void nav_place_button(lv_obj_t *btn, bool is_prev) {
    const int32_t size = nextos_nav_button_size();
    if (NEXTOS_IS_ROUND) {
        const float cx = static_cast<float>(NEXTOS_W) * 0.5F;
        const float cy = static_cast<float>(NEXTOS_H) * 0.5F;
        const float radius = static_cast<float>(NEXTOS_W) * 0.5F - 20.0F;
        const float deg = is_prev ? 135.0F : 45.0F;
        const float rad = deg * 3.14159265F / 180.0F;
        const int32_t x = static_cast<int32_t>(cx + radius * std::cos(rad) - static_cast<float>(size) * 0.5F);
        const int32_t y = static_cast<int32_t>(cy - radius * std::sin(rad) - static_cast<float>(size) * 0.5F);
        lv_obj_set_pos(btn, x, y);
        return;
    }
    if (is_prev) {
        lv_obj_align(btn, LV_ALIGN_TOP_LEFT, nextos_safe_padding_side(), nextos_safe_padding_top());
    } else {
        lv_obj_align(btn, LV_ALIGN_TOP_RIGHT, -nextos_safe_padding_side(), nextos_safe_padding_top());
    }
}

lv_obj_t *next_os_common_create_nav_buttons(lv_obj_t *screen) {
    lv_obj_t *prev_btn = nav_btn_create(screen, true);
    lv_obj_t *next_btn = nav_btn_create(screen, false);
    nav_place_button(prev_btn, true);
    nav_place_button(next_btn, false);

    lv_obj_move_foreground(prev_btn);
    lv_obj_move_foreground(next_btn);
    return prev_btn;
}

static void swipe_gesture_cb(lv_event_t *event) {
    lv_indev_t *indev = lv_event_get_indev(event);
    if (indev == nullptr) {
        return;
    }
    const lv_dir_t dir = lv_indev_get_gesture_dir(indev);
    lv_indev_wait_release(indev);

    if (dir == LV_DIR_LEFT) {
        next_os_screen_manager_next();
    } else if (dir == LV_DIR_RIGHT) {
        next_os_screen_manager_prev();
    }
}

void next_os_common_disable_scroll(lv_obj_t *obj) {
    lv_obj_set_scrollbar_mode(obj, LV_SCROLLBAR_MODE_OFF);
    lv_obj_set_scrollable(obj, false);
}

void next_os_common_attach_swipe_navigation(lv_obj_t *screen) {
    lv_obj_add_event_cb(screen, swipe_gesture_cb, LV_EVENT_GESTURE, nullptr);
}

lv_obj_t *next_os_common_create_header_label(lv_obj_t *parent, const char *text) {
    lv_obj_t *label = lv_label_create(parent);
    lv_label_set_text(label, text);
    lv_obj_set_style_text_font(label, &lv_font_montserrat_12, 0);
    lv_obj_set_style_text_color(label, next_os_color_olive(), 0);
    lv_obj_align(label, LV_ALIGN_TOP_MID, 0, NEXT_OS_SCREEN_SAFE_TOP);
    return label;
}

lv_obj_t *next_os_common_create_inset_header_row(lv_obj_t *parent, int32_t height) {
    lv_obj_t *row = lv_obj_create(parent);
    lv_obj_set_size(row, nextos_inset_header_width(), height);
    lv_obj_align(row, LV_ALIGN_TOP_MID, 0, nextos_inset_header_y());
    lv_obj_set_style_bg_opa(row, LV_OPA_TRANSP, 0);
    lv_obj_set_style_border_width(row, 0, 0);
    lv_obj_set_style_pad_all(row, 0, 0);
    next_os_common_disable_scroll(row);
    return row;
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
