#include "screens/screen_manager.h"

#include "screens/alert_center.h"
#include "screens/cctv_alert.h"
#include "screens/common.h"
#include "screens/irrigation_control.h"
#include "screens/irrigation_wave.h"
#include "screens/mesh_graph.h"
#include "screens/ndvi_heatmap.h"
#include "screens/sensor_monitor.h"
#include "screens/sensor_radial.h"
#include "screens/settings.h"
#include "screens/terminal_feed.h"
#include "screens/watch_face.h"
#include "screens/watch_face_square.h"
#include "screens/qr_pair.h"
#include "layout.h"
#include "theme.h"

static next_os_screen_id_t s_current = NEXT_OS_SCREEN_BOOT;
static bool s_nav_enabled = false;
static lv_obj_t *s_current_screen_obj = nullptr;
static lv_obj_t *s_modal_overlay = nullptr;

static void dismiss_modal_internal(void) {
    if (s_modal_overlay != nullptr) {
        lv_obj_delete(s_modal_overlay);
        s_modal_overlay = nullptr;
    }
}

void next_os_screen_manager_dismiss_modal(void) {
    dismiss_modal_internal();
}

static void build_screen(next_os_screen_id_t screen_id, lv_obj_t *root) {
    switch (screen_id) {
    case NEXT_OS_SCREEN_WATCH_FACE:
        next_os_watch_face_create(root);
        break;
    case NEXT_OS_SCREEN_SENSOR_MONITOR:
        next_os_sensor_monitor_create(root);
        break;
    case NEXT_OS_SCREEN_IRRIGATION:
        next_os_irrigation_control_create(root);
        break;
    case NEXT_OS_SCREEN_ALERT_CENTER:
        next_os_alert_center_create(root);
        break;
    case NEXT_OS_SCREEN_SETTINGS:
        next_os_settings_create(root);
        break;
    case NEXT_OS_SCREEN_CCTV_ALERT:
        next_os_cctv_alert_create(root);
        break;
    case NEXT_OS_SCREEN_WATCH_FACE_SQUARE:
        next_os_watch_face_square_create(root);
        break;
    case NEXT_OS_SCREEN_SENSOR_RADIAL:
        next_os_sensor_radial_create(root);
        break;
    case NEXT_OS_SCREEN_IRRIGATION_WAVE:
        next_os_irrigation_wave_create(root);
        break;
    case NEXT_OS_SCREEN_MESH_GRAPH:
        next_os_mesh_graph_create(root);
        break;
    case NEXT_OS_SCREEN_NDVI_HEATMAP:
        next_os_ndvi_heatmap_create(root);
        break;
    case NEXT_OS_SCREEN_TERMINAL_FEED:
        next_os_terminal_feed_create(root);
        break;
    case NEXT_OS_SCREEN_BOOT:
        break;
    }
}

static bool is_nav_screen(next_os_screen_id_t screen_id) {
    return screen_id >= NEXT_OS_SCREEN_WATCH_FACE && screen_id <= NEXT_OS_SCREEN_TERMINAL_FEED;
}

static void screen_opa_exec(void *obj, int32_t value) {
    lv_obj_set_style_opa(static_cast<lv_obj_t *>(obj), static_cast<lv_opa_t>(value), 0);
}

static next_os_screen_id_t s_pending_screen = NEXT_OS_SCREEN_BOOT;
static bool s_pending_force = false;

static lv_obj_t *ensure_shell_screen(void) {
    lv_obj_t *scr = lv_screen_active();
    if (scr == nullptr) {
        scr = lv_obj_create(nullptr);
        next_os_apply_screen_style(scr);
        lv_screen_load(scr);
    }
    return scr;
}

static void screen_fade_in(lv_obj_t *obj) {
    lv_anim_t anim {};
    lv_anim_init(&anim);
    lv_anim_set_var(&anim, obj);
    lv_anim_set_exec_cb(&anim, screen_opa_exec);
    lv_anim_set_values(&anim, LV_OPA_TRANSP, LV_OPA_COVER);
    lv_anim_set_duration(&anim, 150);
    lv_anim_set_path_cb(&anim, lv_anim_path_ease_in);
    lv_anim_start(&anim);
}

static void mount_screen(next_os_screen_id_t screen_id, bool fade_in) {
    lv_obj_t *scr = ensure_shell_screen();
    s_current_screen_obj = lv_obj_create(scr);
    lv_obj_set_size(s_current_screen_obj, NEXTOS_W, NEXTOS_H);
    lv_obj_center(s_current_screen_obj);
    lv_obj_set_style_bg_color(s_current_screen_obj, NEXTOS_BG, 0);
    lv_obj_set_style_bg_opa(s_current_screen_obj, fade_in ? LV_OPA_TRANSP : LV_OPA_COVER, 0);
    lv_obj_set_style_border_width(s_current_screen_obj, 0, 0);
    lv_obj_set_style_pad_all(s_current_screen_obj, 0, 0);
    next_os_common_disable_scroll(s_current_screen_obj);

    build_screen(screen_id, s_current_screen_obj);
    next_os_common_attach_swipe_navigation(s_current_screen_obj);
    next_os_common_create_nav_buttons(s_current_screen_obj);

    s_current = screen_id;
    s_nav_enabled = true;
    if (fade_in) {
        screen_fade_in(s_current_screen_obj);
    }
}

