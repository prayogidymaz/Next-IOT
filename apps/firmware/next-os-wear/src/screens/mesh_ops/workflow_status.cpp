#include "screens/mesh_ops/workflow_status.h"

#include "mesh_state.h"
#include "layout.h"
#include "screens/common.h"
#include "theme.h"

#include <cstdio>

void next_os_workflow_status_create(lv_obj_t *root) {
    next_os_apply_screen_style(root);
    next_os_common_create_header_label(root, "Workflows");

    const next_os_mesh_workflow_t wf = next_os_mesh_state_workflow();

    lv_obj_t *card = lv_obj_create(root);
    lv_obj_set_size(card, nextos_content_width(), 72);
    lv_obj_align(card, LV_ALIGN_CENTER, 0, -20);
    lv_obj_set_style_bg_color(card, NEXTOS_SURFACE, 0);
    lv_obj_set_style_border_color(card, NEXTOS_BORDER, 0);
    lv_obj_set_style_border_width(card, 1, 0);

    lv_obj_t *name = lv_label_create(card);
    lv_label_set_text(name, wf.workflow_name);
    lv_obj_align(name, LV_ALIGN_TOP_LEFT, 8, 6);

    char prog[24];
    (void)std::snprintf(prog, sizeof(prog), "Step %u / %u", static_cast<unsigned>(wf.step),
                        static_cast<unsigned>(wf.total));
    lv_obj_t *steps = lv_label_create(card);
    lv_label_set_text(steps, prog);
    lv_obj_set_style_text_color(steps, NEXTOS_TEXT_MUTED, 0);
    lv_obj_align(steps, LV_ALIGN_TOP_LEFT, 8, 26);

    lv_obj_t *state = lv_label_create(card);
    lv_label_set_text(state, wf.failed ? "FAILED" : (wf.active ? "ACTIVE" : "COMPLETED"));
    lv_obj_set_style_text_color(state, wf.failed ? NEXTOS_CRITICAL : NEXTOS_SUCCESS, 0);
    lv_obj_align(state, LV_ALIGN_BOTTOM_RIGHT, -8, -8);

    lv_obj_t *bar_bg = lv_obj_create(card);
    lv_obj_set_size(bar_bg, nextos_content_width() - 24, 6);
    lv_obj_align(bar_bg, LV_ALIGN_BOTTOM_MID, 0, -28);
    lv_obj_set_style_bg_color(bar_bg, NEXTOS_BORDER, 0);
    if (wf.total > 0U) {
        lv_obj_t *bar_fg = lv_obj_create(bar_bg);
        lv_obj_set_width(bar_fg, (nextos_content_width() - 24) * wf.step / wf.total);
        lv_obj_set_height(bar_fg, 6);
        lv_obj_set_style_bg_color(bar_fg, NEXTOS_ACCENT_PRIMARY, 0);
    }
}
