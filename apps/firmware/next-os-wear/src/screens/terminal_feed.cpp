#include "screens/terminal_feed.h"

#include "mesh_state.h"
#include "screens/common.h"
#include "theme.h"

#include <cstdio>
#include <cstring>

static lv_obj_t *s_list = nullptr;
static lv_obj_t *s_cursor = nullptr;
static lv_timer_t *s_blink_timer = nullptr;

static lv_color_t terminal_domain_color(const char *domain) {
    if (domain == nullptr) {
        return next_os_color_cream();
    }
    if (strcmp(domain, "sensor") == 0 || strcmp(domain, "vision") == 0) {
        return next_os_color_blue();
    }
    if (strcmp(domain, "motion") == 0 || strcmp(domain, "actuator") == 0) {
        return next_os_color_clay();
    }
    if (strcmp(domain, "security") == 0) {
        return next_os_color_critical();
    }
    if (strcmp(domain, "ui") == 0) {
        return next_os_color_olive();
    }
    if (strcmp(domain, "rule") == 0 || strcmp(domain, "workflow") == 0) {
        return next_os_color_amber();
    }
    return next_os_color_cream();
}

static void terminal_blink_cb(lv_timer_t *timer) {
    (void)timer;
    if (s_cursor == nullptr || !lv_obj_is_in_widget_tree(s_cursor)) {
        return;
    }
    const lv_opa_t opa = lv_obj_get_style_opa(s_cursor, LV_PART_MAIN);
    lv_obj_set_style_opa(s_cursor, opa > LV_OPA_50 ? LV_OPA_TRANSP : LV_OPA_COVER, LV_PART_MAIN);
}

static void terminal_on_delete(lv_event_t *event) {
    if (lv_event_get_code(event) != LV_EVENT_DELETE) {
        return;
    }
    if (s_blink_timer != nullptr) {
        lv_timer_delete(s_blink_timer);
        s_blink_timer = nullptr;
    }
    s_list = nullptr;
    s_cursor = nullptr;
}

static void terminal_rebuild_lines(void) {
    if (s_list == nullptr || !lv_obj_is_in_widget_tree(s_list)) {
        return;
    }
    lv_obj_clean(s_list);

    const uint8_t count = next_os_mesh_state_log_count();
    const uint8_t max_lines = count > 10U ? 10U : count;
    for (uint8_t rev = max_lines; rev > 0; rev--) {
        next_os_mesh_log_entry_t entry {};
        if (!next_os_mesh_state_log_at(static_cast<uint8_t>(rev - 1U), &entry)) {
            continue;
        }
        lv_obj_t *row = lv_label_create(s_list);
        char line[128];
        (void)std::snprintf(line, sizeof(line), "%s [%s] %s", entry.time, entry.domain, entry.payload);
        lv_label_set_text(row, line);
        lv_obj_set_style_text_font(row, &lv_font_montserrat_12, 0);
        lv_obj_set_style_text_color(row, terminal_domain_color(entry.domain), 0);
        lv_obj_set_width(row, 200);
        lv_label_set_long_mode(row, LV_LABEL_LONG_CLIP);
    }

    s_cursor = lv_label_create(s_list);
    lv_label_set_text(s_cursor, "> _");
    lv_obj_set_style_text_color(s_cursor, next_os_color_olive(), 0);
    lv_obj_set_style_text_font(s_cursor, &lv_font_montserrat_12, 0);
}

void next_os_terminal_feed_refresh_from_mesh(void) {
    terminal_rebuild_lines();
}

void next_os_terminal_feed_create(lv_obj_t *root) {
    next_os_apply_black_screen_style(root);
    lv_obj_add_event_cb(root, terminal_on_delete, LV_EVENT_DELETE, nullptr);

    lv_obj_t *header = next_os_common_create_inset_header_row(root, 28);
    lv_obj_t *dot = lv_obj_create(header);
    lv_obj_set_size(dot, 6, 6);
    lv_obj_align(dot, LV_ALIGN_LEFT_MID, 0, 0);
    lv_obj_set_style_radius(dot, LV_RADIUS_CIRCLE, 0);
    lv_obj_set_style_bg_color(dot, next_os_color_live_green(), 0);
    lv_obj_t *title = lv_label_create(header);
    lv_label_set_text(title, "EVENT FEED");
    lv_obj_set_style_text_color(title, next_os_color_olive(), 0);
    lv_obj_align(title, LV_ALIGN_LEFT_MID, 10, -4);
    lv_obj_t *sub = lv_label_create(header);
    lv_label_set_text(sub, "tail -f mesh.log");
    lv_obj_set_style_text_font(sub, &lv_font_montserrat_12, 0);
    lv_obj_set_style_text_color(sub, next_os_color_muted(), 0);
    lv_obj_align(sub, LV_ALIGN_LEFT_MID, 10, 8);

    s_list = lv_obj_create(root);
    lv_obj_set_size(s_list, 210, 130);
    lv_obj_align(s_list, LV_ALIGN_CENTER, 0, 4);
    lv_obj_set_style_bg_color(s_list, next_os_color_dark(), 0);
    lv_obj_set_style_border_width(s_list, 0, 0);
    lv_obj_set_style_pad_all(s_list, 6, 0);
    lv_obj_set_style_pad_row(s_list, 2, 0);
    lv_obj_set_flex_flow(s_list, LV_FLEX_FLOW_COLUMN);
    lv_obj_set_flex_align(s_list, LV_FLEX_ALIGN_START, LV_FLEX_ALIGN_START, LV_FLEX_ALIGN_START);
    lv_obj_set_scrollable(s_list, true);

    terminal_rebuild_lines();

    lv_obj_t *footer = lv_label_create(root);
    char foot[48];
    (void)std::snprintf(foot, sizeof(foot), "%u events • last 2m",
                        static_cast<unsigned>(next_os_mesh_state_log_count()));
    lv_label_set_text(footer, foot);
    lv_obj_set_style_text_color(footer, next_os_color_muted(), 0);
    lv_obj_align(footer, LV_ALIGN_BOTTOM_LEFT, 18, -12);

    lv_obj_t *scroll = lv_label_create(root);
    lv_label_set_text(scroll, "AUTO-SCROLL ▼");
    lv_obj_set_style_text_color(scroll, next_os_color_olive(), 0);
    lv_obj_align(scroll, LV_ALIGN_BOTTOM_RIGHT, -18, -12);

    s_blink_timer = lv_timer_create(terminal_blink_cb, 600, nullptr);
}
