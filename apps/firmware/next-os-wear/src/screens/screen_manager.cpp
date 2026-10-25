#include "screens/screen_manager.h"

#include "navigation/nav_stack.h"
#include "screens/about.h"
#include "screens/alert_center.h"
#include "screens/app_launcher.h"
#include "screens/apps/barometer_app.h"
#include "screens/apps/compass_app.h"
#include "screens/apps/flashlight_app.h"
#include "screens/apps/health_app.h"
#include "screens/apps/timer_app.h"
#include "screens/apps/weather_app.h"
#include "screens/cctv_alert.h"
#include "screens/common.h"
#include "screens/farming/harvest_calendar.h"
#include "screens/hubs/farming_hub.h"
#include "screens/hubs/mesh_ops_hub.h"
#include "screens/irrigation_control.h"
#include "screens/mesh_graph.h"
#include "screens/mesh_ops/device_dispatch.h"
#include "screens/mesh_ops/workflow_status.h"
#include "screens/ndvi_heatmap.h"
#include "screens/overlays/control_center.h"
#include "screens/overlays/notification_center.h"
#include "screens/qr_pair.h"
#include "screens/sensor_monitor.h"
#include "screens/settings.h"
#include "screens/terminal_feed.h"
#include "screens/watch_face.h"
#include "layout.h"
#include "theme.h"

#include <cstdio>

static next_os_screen_id_t s_current = NEXT_OS_SCREEN_BOOT;
static bool s_nav_enabled = false;
static lv_obj_t *s_current_screen_obj = nullptr;
static lv_obj_t *s_modal_overlay = nullptr;
static lv_obj_t *s_sheet_overlay = nullptr;

static void qr_pair_screen_dismiss(void) {
    next_os_nav_stack_pop();
}

static void dismiss_modal_internal(void) {
    if (s_modal_overlay != nullptr) {
        lv_obj_delete(s_modal_overlay);
        s_modal_overlay = nullptr;
    }
}

static void dismiss_sheet_internal(void) {
    if (s_sheet_overlay != nullptr) {
        lv_obj_delete(s_sheet_overlay);
        s_sheet_overlay = nullptr;
    }
}

void next_os_screen_manager_dismiss_modal(void) {
    dismiss_modal_internal();
}

void next_os_screen_manager_dismiss_overlay(void) {
    dismiss_sheet_internal();
}

static void overlay_dismiss_cb(void) {
    dismiss_sheet_internal();
}

static void screen_dispose_before_delete(next_os_screen_id_t screen_id) {
    switch (screen_id) {
    case NEXT_OS_SCREEN_WATCH_FACE:
        next_os_watch_face_dispose();
        break;
    case NEXT_OS_SCREEN_MESH_GRAPH:
        next_os_mesh_graph_dispose();
        break;
    case NEXT_OS_SCREEN_MESH_TERMINAL:
        next_os_terminal_feed_dispose();
        break;
    case NEXT_OS_SCREEN_APP_TIMER:
        next_os_timer_app_dispose();
        break;
    case NEXT_OS_SCREEN_APP_COMPASS:
        next_os_compass_app_dispose();
        break;
    default:
        break;
    }
}

static void delete_current_content(void) {
    if (s_current_screen_obj == nullptr) {
        return;
    }
    screen_dispose_before_delete(s_current);
    lv_anim_delete(s_current_screen_obj, nullptr);
    lv_obj_delete(s_current_screen_obj);
    s_current_screen_obj = nullptr;
}

bool next_os_screen_manager_is_stackable(next_os_screen_id_t screen_id) {
    if (screen_id == NEXT_OS_SCREEN_BOOT || screen_id == NEXT_OS_SCREEN_CONTROL_CENTER ||
        screen_id == NEXT_OS_SCREEN_NOTIFICATION_CENTER) {
        return false;
    }
    return screen_id >= NEXT_OS_SCREEN_WATCH_FACE;
}

static bool screen_wants_back(next_os_screen_id_t screen_id) {
    if (screen_id == NEXT_OS_SCREEN_WATCH_FACE) {
        return false;
    }
    return next_os_screen_manager_is_stackable(screen_id);
}

