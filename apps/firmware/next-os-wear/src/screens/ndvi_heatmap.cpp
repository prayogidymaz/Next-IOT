#include "screens/ndvi_heatmap.h"

#include "mesh_state.h"
#include "screens/common.h"
#include "theme.h"

#include <cstdio>

static lv_obj_t *s_grid_cells[NEXT_OS_MESH_NDVI_CELLS] = {nullptr};
static lv_obj_t *s_avg_label = nullptr;

static lv_color_t ndvi_level_color(uint8_t level) {
    switch (level % 6U) {
    case 0:
        return next_os_color_critical();
    case 1:
        return next_os_color_clay();
    case 2:
        return next_os_color_amber();
    case 3:
        return next_os_color_olive();
    case 4:
        return next_os_color_live_green();
    default:
        return lv_color_hex(0x2D5A27);
    }
}

static void ndvi_on_delete(lv_event_t *event) {
    if (lv_event_get_code(event) != LV_EVENT_DELETE) {
        return;
    }
    for (uint8_t i = 0; i < NEXT_OS_MESH_NDVI_CELLS; i++) {
        s_grid_cells[i] = nullptr;
    }
    s_avg_label = nullptr;
}

void next_os_ndvi_heatmap_refresh_from_mesh(void) {
    const next_os_mesh_ndvi_t ndvi = next_os_mesh_state_ndvi();
    for (uint8_t i = 0; i < NEXT_OS_MESH_NDVI_CELLS; i++) {
        if (s_grid_cells[i] != nullptr && lv_obj_is_in_widget_tree(s_grid_cells[i])) {
            lv_obj_set_style_bg_color(s_grid_cells[i], ndvi_level_color(ndvi.cells[i]), 0);
        }
    }
    if (s_avg_label != nullptr && lv_obj_is_in_widget_tree(s_avg_label)) {
        char buf[32];
        (void)std::snprintf(buf, sizeof(buf), "%.2f avg NDVI", static_cast<double>(ndvi.avg_ndvi));
        lv_label_set_text(s_avg_label, buf);
    }
}

