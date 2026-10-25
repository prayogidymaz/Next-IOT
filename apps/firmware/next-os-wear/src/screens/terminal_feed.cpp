#include "screens/terminal_feed.h"

#include "layout.h"
#include "mesh_state.h"
#include "screens/common.h"
#include "theme.h"

#include <cstdio>
#include <cstring>

static lv_obj_t *s_list = nullptr;
static lv_obj_t *s_cursor = nullptr;
static lv_obj_t *s_footer = nullptr;
static lv_timer_t *s_blink_timer = nullptr;
static lv_timer_t *s_poll_timer = nullptr;
static uint8_t s_last_log_revision = 0;

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
    if (!nextos_ui_obj_alive(s_cursor)) {
        return;
    }
    const lv_opa_t opa = lv_obj_get_style_opa(s_cursor, LV_PART_MAIN);
    lv_obj_set_style_opa(s_cursor, opa > LV_OPA_50 ? LV_OPA_TRANSP : LV_OPA_COVER, LV_PART_MAIN);
}

void next_os_terminal_feed_dispose(void) {
    if (s_blink_timer != nullptr) {
        lv_timer_delete(s_blink_timer);
        s_blink_timer = nullptr;
    }
    if (s_poll_timer != nullptr) {
        lv_timer_delete(s_poll_timer);
        s_poll_timer = nullptr;
    }
    s_list = nullptr;
    s_cursor = nullptr;
    s_footer = nullptr;
}

static void terminal_on_delete(lv_event_t *event) {
    if (lv_event_get_code(event) != LV_EVENT_DELETE) {
        return;
    }
    next_os_terminal_feed_dispose();
}

static void terminal_rebuild_lines(void);

static void terminal_format_line(char *line, size_t len, const next_os_mesh_log_entry_t *entry) {
    if (strcmp(entry->event_type, "execution_step") == 0) {
        (void)std::snprintf(line, len, "%s %s", entry->time, entry->payload);
        return;
    }
    (void)std::snprintf(line, len, "%s [%s] %s", entry->time, entry->domain, entry->payload);
}

static void terminal_poll_cb(lv_timer_t *timer) {
    (void)timer;
    const uint8_t rev = next_os_mesh_state_log_revision();
    if (rev != s_last_log_revision) {
        s_last_log_revision = rev;
        terminal_rebuild_lines();
        if (nextos_ui_obj_alive(s_footer)) {
            char foot[48];
            (void)std::snprintf(foot, sizeof(foot), "%u events • last 2m",
                                static_cast<unsigned>(next_os_mesh_state_log_count()));
            lv_label_set_text(s_footer, foot);
        }
        if (nextos_ui_obj_alive(s_list)) {
            lv_obj_scroll_to_y(s_list, LV_COORD_MAX, LV_ANIM_ON);
        }
    }
}

static void terminal_rebuild_lines(void) {
    if (!nextos_ui_obj_alive(s_list)) {
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
        terminal_format_line(line, sizeof(line), &entry);
        lv_label_set_text(row, line);
        lv_obj_set_style_text_font(row, &lv_font_montserrat_12, 0);
        lv_obj_set_style_text_color(row, terminal_domain_color(entry.domain), 0);
        lv_obj_set_width(row, nextos_content_width() - 8);
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
    next_os_terminal_feed_dispose();
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
    const int32_t list_h = NEXTOS_IS_ROUND ? 130 : nextos_content_height() - 90;
    lv_obj_set_size(s_list, nextos_content_width(), list_h);
    lv_obj_align(s_list, LV_ALIGN_CENTER, 0, 4);
    lv_obj_set_style_bg_color(s_list, next_os_color_dark(), 0);
    lv_obj_set_style_border_width(s_list, 0, 0);
    lv_obj_set_style_pad_all(s_list, 6, 0);
    lv_obj_set_style_pad_row(s_list, 2, 0);
    lv_obj_set_flex_flow(s_list, LV_FLEX_FLOW_COLUMN);
    lv_obj_set_flex_align(s_list, LV_FLEX_ALIGN_START, LV_FLEX_ALIGN_START, LV_FLEX_ALIGN_START);
    lv_obj_set_scrollable(s_list, true);

    terminal_rebuild_lines();

    s_footer = lv_label_create(root);
    char foot[48];
    (void)std::snprintf(foot, sizeof(foot), "%u events • last 2m",
                        static_cast<unsigned>(next_os_mesh_state_log_count()));
    lv_label_set_text(s_footer, foot);
    lv_obj_set_style_text_color(s_footer, next_os_color_muted(), 0);
    lv_obj_align(s_footer, LV_ALIGN_BOTTOM_LEFT, nextos_safe_padding_side(), -nextos_safe_padding_bottom());

    s_last_log_revision = next_os_mesh_state_log_revision();
    s_poll_timer = lv_timer_create(terminal_poll_cb, 500, nullptr);

    lv_obj_t *scroll = lv_label_create(root);
    lv_label_set_text(scroll, "AUTO-SCROLL ▼");
    lv_obj_set_style_text_color(scroll, next_os_color_olive(), 0);
    lv_obj_align(scroll, LV_ALIGN_BOTTOM_RIGHT, -18, -12);

    s_blink_timer = lv_timer_create(terminal_blink_cb, 600, nullptr);
}