static void screen_fade_out_ready(lv_anim_t *anim) {
    lv_obj_t *old = static_cast<lv_obj_t *>(anim->var);
    if (old != nullptr) {
        lv_obj_delete(old);
    }
    if (s_current_screen_obj == old) {
        s_current_screen_obj = nullptr;
    }
    mount_screen(s_pending_screen, true);
    s_pending_force = false;
}

static void switch_screen(next_os_screen_id_t screen_id, bool force_reload) {
    if (!is_nav_screen(screen_id)) {
        return;
    }
    if (!force_reload && s_nav_enabled && screen_id == s_current) {
        return;
    }

    dismiss_modal_internal();
    (void)ensure_shell_screen();

    if (s_current_screen_obj == nullptr) {
        mount_screen(screen_id, false);
        return;
    }

    s_pending_screen = screen_id;
    s_pending_force = force_reload;

    lv_anim_t anim {};
    lv_anim_init(&anim);
    lv_anim_set_var(&anim, s_current_screen_obj);
    lv_anim_set_exec_cb(&anim, screen_opa_exec);
    lv_anim_set_values(&anim, LV_OPA_COVER, LV_OPA_TRANSP);
    lv_anim_set_duration(&anim, 150);
    lv_anim_set_path_cb(&anim, lv_anim_path_ease_out);
    lv_anim_set_ready_cb(&anim, screen_fade_out_ready);
    lv_anim_start(&anim);
}

lv_obj_t *next_os_screen_manager_get_content_root(void) {
    return s_current_screen_obj;
}

static void enter_from_boot_async(void *user_data) {
    lv_obj_t *boot_screen = static_cast<lv_obj_t *>(user_data);
    if (boot_screen != nullptr) {
        lv_anim_delete(boot_screen, nullptr);
    }

    lv_obj_t *shell = lv_obj_create(nullptr);
    next_os_apply_screen_style(shell);
    lv_screen_load(shell);

    if (boot_screen != nullptr) {
        lv_obj_delete(boot_screen);
    }

    switch_screen(NEXT_OS_SCREEN_WATCH_FACE, false);
}

void next_os_screen_manager_enter_from_boot(lv_obj_t *boot_screen) {
    lv_async_call(enter_from_boot_async, boot_screen);
}

void next_os_screen_manager_switch(next_os_screen_id_t screen_id) {
    switch_screen(screen_id, false);
}

void next_os_screen_manager_reload_current(void) {
    if (!s_nav_enabled) {
        return;
    }
    switch_screen(s_current, true);
}

void next_os_screen_manager_show_qr_pair_modal(void) {
    if (s_modal_overlay != nullptr) {
        return;
    }
    lv_obj_t *scr = lv_screen_active();
    if (scr == nullptr) {
        return;
    }
    s_modal_overlay = lv_obj_create(scr);
    lv_obj_set_scrollable(s_modal_overlay, false);
    next_os_qr_pair_show(s_modal_overlay, next_os_screen_manager_dismiss_modal);
    lv_obj_move_foreground(s_modal_overlay);
}

next_os_screen_id_t next_os_screen_manager_get_current(void) {
    return s_current;
}

void next_os_screen_manager_next(void) {
    if (!s_nav_enabled) {
        return;
    }
    int next_id = static_cast<int>(s_current) + 1;
    if (next_id > static_cast<int>(NEXT_OS_SCREEN_TERMINAL_FEED)) {
        next_id = static_cast<int>(NEXT_OS_SCREEN_WATCH_FACE);
    }
    switch_screen(static_cast<next_os_screen_id_t>(next_id), false);
}

void next_os_screen_manager_prev(void) {
    if (!s_nav_enabled) {
        return;
    }
    int prev_id = static_cast<int>(s_current) - 1;
    if (prev_id < static_cast<int>(NEXT_OS_SCREEN_WATCH_FACE)) {
        prev_id = static_cast<int>(NEXT_OS_SCREEN_TERMINAL_FEED);
    }
    switch_screen(static_cast<next_os_screen_id_t>(prev_id), false);
}

void next_os_screen_manager_attach_input_gestures(void) {
    /* Gesture via next_os_common_attach_swipe_navigation per layar */
}

void next_os_screen_manager_tune_pointer_gesture(void) {
    lv_indev_t *indev = lv_indev_get_next(nullptr);
    while (indev != nullptr) {
        if (lv_indev_get_type(indev) == LV_INDEV_TYPE_POINTER) {
            lv_indev_set_scroll_limit(indev, 10);
            lv_indev_set_gesture_min_distance(indev, 35);
            lv_indev_set_gesture_min_velocity(indev, 2);
        }
        indev = lv_indev_get_next(indev);
    }
}
