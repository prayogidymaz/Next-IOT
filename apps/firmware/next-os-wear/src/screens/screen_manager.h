/**
 * Screen manager — hierarchical navigation (Week 21+).
 */
#ifndef NEXT_OS_SCREEN_MANAGER_H
#define NEXT_OS_SCREEN_MANAGER_H

#include <lvgl.h>

#include <stdbool.h>

typedef enum {
    NEXT_OS_SCREEN_BOOT = 0,

    NEXT_OS_SCREEN_WATCH_FACE,
    NEXT_OS_SCREEN_APP_LAUNCHER,

    NEXT_OS_SCREEN_FARMING_HUB,
    NEXT_OS_SCREEN_FARMING_SENSOR,
    NEXT_OS_SCREEN_FARMING_IRRIGATION,
    NEXT_OS_SCREEN_FARMING_CCTV,
    NEXT_OS_SCREEN_FARMING_NDVI,
    NEXT_OS_SCREEN_FARMING_HARVEST,

    NEXT_OS_SCREEN_MESH_HUB,
    NEXT_OS_SCREEN_MESH_GRAPH,
    NEXT_OS_SCREEN_MESH_TERMINAL,
    NEXT_OS_SCREEN_MESH_WORKFLOW,
    NEXT_OS_SCREEN_MESH_DISPATCH,

    NEXT_OS_SCREEN_ALERT_CENTER,

    NEXT_OS_SCREEN_APP_TIMER,
    NEXT_OS_SCREEN_APP_WEATHER,
    NEXT_OS_SCREEN_APP_COMPASS,
    NEXT_OS_SCREEN_APP_FLASHLIGHT,
    NEXT_OS_SCREEN_APP_HEALTH,
    NEXT_OS_SCREEN_APP_BAROMETER,

    NEXT_OS_SCREEN_SETTINGS,
    NEXT_OS_SCREEN_QR_PAIR,
    NEXT_OS_SCREEN_ABOUT,

    NEXT_OS_SCREEN_CONTROL_CENTER,
    NEXT_OS_SCREEN_NOTIFICATION_CENTER,
} next_os_screen_id_t;

void next_os_screen_manager_enter_from_boot(lv_obj_t *boot_screen);

bool next_os_screen_manager_is_stackable(next_os_screen_id_t screen_id);

void next_os_screen_manager_present(next_os_screen_id_t screen_id, bool animate);

next_os_screen_id_t next_os_screen_manager_get_current(void);

void next_os_screen_manager_reload_current(void);

void next_os_screen_manager_show_qr_pair_modal(void);
void next_os_screen_manager_dismiss_modal(void);

void next_os_screen_manager_show_control_center(void);
void next_os_screen_manager_show_notification_center(void);
void next_os_screen_manager_dismiss_overlay(void);

lv_obj_t *next_os_screen_manager_get_content_root(void);

void next_os_screen_manager_attach_input_gestures(void);
void next_os_screen_manager_tune_pointer_gesture(void);

/** @deprecated Flat cycle removed — no-op. */
void next_os_screen_manager_next(void);
void next_os_screen_manager_prev(void);
void next_os_screen_manager_switch(next_os_screen_id_t screen_id);

#endif /* NEXT_OS_SCREEN_MANAGER_H */
