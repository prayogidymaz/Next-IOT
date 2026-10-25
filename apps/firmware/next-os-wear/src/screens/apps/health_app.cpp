#include "screens/apps/health_app.h"

#include "layout.h"
#include "screens/common.h"
#include "theme.h"

void next_os_health_app_create(lv_obj_t *root) {
    next_os_apply_screen_style(root);
    next_os_common_create_header_label(root, "Health");

    lv_obj_t *row = lv_obj_create(root);
    lv_obj_set_size(row, nextos_content_width(), 120);
    lv_obj_align(row, LV_ALIGN_CENTER, 0, 0);
    lv_obj_set_style_bg_opa(row, LV_OPA_TRANSP, 0);
    lv_obj_set_style_border_width(row, 0, 0);
    lv_obj_set_flex_flow(row, LV_FLEX_FLOW_ROW);
    lv_obj_set_flex_align(row, LV_FLEX_ALIGN_SPACE_EVENLY, LV_FLEX_ALIGN_CENTER, LV_FLEX_ALIGN_CENTER);
    next_os_common_disable_scroll(row);

    const char *vals[] = {"6420", "78", "6h 40m"};
    const char *labels[] = {"Steps", "BPM", "Sleep"};
    for (int i = 0; i < 3; i++) {
        lv_obj_t *col = lv_obj_create(row);
        lv_obj_set_size(col, 64, 80);
        lv_obj_set_style_bg_color(col, NEXTOS_SURFACE, 0);
        lv_obj_set_style_border_color(col, NEXTOS_BORDER, 0);
        lv_obj_set_style_border_width(col, 1, 0);
        lv_obj_t *v = lv_label_create(col);
        lv_label_set_text(v, vals[i]);
        lv_obj_align(v, LV_ALIGN_CENTER, 0, -8);
        lv_obj_t *l = lv_label_create(col);
        lv_label_set_text(l, labels[i]);
        lv_obj_set_style_text_font(l, &lv_font_montserrat_12, 0);
        lv_obj_align(l, LV_ALIGN_CENTER, 0, 16);
    }
}
