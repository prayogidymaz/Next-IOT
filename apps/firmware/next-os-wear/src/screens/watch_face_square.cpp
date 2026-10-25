#include "screens/watch_face_square.h"

#include "mesh_state.h"
#include "screens/common.h"
#include "theme.h"

#include <cstdio>

static lv_obj_t *s_moist_label = nullptr;
static lv_obj_t *s_alert_badge = nullptr;
static lv_obj_t *s_spark_line_obj = nullptr;
static lv_point_precise_t s_spark_pts[8] = {{0, 20}, {8, 14}, {16, 18}, {24, 10},
                                            {32, 12}, {40, 6}, {48, 8}, {56, 4}};

static void square_on_delete(lv_event_t *event) {
    if (lv_event_get_code(event) != LV_EVENT_DELETE) {
        return;
    }
    s_moist_label = nullptr;
    s_alert_badge = nullptr;
    s_spark_line_obj = nullptr;
}

void next_os_watch_face_square_refresh_from_mesh(void) {
    const next_os_mesh_sensor_t s = next_os_mesh_state_sensor();
    if (s_moist_label != nullptr && lv_obj_is_in_widget_tree(s_moist_label)) {
        char buf[8];
        (void)std::snprintf(buf, sizeof(buf), "%ld%%", static_cast<long>(s.moisture));
        lv_label_set_text(s_moist_label, buf);
    }
    if (s_alert_badge != nullptr && lv_obj_is_in_widget_tree(s_alert_badge)) {
        char buf[4];
        (void)std::snprintf(buf, sizeof(buf), "%u",
                            static_cast<unsigned>(next_os_mesh_state_alert_count()));
        lv_label_set_text(s_alert_badge, buf);
    }
}

void next_os_watch_face_square_create(lv_obj_t *root) {
    next_os_apply_dark_tactical_style(root);
    lv_obj_add_event_cb(root, square_on_delete, LV_EVENT_DELETE, nullptr);

    lv_obj_t *top = next_os_common_create_inset_header_row(root, 22);
    lv_obj_t *dot = lv_obj_create(top);
    lv_obj_set_size(dot, 6, 6);
    lv_obj_align(dot, LV_ALIGN_LEFT_MID, 0, 0);
    lv_obj_set_style_radius(dot, LV_RADIUS_CIRCLE, 0);
    lv_obj_set_style_bg_color(dot, next_os_color_live_green(), 0);
    lv_obj_t *live = lv_label_create(top);
    char farm_buf[24];
    (void)std::snprintf(farm_buf, sizeof(farm_buf), "LIVE • %u FARM",
                        static_cast<unsigned>(next_os_mesh_state_farm_count()));
    lv_label_set_text(live, farm_buf);
    lv_obj_set_style_text_font(live, &lv_font_montserrat_12, 0);
    lv_obj_set_style_text_color(live, next_os_color_cream(), 0);
    lv_obj_align(live, LV_ALIGN_LEFT_MID, 10, 0);
    lv_obj_t *bat = lv_label_create(top);
    lv_label_set_text(bat, "78%");
    lv_obj_set_style_text_color(bat, next_os_color_cream(), 0);
    lv_obj_align(bat, LV_ALIGN_RIGHT_MID, 0, 0);

    lv_obj_t *clock = lv_label_create(root);
    lv_label_set_text(clock, "07:42");
    lv_obj_set_style_text_font(clock, &lv_font_montserrat_48, 0);
    lv_obj_set_style_text_color(clock, next_os_color_cream(), 0);
    lv_obj_align(clock, LV_ALIGN_CENTER, 0, -24);

    lv_obj_t *date = lv_label_create(root);
    lv_label_set_text(date, "SAB, 24 OKT • W43");
    lv_obj_set_style_text_font(date, &lv_font_montserrat_12, 0);
    lv_obj_set_style_text_color(date, next_os_color_muted(), 0);
    lv_obj_align(date, LV_ALIGN_CENTER, 0, 18);

    lv_obj_t *div = lv_obj_create(root);
    lv_obj_set_size(div, 180, 1);
    lv_obj_align(div, LV_ALIGN_CENTER, 0, 38);
    lv_obj_set_style_bg_color(div, next_os_color_dark_separator(), 0);
    lv_obj_set_style_border_width(div, 0, 0);

    lv_obj_t *row1 = lv_obj_create(root);
    lv_obj_set_size(row1, 200, 28);
    lv_obj_align(row1, LV_ALIGN_BOTTOM_MID, 0, -48);
    lv_obj_set_style_bg_opa(row1, LV_OPA_TRANSP, 0);
    lv_obj_set_style_border_width(row1, 0, 0);
    next_os_common_disable_scroll(row1);

    s_moist_label = lv_label_create(row1);
    lv_label_set_text(s_moist_label, "68%");
    lv_obj_set_style_text_font(s_moist_label, &lv_font_montserrat_20, 0);
    lv_obj_set_style_text_color(s_moist_label, next_os_color_olive(), 0);
    lv_obj_align(s_moist_label, LV_ALIGN_LEFT_MID, 0, 0);

    s_spark_line_obj = lv_line_create(row1);
    lv_line_set_points(s_spark_line_obj, s_spark_pts, 8);
    lv_obj_set_style_line_color(s_spark_line_obj, next_os_color_olive(), 0);
    lv_obj_set_style_line_width(s_spark_line_obj, 2, 0);
    lv_obj_align(s_spark_line_obj, LV_ALIGN_RIGHT_MID, 0, 0);

    lv_obj_t *row2 = lv_obj_create(root);
    lv_obj_set_size(row2, 200, 28);
    lv_obj_align(row2, LV_ALIGN_BOTTOM_MID, 0, -16);
    lv_obj_set_style_bg_opa(row2, LV_OPA_TRANSP, 0);
    lv_obj_set_style_border_width(row2, 0, 0);
    next_os_common_disable_scroll(row2);

    lv_obj_t *badge = lv_obj_create(row2);
    lv_obj_set_size(badge, 36, 22);
    lv_obj_align(badge, LV_ALIGN_LEFT_MID, 0, 0);
    lv_obj_set_style_bg_color(badge, next_os_color_critical(), 0);
    lv_obj_set_style_radius(badge, 6, 0);
    s_alert_badge = lv_label_create(badge);
    lv_label_set_text(s_alert_badge, "2");
    lv_obj_set_style_text_color(s_alert_badge, next_os_color_cream(), 0);
    lv_obj_center(s_alert_badge);

    lv_obj_t *al = lv_label_create(row2);
    lv_label_set_text(al, "ALERT");
    lv_obj_set_style_text_color(al, next_os_color_critical(), 0);
    lv_obj_align(al, LV_ALIGN_LEFT_MID, 42, 0);

    lv_obj_t *timer = lv_label_create(row2);
    lv_label_set_text(timer, LV_SYMBOL_BELL " 14:23");
    lv_obj_set_style_text_color(timer, next_os_color_clay(), 0);
    lv_obj_align(timer, LV_ALIGN_RIGHT_MID, 0, 0);

    next_os_watch_face_square_refresh_from_mesh();
}
