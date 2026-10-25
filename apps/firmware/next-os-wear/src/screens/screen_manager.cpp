#include "screens/screen_manager.h"

#include "screens/alert_center.h"
#include "screens/common.h"
#include "screens/irrigation_control.h"
#include "screens/sensor_monitor.h"
#include "screens/watch_face.h"

static next_os_screen_id_t s_current = NEXT_OS_SCREEN_BOOT;
static bool s_nav_enabled = false;

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
    case NEXT_OS_SCREEN_BOOT:
        break;
    }
}

static bool is_mvp_screen(next_os_screen_id_t screen_id) {
    return screen_id >= NEXT_OS_SCREEN_WATCH_FACE && screen_id <= NEXT_OS_SCREEN_ALERT_CENTER;
}

static void enter_from_boot_async(void *user_data) {
    lv_obj_t *boot_screen = static_cast<lv_obj_t *>(user_data);
    if (boot_screen != nullptr) {
        lv_anim_delete(boot_screen, nullptr);
    }
    next_os_screen_manager_switch(NEXT_OS_SCREEN_WATCH_FACE);
}

void next_os_screen_manager_enter_from_boot(lv_obj_t *boot_screen) {
    lv_async_call(enter_from_boot_async, boot_screen);
}

void next_os_screen_manager_switch(next_os_screen_id_t screen_id) {
    if (!is_mvp_screen(screen_id)) {
        return;
    }
    if (s_nav_enabled && screen_id == s_current) {
        return;
    }

    lv_obj_t *screen = lv_obj_create(nullptr);
    build_screen(screen_id, screen);
    next_os_common_attach_swipe_navigation(screen);

    lv_screen_load_anim(screen, LV_SCREEN_LOAD_ANIM_FADE_IN, 300, 0, true);
    s_current = screen_id;
    s_nav_enabled = true;
}

next_os_screen_id_t next_os_screen_manager_get_current(void) {
    return s_current;
}

void next_os_screen_manager_next(void) {
    if (!s_nav_enabled) {
        return;
    }
    next_os_screen_id_t next_id = s_current;
    switch (s_current) {
    case NEXT_OS_SCREEN_WATCH_FACE:
        next_id = NEXT_OS_SCREEN_SENSOR_MONITOR;
        break;
    case NEXT_OS_SCREEN_SENSOR_MONITOR:
        next_id = NEXT_OS_SCREEN_IRRIGATION;
        break;
    case NEXT_OS_SCREEN_IRRIGATION:
        next_id = NEXT_OS_SCREEN_ALERT_CENTER;
        break;
    case NEXT_OS_SCREEN_ALERT_CENTER:
        next_id = NEXT_OS_SCREEN_WATCH_FACE;
        break;
    default:
        return;
    }
    next_os_screen_manager_switch(next_id);
}

void next_os_screen_manager_prev(void) {
    if (!s_nav_enabled) {
        return;
    }
    next_os_screen_id_t prev_id = s_current;
    switch (s_current) {
    case NEXT_OS_SCREEN_WATCH_FACE:
        prev_id = NEXT_OS_SCREEN_ALERT_CENTER;
        break;
    case NEXT_OS_SCREEN_SENSOR_MONITOR:
        prev_id = NEXT_OS_SCREEN_WATCH_FACE;
        break;
    case NEXT_OS_SCREEN_IRRIGATION:
        prev_id = NEXT_OS_SCREEN_SENSOR_MONITOR;
        break;
    case NEXT_OS_SCREEN_ALERT_CENTER:
        prev_id = NEXT_OS_SCREEN_IRRIGATION;
        break;
    default:
        return;
    }
    next_os_screen_manager_switch(prev_id);
}

void next_os_screen_manager_attach_input_gestures(void) {
    /* Gesture via next_os_common_attach_swipe_navigation per layar */
}
