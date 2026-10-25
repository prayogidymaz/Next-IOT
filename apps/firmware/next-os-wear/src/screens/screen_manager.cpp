#include "screens/screen_manager.h"

#include "screens/alert_center.h"
#include "screens/common.h"
#include "screens/irrigation_control.h"
#include "screens/sensor_monitor.h"
#include "screens/watch_face.h"
#include "theme.h"

static next_os_screen_id_t s_current = NEXT_OS_SCREEN_BOOT;
static bool s_nav_enabled = false;
static lv_obj_t *s_current_screen_obj = nullptr;

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

static void switch_screen(next_os_screen_id_t screen_id) {
    if (!is_mvp_screen(screen_id)) {
        return;
    }
    if (s_nav_enabled && screen_id == s_current) {
        return;
    }

    lv_obj_t *scr = lv_screen_active();
    if (scr == nullptr) {
        scr = lv_obj_create(nullptr);
        next_os_apply_screen_style(scr);
        lv_screen_load(scr);
    }

    if (s_current_screen_obj != nullptr) {
        lv_anim_delete(s_current_screen_obj, nullptr);
        lv_obj_delete(s_current_screen_obj);
        s_current_screen_obj = nullptr;
    }

    s_current_screen_obj = lv_obj_create(scr);
    lv_obj_set_size(s_current_screen_obj, 240, 240);
    lv_obj_center(s_current_screen_obj);
    lv_obj_set_style_bg_color(s_current_screen_obj, next_os_color_cream(), 0);
    lv_obj_set_style_bg_opa(s_current_screen_obj, LV_OPA_COVER, 0);
    lv_obj_set_style_border_width(s_current_screen_obj, 0, 0);
    lv_obj_set_style_pad_all(s_current_screen_obj, 0, 0);
    next_os_common_disable_scroll(s_current_screen_obj);

    build_screen(screen_id, s_current_screen_obj);
    next_os_common_attach_swipe_navigation(s_current_screen_obj);
    next_os_common_create_nav_buttons(s_current_screen_obj);

    s_current = screen_id;
    s_nav_enabled = true;
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

    switch_screen(NEXT_OS_SCREEN_WATCH_FACE);
}

void next_os_screen_manager_enter_from_boot(lv_obj_t *boot_screen) {
    lv_async_call(enter_from_boot_async, boot_screen);
}

void next_os_screen_manager_switch(next_os_screen_id_t screen_id) {
    switch_screen(screen_id);
}

next_os_screen_id_t next_os_screen_manager_get_current(void) {
    return s_current;
}

void next_os_screen_manager_next(void) {
    if (!s_nav_enabled) {
        return;
    }
    int next_id = static_cast<int>(s_current) + 1;
    if (next_id > static_cast<int>(NEXT_OS_SCREEN_ALERT_CENTER)) {
        next_id = static_cast<int>(NEXT_OS_SCREEN_WATCH_FACE);
    }
    switch_screen(static_cast<next_os_screen_id_t>(next_id));
}

void next_os_screen_manager_prev(void) {
    if (!s_nav_enabled) {
        return;
    }
    int prev_id = static_cast<int>(s_current) - 1;
    if (prev_id < static_cast<int>(NEXT_OS_SCREEN_WATCH_FACE)) {
        prev_id = static_cast<int>(NEXT_OS_SCREEN_ALERT_CENTER);
    }
    switch_screen(static_cast<next_os_screen_id_t>(prev_id));
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