void next_os_ndvi_heatmap_create(lv_obj_t *root) {
    next_os_apply_black_screen_style(root);
    lv_obj_add_event_cb(root, ndvi_on_delete, LV_EVENT_DELETE, nullptr);

    const next_os_mesh_ndvi_t ndvi = next_os_mesh_state_ndvi();

    lv_obj_t *header = next_os_common_create_inset_header_row(root, 22);
    lv_obj_t *icon = lv_label_create(header);
    lv_label_set_text(icon, LV_SYMBOL_IMAGE);
    lv_obj_set_style_text_color(icon, next_os_color_olive(), 0);
    lv_obj_align(icon, LV_ALIGN_LEFT_MID, 0, 0);
    lv_obj_t *ht = lv_label_create(header);
    lv_label_set_text(ht, "NDVI • PLOT A");
    lv_obj_set_style_text_color(ht, next_os_color_olive(), 0);
    lv_obj_align(ht, LV_ALIGN_CENTER, 0, 0);
    lv_obj_t *tm = lv_label_create(header);
    lv_label_set_text(tm, ndvi.timestamp);
    lv_obj_set_style_text_color(tm, next_os_color_muted(), 0);
    lv_obj_align(tm, LV_ALIGN_RIGHT_MID, 0, 0);

    lv_obj_t *grid = lv_obj_create(root);
    lv_obj_set_size(grid, 192, 96);
    lv_obj_align(grid, LV_ALIGN_CENTER, 0, -20);
    lv_obj_set_style_bg_opa(grid, LV_OPA_TRANSP, 0);
    lv_obj_set_style_border_width(grid, 0, 0);
    lv_obj_set_style_pad_row(grid, 2, 0);
    lv_obj_set_style_pad_column(grid, 2, 0);
    lv_obj_set_flex_flow(grid, LV_FLEX_FLOW_ROW_WRAP);
    lv_obj_set_flex_align(grid, LV_FLEX_ALIGN_START, LV_FLEX_ALIGN_START, LV_FLEX_ALIGN_START);
    next_os_common_disable_scroll(grid);

    for (uint8_t i = 0; i < NEXT_OS_MESH_NDVI_CELLS; i++) {
        lv_obj_t *cell = lv_obj_create(grid);
        lv_obj_set_size(cell, 22, 22);
        lv_obj_set_style_radius(cell, 2, 0);
        lv_obj_set_style_border_width(cell, 0, 0);
        lv_obj_set_style_bg_color(cell, ndvi_level_color(ndvi.cells[i]), 0);
        s_grid_cells[i] = cell;
    }

    lv_obj_t *summary = lv_obj_create(root);
    lv_obj_set_size(summary, 210, LV_SIZE_CONTENT);
    lv_obj_align(summary, LV_ALIGN_BOTTOM_MID, 0, -36);
    lv_obj_set_style_bg_opa(summary, LV_OPA_TRANSP, 0);
    lv_obj_set_style_border_width(summary, 0, 0);
    next_os_common_disable_scroll(summary);

    s_avg_label = lv_label_create(summary);
    char avg_buf[32];
    (void)std::snprintf(avg_buf, sizeof(avg_buf), "%.2f avg NDVI", static_cast<double>(ndvi.avg_ndvi));
    lv_label_set_text(s_avg_label, avg_buf);
    lv_obj_set_style_text_font(s_avg_label, &lv_font_montserrat_14, 0);
    lv_obj_set_style_text_color(s_avg_label, next_os_color_cream(), 0);
    lv_obj_align(s_avg_label, LV_ALIGN_TOP_LEFT, 0, 0);

    lv_obj_t *stress_dot = lv_obj_create(summary);
    lv_obj_set_size(stress_dot, 6, 6);
    lv_obj_align(stress_dot, LV_ALIGN_TOP_RIGHT, -80, 4);
    lv_obj_set_style_radius(stress_dot, LV_RADIUS_CIRCLE, 0);
    lv_obj_set_style_bg_color(stress_dot, next_os_color_critical(), 0);
    lv_obj_t *stress = lv_label_create(summary);
    char stress_buf[24];
    (void)std::snprintf(stress_buf, sizeof(stress_buf), "%u ZONA STRESS",
                        static_cast<unsigned>(ndvi.stress_zones));
    lv_label_set_text(stress, stress_buf);
    lv_obj_set_style_text_color(stress, next_os_color_critical(), 0);
    lv_obj_align(stress, LV_ALIGN_TOP_RIGHT, 0, 0);

    lv_obj_t *bar = lv_obj_create(summary);
    lv_obj_set_size(bar, 200, 8);
    lv_obj_align(bar, LV_ALIGN_BOTTOM_MID, 0, -14);
    lv_obj_set_style_border_width(bar, 0, 0);
    lv_obj_set_style_pad_all(bar, 0, 0);
    lv_obj_set_flex_flow(bar, LV_FLEX_FLOW_ROW);
    next_os_common_disable_scroll(bar);
    const lv_color_t grad[8] = {next_os_color_critical(), next_os_color_clay(), next_os_color_amber(),
                                lv_color_hex(0xE8D44D), next_os_color_live_green(), next_os_color_olive(),
                                lv_color_hex(0x2D5A27), lv_color_hex(0x1B3D16)};
    for (uint8_t g = 0; g < 8; g++) {
        lv_obj_t *seg = lv_obj_create(bar);
        lv_obj_set_size(seg, 24, 8);
        lv_obj_set_style_bg_color(seg, grad[g], 0);
        lv_obj_set_style_border_width(seg, 0, 0);
        lv_obj_set_style_radius(seg, 0, 0);
    }

    lv_obj_t *scale = lv_label_create(summary);
    lv_label_set_text(scale, "-0.2 ... 0.9");
    lv_obj_set_style_text_font(scale, &lv_font_montserrat_12, 0);
    lv_obj_set_style_text_color(scale, next_os_color_muted(), 0);
    lv_obj_align(scale, LV_ALIGN_BOTTOM_MID, 0, 0);
}
