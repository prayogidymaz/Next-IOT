/**
 * Navigasi layar MVP — Artifact preview artboard 01–04
 */
#ifndef NEXT_OS_SCREEN_MANAGER_H
#define NEXT_OS_SCREEN_MANAGER_H

#include <lvgl.h>

typedef enum {
    NEXT_OS_SCREEN_BOOT = 0,
    NEXT_OS_SCREEN_WATCH_FACE,
    NEXT_OS_SCREEN_SENSOR_MONITOR,
    NEXT_OS_SCREEN_IRRIGATION,
    NEXT_OS_SCREEN_ALERT_CENTER,
} next_os_screen_id_t;

/** Panggil setelah animasi boot selesai (hapus layar boot + tampilkan watch face) */
void next_os_screen_manager_enter_from_boot(lv_obj_t *boot_screen);

void next_os_screen_manager_switch(next_os_screen_id_t screen_id);

next_os_screen_id_t next_os_screen_manager_get_current(void);

void next_os_screen_manager_next(void);

void next_os_screen_manager_prev(void);

/** Registrasi gesture — dipanggil otomatis saat switch_screen */
void next_os_screen_manager_attach_input_gestures(void);

/** Sensitivitas swipe pointer (simulator + hardware) */
void next_os_screen_manager_tune_pointer_gesture(void);

#endif /* NEXT_OS_SCREEN_MANAGER_H */
