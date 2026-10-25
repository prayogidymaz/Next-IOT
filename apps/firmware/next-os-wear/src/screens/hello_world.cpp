#include "screens/hello_world.h"

#include "config.h"
#include "theme.h"

#include <cmath>

static lv_obj_t *s_hour_hand = nullptr;
static lv_obj_t *s_min_hand = nullptr;
static lv_point_precise_t s_hour_pts[2];
static lv_point_precise_t s_min_pts[2];

static void next_os_clock_set_hand_points(lv_point_precise_t *pts, int32_t angle_deg, int32_t length) {
    const double rad = static_cast<double>(angle_deg) * M_PI / 180.0;
    pts[0].x = 0;
    pts[0].y = 0;
    pts[1].x = static_cast<lv_value_precise_t>(std::sin(rad) * static_cast<double>(length));
    pts[1].y = static_cast<lv_value_precise_t>(-std::cos(rad) * static_cast<double>(length));
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

    s_hour_hand = lv_line_create(clock_face);
    lv_obj_set_style_line_color(s_hour_hand, next_os_color_cream(), 0);
    lv_obj_set_style_line_width(s_hour_hand, 3, 0);
    lv_obj_center(s_hour_hand);

    s_min_hand = lv_line_create(clock_face);
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
    if (!lv_obj_is_in_widget_tree(s_hour_hand) || !lv_obj_is_in_widget_tree(s_min_hand)) {
        return;
    }

    const int32_t min_angle = static_cast<int32_t>(minute * 6);
    const int32_t hour_angle = static_cast<int32_t>((hour % 12) * 30 + minute / 2);

    next_os_clock_set_hand_points(s_hour_pts, hour_angle, 35);
    lv_line_set_points(s_hour_hand, s_hour_pts, 2);

    next_os_clock_set_hand_points(s_min_pts, min_angle, 50);
    lv_line_set_points(s_min_hand, s_min_pts, 2);

    lv_obj_invalidate(s_hour_hand);
    lv_obj_invalidate(s_min_hand);
}
