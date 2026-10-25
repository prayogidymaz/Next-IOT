#include "screens/app_launcher.h"

#include "icons/app_icons.h"
#include "layout.h"
#include "navigation/nav_stack.h"
#include "screens/common.h"
#include "theme.h"

static lv_obj_t *s_grid = nullptr;
static lv_obj_t *s_root = nullptr;
static lv_obj_t *s_dots_row = nullptr;
static uint8_t s_page = 0;

static uint8_t launcher_page_count(void) {
    const uint8_t total = next_os_app_icon_count();
    return static_cast<uint8_t>((total + 8U) / 9U);
}

uint8_t next_os_app_launcher_page_count(void) {
    return launcher_page_count();
}

uint8_t next_os_app_launcher_page_index(void) {
    return s_page;
}

static void launcher_icon_click_cb(lv_event_t *event) {
    if (lv_event_get_code(event) != LV_EVENT_CLICKED) {
        return;
    }
    const auto index = static_cast<uint8_t>(reinterpret_cast<intptr_t>(lv_event_get_user_data(event)));
    const next_os_app_icon_entry_t *entry = next_os_app_icon_at(index);
    if (entry == nullptr) {
        return;
    }
    next_os_nav_stack_push(entry->screen_id, true);
}

static void launcher_rebuild_page(void) {
    if (s_grid == nullptr || s_root == nullptr) {
        return;
    }
    lv_obj_clean(s_grid);

    const uint8_t start = static_cast<uint8_t>(s_page * 9U);
    const uint8_t total = next_os_app_icon_count();
    uint8_t col = 0;
    uint8_t row = 0;
    for (uint8_t i = start; i < total && i < start + 9U; i++) {
        const next_os_app_icon_entry_t *entry = next_os_app_icon_at(i);
        if (entry == nullptr) {
            continue;
        }
        lv_obj_t *cell = lv_button_create(s_grid);
        lv_obj_set_size(cell, 60, 78);
        lv_obj_set_style_bg_color(cell, NEXTOS_SURFACE, 0);
        lv_obj_set_style_border_color(cell, NEXTOS_BORDER, 0);
        lv_obj_set_style_border_width(cell, 1, 0);
        lv_obj_set_style_radius(cell, 12, 0);
        lv_obj_add_event_cb(cell, launcher_icon_click_cb, LV_EVENT_CLICKED,
                            reinterpret_cast<void *>(static_cast<intptr_t>(i)));

        lv_obj_t *icon = lv_label_create(cell);
        lv_label_set_text(icon, entry->symbol != nullptr ? entry->symbol : LV_SYMBOL_FILE);
        lv_obj_set_style_text_font(icon, &lv_font_montserrat_24, 0);
        lv_obj_set_style_text_color(icon, NEXTOS_ACCENT_PRIMARY, 0);
        lv_obj_align(icon, LV_ALIGN_TOP_MID, 0, 8);

        lv_obj_t *label = lv_label_create(cell);
        lv_label_set_text(label, entry->label != nullptr ? entry->label : "App");
        lv_obj_set_style_text_font(label, &lv_font_montserrat_12, 0);
        lv_obj_set_width(label, 56);
        lv_label_set_long_mode(label, LV_LABEL_LONG_DOT);
        lv_obj_set_style_text_align(label, LV_TEXT_ALIGN_CENTER, 0);
        lv_obj_align(label, LV_ALIGN_BOTTOM_MID, 0, -4);

        lv_obj_set_grid_cell(cell, LV_GRID_ALIGN_CENTER, col, 1, LV_GRID_ALIGN_CENTER, row, 1);
        col++;
        if (col >= 3U) {
            col = 0;
            row++;
        }
    }
    if (s_dots_row != nullptr) {
        lv_obj_delete(s_dots_row);
        s_dots_row = nullptr;
    }
    s_dots_row = lv_obj_create(s_root);
    lv_obj_set_size(s_dots_row, LV_SIZE_CONTENT, LV_SIZE_CONTENT);
    lv_obj_set_style_bg_opa(s_dots_row, LV_OPA_TRANSP, 0);
    lv_obj_set_style_border_width(s_dots_row, 0, 0);
    lv_obj_align(s_dots_row, LV_ALIGN_BOTTOM_MID, 0, -10);
    next_os_common_create_pagination_dots(s_dots_row, launcher_page_count(), s_page);
}

void next_os_app_launcher_page_prev(void) {
    if (s_page == 0U) {
        return;
    }
    s_page--;
    launcher_rebuild_page();
}

void next_os_app_launcher_page_next(void) {
    const uint8_t pages = launcher_page_count();
    if (s_page + 1U >= pages) {
        return;
    }
    s_page++;
    launcher_rebuild_page();
}

void next_os_app_launcher_create(lv_obj_t *root) {
    s_root = root;
    s_page = 0;
    next_os_apply_screen_style(root);

    lv_obj_t *title = lv_label_create(root);
    lv_label_set_text(title, "Apps");
    lv_obj_set_style_text_font(title, &lv_font_montserrat_16, 0);
    lv_obj_set_style_text_color(title, NEXTOS_TEXT_PRIMARY, 0);
    lv_obj_align(title, LV_ALIGN_TOP_MID, 0, nextos_status_header_y());

    s_grid = lv_obj_create(root);
    lv_obj_set_size(s_grid, nextos_content_width(), NEXTOS_IS_ROUND ? 168 : 220);
    lv_obj_align(s_grid, LV_ALIGN_CENTER, 0, 8);
    lv_obj_set_style_bg_opa(s_grid, LV_OPA_TRANSP, 0);
    lv_obj_set_style_border_width(s_grid, 0, 0);
    lv_obj_set_style_pad_row(s_grid, 10, 0);
    lv_obj_set_style_pad_column(s_grid, 10, 0);
    lv_obj_set_layout(s_grid, LV_LAYOUT_GRID);
    static int32_t col_dsc[] = {LV_GRID_FR(1), LV_GRID_FR(1), LV_GRID_FR(1), LV_GRID_TEMPLATE_LAST};
    static int32_t row_dsc[] = {LV_GRID_FR(1), LV_GRID_FR(1), LV_GRID_FR(1), LV_GRID_TEMPLATE_LAST};
    lv_obj_set_grid_dsc_array(s_grid, col_dsc, row_dsc);
    next_os_common_disable_scroll(s_grid);

    launcher_rebuild_page();
}
