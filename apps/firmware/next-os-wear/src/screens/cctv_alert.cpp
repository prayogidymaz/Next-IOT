#include "screens/cctv_alert.h"

#include "mesh_state.h"
#include "screens/common.h"
#include "theme.h"

#include <cstdio>

static lv_obj_t *s_ts_label = nullptr;
static lv_obj_t *s_pest_label = nullptr;
static lv_obj_t *s_title_label = nullptr;
static lv_obj_t *s_sub_label = nullptr;

static void cctv_on_delete(lv_event_t *event) {
    if (lv_event_get_code(event) != LV_EVENT_DELETE) {
        return;
    }
    s_ts_label = nullptr;
    s_pest_label = nullptr;
    s_title_label = nullptr;
    s_sub_label = nullptr;
}

void next_os_cctv_alert_refresh_from_mesh(void) {
    const next_os_mesh_cctv_t cctv = next_os_mesh_state_cctv();
    if (s_ts_label != nullptr && lv_obj_is_in_widget_tree(s_ts_label)) {
        lv_label_set_text(s_ts_label, cctv.timestamp);
    }
    if (s_pest_label != nullptr && lv_obj_is_in_widget_tree(s_pest_label)) {
        char buf[16];
        (void)std::snprintf(buf, sizeof(buf), "PEST %u%%", static_cast<unsigned>(cctv.pest_pct));
        lv_label_set_text(s_pest_label, buf);
    }
    if (s_title_label != nullptr && lv_obj_is_in_widget_tree(s_title_label)) {
        lv_label_set_text(s_title_label, cctv.title);
    }
    if (s_sub_label != nullptr && lv_obj_is_in_widget_tree(s_sub_label)) {
        lv_label_set_text(s_sub_label, cctv.subtitle);
    }
}

