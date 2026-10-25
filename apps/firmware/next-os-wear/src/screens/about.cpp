#include "screens/about.h"

#include "config.h"
#include "layout.h"
#include "screens/common.h"
#include "theme.h"

#include <cstdio>

void next_os_about_create(lv_obj_t *root) {
    next_os_apply_screen_style(root);
    next_os_common_create_header_label(root, "About");

    char ver[48];
    (void)std::snprintf(ver, sizeof(ver), "NEXT-OS WEAR v%s", NEXT_OS_FIRMWARE_VERSION);
    lv_obj_t *label = lv_label_create(root);
    lv_label_set_text(label, ver);
    lv_obj_set_style_text_font(label, &lv_font_montserrat_16, 0);
    lv_obj_align(label, LV_ALIGN_CENTER, 0, -10);

    lv_obj_t *sub = lv_label_create(root);
    lv_label_set_text(sub, "Smart Farming Mesh\nPhase 2 Week 21-24");
    lv_obj_set_style_text_align(sub, LV_TEXT_ALIGN_CENTER, 0);
    lv_obj_set_style_text_color(sub, NEXTOS_TEXT_MUTED, 0);
    lv_obj_align(sub, LV_ALIGN_CENTER, 0, 24);
}
