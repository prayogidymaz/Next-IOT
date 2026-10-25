#include "screens/hello_world.h"

#include "config.h"
#include "theme.h"

#include <cstdio>

static lv_obj_t *s_time_label = nullptr;

static void next_os_clock_format(char *buf, size_t buf_len, uint8_t hour, uint8_t minute) {
    (void)std::snprintf(buf, buf_len, "%02u:%02u", static_cast<unsigned>(hour % 24U),
                        static_cast<unsigned>(minute % 60U));
}

void next_os_hello_world_screen_create(lv_obj_t *root) {
    next_os_apply_screen_style(root);

    lv_obj_t *header = lv_label_create(root);
    lv_label_set_text(header, "NEXT-OS WEAR v1.0.0-dev");
    lv_obj_set_style_text_color(header, next_os_color_olive(), 0);
    lv_obj_align(header, LV_ALIGN_TOP_MID, 0, 12);

    lv_obj_t *clock_face = lv_obj_create(root);
    lv_obj_set_size(clock_face, 140, 140);
    lv_obj_set_style_radius(clock_face, LV_RADIUS_CIRCLE, 0);
    lv_obj_set_style_bg_color(clock_face, next_os_color_dark(), 0);
    lv_obj_set_style_border_color(clock_face, next_os_color_olive(), 0);
    lv_obj_set_style_border_width(clock_face, 3, 0);
    lv_obj_align(clock_face, LV_ALIGN_CENTER, 0, 0);

    /* Jarum analog statis (placeholder) — update dinamis pakai label (lv_line tick crash LVGL 9.6) */
    lv_obj_t *hour_hand = lv_line_create(clock_face);
    static lv_point_precise_t hour_pts[2] = {{0, 8}, {0, -32}};
    lv_line_set_points(hour_hand, hour_pts, 2);
    lv_obj_set_style_line_color(hour_hand, next_os_color_cream(), 0);
    lv_obj_set_style_line_width(hour_hand, 3, 0);
    lv_obj_center(hour_hand);

    lv_obj_t *min_hand = lv_line_create(clock_face);
    static lv_point_precise_t min_pts[2] = {{0, 10}, {0, -45}};
    lv_line_set_points(min_hand, min_pts, 2);
    lv_obj_set_style_line_color(min_hand, next_os_color_clay(), 0);
    lv_obj_set_style_line_width(min_hand, 2, 0);
    lv_obj_center(min_hand);

    s_time_label = lv_label_create(clock_face);
    lv_obj_set_style_text_color(s_time_label, next_os_color_cream(), 0);
    lv_obj_align(s_time_label, LV_ALIGN_BOTTOM_MID, 0, -18);

    lv_obj_t *kpi = lv_label_create(root);
    lv_label_set_text(kpi, "0 FARM • 0 ALERT • 0 IRIG");
    lv_obj_set_style_text_color(kpi, next_os_color_dark(), 0);
    lv_obj_align(kpi, LV_ALIGN_BOTTOM_MID, 0, -16);

    next_os_hello_world_update_clock(10, 15);
}

void next_os_hello_world_update_clock(uint8_t hour, uint8_t minute) {
    if (s_time_label == nullptr || !lv_obj_is_in_widget_tree(s_time_label)) {
        return;
    }
    char buf[8];
    next_os_clock_format(buf, sizeof(buf), hour, minute);
    lv_label_set_text(s_time_label, buf);
}