static bool build_screen(next_os_screen_id_t screen_id, lv_obj_t *root) {
    if (root == nullptr) {
        (void)std::printf("[SCR] build_screen root=null id=%d\n", static_cast<int>(screen_id));
        (void)std::fflush(stdout);
        return false;
    }
    switch (screen_id) {
    case NEXT_OS_SCREEN_WATCH_FACE:
        next_os_watch_face_create(root);
        break;
    case NEXT_OS_SCREEN_APP_LAUNCHER:
        next_os_app_launcher_create(root);
        break;
    case NEXT_OS_SCREEN_FARMING_HUB:
        next_os_farming_hub_create(root);
        break;
    case NEXT_OS_SCREEN_FARMING_SENSOR:
        next_os_sensor_monitor_create(root);
        break;
    case NEXT_OS_SCREEN_FARMING_IRRIGATION:
        next_os_irrigation_control_create(root);
        break;
    case NEXT_OS_SCREEN_FARMING_CCTV:
        next_os_cctv_alert_create(root);
        break;
    case NEXT_OS_SCREEN_FARMING_NDVI:
        next_os_ndvi_heatmap_create(root);
        break;
    case NEXT_OS_SCREEN_FARMING_HARVEST:
        next_os_harvest_calendar_create(root);
        break;
    case NEXT_OS_SCREEN_MESH_HUB:
        next_os_mesh_ops_hub_create(root);
        break;
    case NEXT_OS_SCREEN_MESH_GRAPH:
        next_os_mesh_graph_create(root);
        break;
    case NEXT_OS_SCREEN_MESH_TERMINAL:
        next_os_terminal_feed_create(root);
        break;
    case NEXT_OS_SCREEN_MESH_WORKFLOW:
        next_os_workflow_status_create(root);
        break;
    case NEXT_OS_SCREEN_MESH_DISPATCH:
        next_os_device_dispatch_create(root);
        break;
    case NEXT_OS_SCREEN_ALERT_CENTER:
        next_os_alert_center_create(root);
        break;
    case NEXT_OS_SCREEN_APP_TIMER:
        next_os_timer_app_create(root);
        break;
    case NEXT_OS_SCREEN_APP_WEATHER:
        next_os_weather_app_create(root);
        break;
    case NEXT_OS_SCREEN_APP_COMPASS:
        next_os_compass_app_create(root);
        break;
    case NEXT_OS_SCREEN_APP_FLASHLIGHT:
        next_os_flashlight_app_create(root);
        break;
    case NEXT_OS_SCREEN_APP_HEALTH:
        next_os_health_app_create(root);
        break;
    case NEXT_OS_SCREEN_APP_BAROMETER:
        next_os_barometer_app_create(root);
        break;
    case NEXT_OS_SCREEN_SETTINGS:
        next_os_settings_create(root);
        break;
    case NEXT_OS_SCREEN_QR_PAIR:
        next_os_qr_pair_show(root, qr_pair_screen_dismiss);
        break;
    case NEXT_OS_SCREEN_ABOUT:
        next_os_about_create(root);
        break;
    case NEXT_OS_SCREEN_BOOT:
    case NEXT_OS_SCREEN_CONTROL_CENTER:
    case NEXT_OS_SCREEN_NOTIFICATION_CENTER:
        break;
    default:
        (void)std::printf("[SCR] unknown screen id=%d - fallback watch face\n", static_cast<int>(screen_id));
        (void)std::fflush(stdout);
        next_os_watch_face_create(root);
        return false;
    }
    return true;
}

static void apply_screen_chrome(next_os_screen_id_t screen_id, lv_obj_t *root) {
    if (screen_id == NEXT_OS_SCREEN_WATCH_FACE) {
        next_os_watch_face_install_input(root);
        next_os_common_create_corner_nav_for_watch_face(root);
        return;
    }
    if (screen_id == NEXT_OS_SCREEN_APP_LAUNCHER) {
        next_os_common_create_corner_nav_for_launcher(root);
        return;
    }
    if (screen_wants_back(screen_id)) {
        next_os_common_create_back_button(root);
    }
}

static void screen_opa_exec(void *obj, int32_t value) {
    lv_obj_set_style_opa(static_cast<lv_obj_t *>(obj), static_cast<lv_opa_t>(value), 0);
}

static next_os_screen_id_t s_pending_screen = NEXT_OS_SCREEN_BOOT;

