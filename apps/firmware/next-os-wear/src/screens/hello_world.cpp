#include "screens/hello_world.h"

#include "config.h"
#include "theme.h"

static lv_obj_t *s_hour_hand = nullptr;
static lv_obj_t *s_min_hand = nullptr;
static lv_obj_t *s_clock_face = nullptr;

void next_os_hello_world_screen_create(lv_obj_t *root) {
    next_os_apply_screen_style(root);

    lv_obj_t *header = lv_label_create(root);
    lv_label_set_text(header, "NEXT-OS WEAR v1.0.0-dev");
    lv_obj_set_style_text_color(header, next_os_color_olive(), 0);
    lv_obj_align(header, LV_ALIGN_TOP_MID, 0, 12);

    s_clock_face = lv_obj_create(root);
    lv_obj_set_size(s_clock_face, 140, 140);
    lv_obj_set_style_radius(s_clock_face, LV_RADIUS_CIRCLE, 0);
    lv_obj_set_style_bg_color(s_clock_face, next_os_color_dark(), 0);
    lv_obj_set_style_border_color(s_clock_face, next_os_color_olive(), 0);
    lv_obj_set_style_border_width(s_clock_face, 3, 0);
    lv_obj_align(s_clock_face, LV_ALIGN_CENTER, 0, 0);

    s_hour_hand = lv_line_create(s_clock_face);
    static lv_point_precise_t hour_pts[2] = {{0, 0}, {0, -35}};
    lv_line_set_points(s_hour_hand, hour_pts, 2);
    lv_obj_set_style_line_color(s_hour_hand, next_os_color_cream(), 0);
    lv_obj_set_style_line_width(s_hour_hand, 3, 0);
    lv_obj_center(s_hour_hand);

    s_min_hand = lv_line_create(s_clock_face);
    static lv_point_precise_t min_pts[2] = {{0, 0}, {0, -50}};
    lv_line_set_points(s_min_hand, min_pts, 2);
    lv_obj_set_style_line_color(s_min_hand, next_os_color_clay(), 0);
    lv_obj_set_style_line_width(s_min_hand, 2, 0);
    lv_obj_center(s_min_hand);

    lv_obj_t *kpi = lv_label_create(root);
    lv_label_set_text(kpi, "0 FARM • 0 ALERT • 0 IRIG");
    lv_obj_set_style_text_color(kpi, next_os_color_dark(), 0);
    lv_obj_align(kpi, LV_ALIGN_BOTTOM_MID, 0, -16);

    next_os_hello_world_update_clock(10, 15);
}

void next_os_hello_world_update_clock(uint8_t hour, uint8_t minute) {
    if (s_hour_hand == nullptr || s_min_hand == nullptr) {
        return;
    }
    const int32_t min_angle = static_cast<int32_t>(minute * 6);
    const int32_t hour_angle = static_cast<int32_t>((hour % 12) * 30 + minute / 2);
    lv_obj_set_style_transform_angle(s_min_hand, min_angle * 10, 0);
    lv_obj_set_style_transform_angle(s_hour_hand, hour_angle * 10, 0);
    lv_obj_set_style_transform_pivot_x(s_min_hand, 0, 0);
    lv_obj_set_style_transform_pivot_y(s_min_hand, 0, 0);
    lv_obj_set_style_transform_pivot_x(s_hour_hand, 0, 0);
    lv_obj_set_style_transform_pivot_y(s_hour_hand, 0, 0);
}
