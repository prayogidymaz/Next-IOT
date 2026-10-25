#include "screens/farming/harvest_calendar.h"

#include "layout.h"
#include "screens/common.h"
#include "theme.h"

void next_os_harvest_calendar_create(lv_obj_t *root) {
    next_os_apply_screen_style(root);
    next_os_common_create_header_label(root, "Harvest Calendar");

    lv_obj_t *badge = lv_label_create(root);
    lv_label_set_text(badge, "FRUITING");
    lv_obj_set_style_bg_color(badge, NEXTOS_ACCENT_PRIMARY, 0);
    lv_obj_set_style_text_color(badge, NEXTOS_SURFACE, 0);
    lv_obj_set_style_pad_hor(badge, 10, 0);
    lv_obj_set_style_pad_ver(badge, 4, 0);
    lv_obj_set_style_radius(badge, 8, 0);
    lv_obj_align(badge, LV_ALIGN_TOP_MID, 0, 40);

    lv_obj_t *days = lv_label_create(root);
    lv_label_set_text(days, "Day 42 in stage");
    lv_obj_align(days, LV_ALIGN_TOP_MID, 0, 68);

    lv_obj_t *bar_bg = lv_obj_create(root);
    lv_obj_set_size(bar_bg, nextos_content_width() - 20, 8);
    lv_obj_align(bar_bg, LV_ALIGN_CENTER, 0, -10);
    lv_obj_set_style_bg_color(bar_bg, NEXTOS_BORDER, 0);

    lv_obj_t *bar_fg = lv_obj_create(bar_bg);
    lv_obj_set_size(bar_fg, (nextos_content_width() - 20) * 7 / 10, 8);
    lv_obj_set_style_bg_color(bar_fg, NEXTOS_ACCENT_PRIMARY, 0);

    lv_obj_t *tasks = lv_label_create(root);
    lv_label_set_text(tasks, "• Scout pests\n• Adjust irrigation\n• Sample NDVI");
    lv_obj_set_style_text_color(tasks, NEXTOS_TEXT_SECONDARY, 0);
    lv_obj_align(tasks, LV_ALIGN_BOTTOM_MID, 0, -40);
}