void next_os_cctv_alert_create(lv_obj_t *root) {
    next_os_apply_screen_style(root);
    lv_obj_add_event_cb(root, cctv_on_delete, LV_EVENT_DELETE, nullptr);

    const next_os_mesh_cctv_t cctv = next_os_mesh_state_cctv();

    lv_obj_t *header = next_os_common_create_inset_header_row(root, 24);
    lv_obj_t *cam = lv_label_create(header);
    lv_label_set_text(cam, LV_SYMBOL_VIDEO);
    lv_obj_set_style_text_color(cam, next_os_color_clay(), 0);
    lv_obj_align(cam, LV_ALIGN_LEFT_MID, 0, 0);
    lv_obj_t *ht = lv_label_create(header);
    lv_label_set_text(ht, "CCTV • PLOT B");
    lv_obj_set_style_text_font(ht, &lv_font_montserrat_12, 0);
    lv_obj_set_style_text_color(ht, next_os_color_clay(), 0);
    lv_obj_align(ht, LV_ALIGN_CENTER, 0, 0);

    lv_obj_t *frame = lv_obj_create(root);
    lv_obj_set_size(frame, 180, 118);
    lv_obj_align(frame, LV_ALIGN_TOP_MID, 0, 68);
    lv_obj_set_style_radius(frame, 8, 0);
    lv_obj_set_style_border_width(frame, 0, 0);
    lv_obj_set_style_bg_color(frame, next_os_color_olive(), 0);
    lv_obj_set_style_bg_grad_color(frame, next_os_color_live_green(), 0);
    lv_obj_set_style_bg_grad_dir(frame, LV_GRAD_DIR_VER, 0);
    next_os_common_disable_scroll(frame);

    lv_obj_t *live_dot = lv_obj_create(frame);
    lv_obj_set_size(live_dot, 6, 6);
    lv_obj_align(live_dot, LV_ALIGN_TOP_LEFT, 6, 6);
    lv_obj_set_style_radius(live_dot, LV_RADIUS_CIRCLE, 0);
    lv_obj_set_style_bg_color(live_dot, next_os_color_critical(), 0);
    lv_obj_t *live = lv_label_create(frame);
    lv_label_set_text(live, "LIVE");
    lv_obj_set_style_text_font(live, &lv_font_montserrat_12, 0);
    lv_obj_set_style_text_color(live, next_os_color_cream(), 0);
    lv_obj_align(live, LV_ALIGN_TOP_LEFT, 16, 4);

    s_ts_label = lv_label_create(frame);
    lv_label_set_text(s_ts_label, cctv.timestamp);
    lv_obj_set_style_text_font(s_ts_label, &lv_font_montserrat_12, 0);
    lv_obj_set_style_text_color(s_ts_label, next_os_color_cream(), 0);
    lv_obj_align(s_ts_label, LV_ALIGN_TOP_RIGHT, -6, 4);

    lv_obj_t *motion = lv_obj_create(frame);
    lv_obj_set_size(motion, 72, 40);
    lv_obj_align(motion, LV_ALIGN_BOTTOM_MID, 0, -8);
    lv_obj_set_style_bg_opa(motion, LV_OPA_TRANSP, 0);
    lv_obj_set_style_border_color(motion, next_os_color_amber(), 0);
    lv_obj_set_style_border_width(motion, 1, 0);
    lv_obj_set_style_border_opa(motion, LV_OPA_70, 0);

    lv_obj_t *pest_bg = lv_obj_create(frame);
    lv_obj_set_size(pest_bg, LV_SIZE_CONTENT, LV_SIZE_CONTENT);
    lv_obj_set_style_bg_color(pest_bg, next_os_color_dark(), 0);
    lv_obj_set_style_bg_opa(pest_bg, LV_OPA_80, 0);
    lv_obj_set_style_pad_hor(pest_bg, 4, 0);
    lv_obj_set_style_pad_ver(pest_bg, 2, 0);
    lv_obj_align(pest_bg, LV_ALIGN_BOTTOM_LEFT, 4, -4);
    s_pest_label = lv_label_create(pest_bg);
    char pest_buf[16];
    (void)std::snprintf(pest_buf, sizeof(pest_buf), "PEST %u%%", static_cast<unsigned>(cctv.pest_pct));
    lv_label_set_text(s_pest_label, pest_buf);
    lv_obj_set_style_text_font(s_pest_label, &lv_font_montserrat_12, 0);
    lv_obj_set_style_text_color(s_pest_label, next_os_color_cream(), 0);

    lv_obj_t *ndvi_bg = lv_obj_create(frame);
    lv_obj_set_size(ndvi_bg, LV_SIZE_CONTENT, LV_SIZE_CONTENT);
    lv_obj_set_style_bg_color(ndvi_bg, next_os_color_dark(), 0);
    lv_obj_set_style_bg_opa(ndvi_bg, LV_OPA_80, 0);
    lv_obj_set_style_pad_hor(ndvi_bg, 4, 0);
    lv_obj_set_style_pad_ver(ndvi_bg, 2, 0);
    lv_obj_align(ndvi_bg, LV_ALIGN_BOTTOM_RIGHT, -4, -4);
    lv_obj_t *ndvi = lv_label_create(ndvi_bg);
    lv_label_set_text(ndvi, "NDVI");
    lv_obj_set_style_text_font(ndvi, &lv_font_montserrat_12, 0);
    lv_obj_set_style_text_color(ndvi, next_os_color_cream(), 0);

    s_title_label = lv_label_create(root);
    lv_label_set_text(s_title_label, cctv.title);
    lv_obj_set_style_text_font(s_title_label, &lv_font_montserrat_14, 0);
    lv_obj_set_style_text_color(s_title_label, next_os_color_dark(), 0);
    lv_obj_align(s_title_label, LV_ALIGN_BOTTOM_MID, 0, -52);

    s_sub_label = lv_label_create(root);
    lv_label_set_text(s_sub_label, cctv.subtitle);
    lv_obj_set_style_text_font(s_sub_label, &lv_font_montserrat_12, 0);
    lv_obj_set_style_text_color(s_sub_label, next_os_color_muted(), 0);
    lv_obj_align(s_sub_label, LV_ALIGN_BOTTOM_MID, 0, -34);

    lv_obj_t *dispatch = lv_button_create(root);
    lv_obj_set_size(dispatch, 160, 32);
    lv_obj_align(dispatch, LV_ALIGN_BOTTOM_MID, 0, -8);
    lv_obj_set_style_bg_color(dispatch, next_os_color_clay(), 0);
    lv_obj_t *dl = lv_label_create(dispatch);
    lv_label_set_text(dl, "DISPATCH DRONE");
    lv_obj_set_style_text_color(dl, next_os_color_cream(), 0);
    lv_obj_center(dl);
}
