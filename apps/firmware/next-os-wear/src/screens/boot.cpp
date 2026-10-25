#include "screens/boot.h"

#include "theme.h"

static void (*s_on_finished)(void) = nullptr;
static lv_obj_t *s_logo_arc = nullptr;

static void boot_rotate_exec(void *obj, int32_t v) {
    lv_obj_t *arc = static_cast<lv_obj_t *>(obj);
    if (arc == nullptr || s_logo_arc == nullptr || arc != s_logo_arc) {
        return;
    }
    lv_arc_set_rotation(arc, static_cast<lv_value_precise_t>(v));
}

static void boot_fade_exec(void *obj, int32_t v) {
    lv_obj_set_style_opa(static_cast<lv_obj_t *>(obj), static_cast<lv_opa_t>(v), 0);
}

static void boot_finish_async(void *user_data) {
    (void)user_data;
    s_logo_arc = nullptr;
    if (s_on_finished != nullptr) {
        s_on_finished();
    }
}

static void boot_anim_ready(lv_anim_t *anim) {
    (void)anim;
    lv_async_call(boot_finish_async, nullptr);
}

static void boot_timer_cb(lv_timer_t *timer) {
    if (s_logo_arc == nullptr) {
        lv_timer_del(timer);
        return;
    }
    lv_anim_t a;
    lv_anim_init(&a);
    lv_anim_set_var(&a, s_logo_arc);
    lv_anim_set_exec_cb(&a, boot_rotate_exec);
    lv_anim_set_values(&a, 0, 360);
    lv_anim_set_duration(&a, 800);
    lv_anim_set_ready_cb(&a, boot_anim_ready);
    lv_anim_start(&a);
    lv_timer_del(timer);
}

void next_os_boot_screen_create(lv_obj_t *root, void (*on_finished)(void)) {
    s_on_finished = on_finished;
    next_os_apply_screen_style(root);

    s_logo_arc = lv_arc_create(root);
    lv_obj_set_size(s_logo_arc, 120, 120);
    lv_obj_center(s_logo_arc);
    lv_arc_set_bg_angles(s_logo_arc, 0, 360);
    lv_arc_set_angles(s_logo_arc, 0, 300);
    lv_obj_set_style_arc_color(s_logo_arc, next_os_color_olive(), LV_PART_MAIN);
    lv_obj_set_style_arc_color(s_logo_arc, next_os_color_clay(), LV_PART_INDICATOR);
    lv_obj_set_style_arc_width(s_logo_arc, 8, LV_PART_MAIN);
    lv_obj_set_style_arc_width(s_logo_arc, 8, LV_PART_INDICATOR);
    lv_obj_remove_style(s_logo_arc, nullptr, LV_PART_KNOB);
    lv_obj_set_clickable(s_logo_arc, false);

    lv_obj_t *title = lv_label_create(root);
    lv_label_set_text(title, "NEXT-IOT");
    lv_obj_set_style_text_color(title, next_os_color_dark(), 0);
    lv_obj_align(title, LV_ALIGN_CENTER, 0, 0);

    lv_obj_t *sub = lv_label_create(root);
    lv_label_set_text(sub, "Next-OS Wear");
    lv_obj_set_style_text_color(sub, next_os_color_olive(), 0);
    lv_obj_align(sub, LV_ALIGN_CENTER, 0, 28);

    lv_obj_set_style_opa(root, LV_OPA_TRANSP, 0);
    lv_anim_t fade;
    lv_anim_init(&fade);
    lv_anim_set_var(&fade, root);
    lv_anim_set_exec_cb(&fade, boot_fade_exec);
    lv_anim_set_values(&fade, LV_OPA_TRANSP, LV_OPA_COVER);
    lv_anim_set_duration(&fade, 600);
    lv_anim_start(&fade);

    lv_timer_create(boot_timer_cb, 2000, nullptr);
}