static lv_obj_t *ensure_shell_screen(void) {
    lv_obj_t *scr = lv_screen_active();
    if (scr == nullptr) {
        scr = lv_obj_create(nullptr);
        if (scr == nullptr) {
            (void)std::printf("[SCR] FATAL: cannot create shell screen\n");
            (void)std::fflush(stdout);
            return nullptr;
        }
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
    if (scr == nullptr) {
        return;
    }
    (void)std::printf("[SCR] mount id=%d fade=%d\n", static_cast<int>(screen_id), fade_in ? 1 : 0);
    (void)std::fflush(stdout);
    s_current_screen_obj = lv_obj_create(scr);
    if (s_current_screen_obj == nullptr) {
        (void)std::printf("[SCR] FATAL: content root alloc failed\n");
        (void)std::fflush(stdout);
        return;
    }
    lv_obj_set_size(s_current_screen_obj, NEXTOS_W, NEXTOS_H);
    lv_obj_center(s_current_screen_obj);
    lv_obj_set_style_bg_color(s_current_screen_obj, NEXTOS_BG, 0);
    lv_obj_set_style_bg_opa(s_current_screen_obj, fade_in ? LV_OPA_TRANSP : LV_OPA_COVER, 0);
    lv_obj_set_style_border_width(s_current_screen_obj, 0, 0);
    lv_obj_set_style_pad_all(s_current_screen_obj, 0, 0);
    next_os_common_disable_scroll(s_current_screen_obj);

    s_current = screen_id;
    s_nav_enabled = true;
    if (!build_screen(screen_id, s_current_screen_obj)) {
        s_current = NEXT_OS_SCREEN_WATCH_FACE;
    }
    apply_screen_chrome(s_current, s_current_screen_obj);
    if (fade_in) {
        screen_fade_in(s_current_screen_obj);
    }
}

static void screen_fade_out_ready(lv_anim_t *anim) {
    lv_obj_t *old = static_cast<lv_obj_t *>(anim->var);
    if (old != nullptr) {
        screen_dispose_before_delete(s_current);
        lv_obj_delete(old);
    }
    if (s_current_screen_obj == old) {
        s_current_screen_obj = nullptr;
    }
    mount_screen(s_pending_screen, true);
}

static void present_internal(next_os_screen_id_t screen_id, bool animate, bool force_reload) {
    if (!next_os_screen_manager_is_stackable(screen_id)) {
        return;
    }
    if (!force_reload && s_nav_enabled && screen_id == s_current) {
        return;
    }

    dismiss_modal_internal();
    dismiss_sheet_internal();
    (void)ensure_shell_screen();

    if (s_current_screen_obj == nullptr || !animate) {
        delete_current_content();
        mount_screen(screen_id, false);
        return;
    }

    s_pending_screen = screen_id;
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

void next_os_screen_manager_present(next_os_screen_id_t screen_id, bool animate) {
    present_internal(screen_id, animate, false);
}

static void enter_from_boot_async(void *user_data) {
    (void)std::printf("[BOOT] enter_from_boot_async\n");
    (void)std::fflush(stdout);
    lv_obj_t *boot_screen = static_cast<lv_obj_t *>(user_data);
    if (boot_screen != nullptr) {
        lv_anim_delete(boot_screen, nullptr);
    }

    lv_obj_t *shell = lv_obj_create(nullptr);
    if (shell == nullptr) {
        (void)std::printf("[BOOT] FATAL: shell alloc failed\n");
        (void)std::fflush(stdout);
        return;
    }
    next_os_apply_screen_style(shell);
    lv_screen_load(shell);

    if (boot_screen != nullptr) {
        lv_obj_delete(boot_screen);
    }

    if (!next_os_nav_stack_is_ready()) {
        next_os_nav_stack_init();
    }
    next_os_nav_stack_go_home();
    (void)std::printf("[BOOT] watch face mounted after boot\n");
    (void)std::fflush(stdout);
}

void next_os_screen_manager_enter_from_boot(lv_obj_t *boot_screen) {
    lv_async_call(enter_from_boot_async, boot_screen);
}

void next_os_screen_manager_switch(next_os_screen_id_t screen_id) {
    next_os_nav_stack_push(screen_id, true);
}

void next_os_screen_manager_reload_current(void) {
    if (!s_nav_enabled) {
        return;
    }
    present_internal(s_current, false, true);
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

void next_os_screen_manager_show_control_center(void) {
    if (s_sheet_overlay != nullptr) {
        return;
    }
    lv_obj_t *scr = lv_screen_active();
    if (scr == nullptr) {
        return;
    }
    s_sheet_overlay = lv_obj_create(scr);
    lv_obj_set_size(s_sheet_overlay, NEXTOS_W, NEXTOS_H);
    lv_obj_set_style_bg_opa(s_sheet_overlay, LV_OPA_TRANSP, 0);
    lv_obj_set_style_border_width(s_sheet_overlay, 0, 0);
    next_os_control_center_show(s_sheet_overlay, overlay_dismiss_cb);
    lv_obj_move_foreground(s_sheet_overlay);
}

void next_os_screen_manager_show_notification_center(void) {
    if (s_sheet_overlay != nullptr) {
        return;
    }
    lv_obj_t *scr = lv_screen_active();
    if (scr == nullptr) {
        return;
    }
    s_sheet_overlay = lv_obj_create(scr);
    lv_obj_set_size(s_sheet_overlay, NEXTOS_W, NEXTOS_H);
    lv_obj_set_style_bg_opa(s_sheet_overlay, LV_OPA_TRANSP, 0);
    lv_obj_set_style_border_width(s_sheet_overlay, 0, 0);
    next_os_notification_center_show(s_sheet_overlay, overlay_dismiss_cb);
    lv_obj_move_foreground(s_sheet_overlay);
}

next_os_screen_id_t next_os_screen_manager_get_current(void) {
    return s_current;
}

lv_obj_t *next_os_screen_manager_get_content_root(void) {
    return s_current_screen_obj;
}

void next_os_screen_manager_next(void) {}
void next_os_screen_manager_prev(void) {}

void next_os_screen_manager_attach_input_gestures(void) {}

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
