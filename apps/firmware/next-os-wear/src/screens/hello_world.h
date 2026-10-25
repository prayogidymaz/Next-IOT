#ifndef NEXT_OS_SCREEN_HELLO_H
#define NEXT_OS_SCREEN_HELLO_H

#include <lvgl.h>

void next_os_hello_world_screen_create(lv_obj_t *root);

/** Perbarui jarum jam analog (0-59 menit, 0-23 jam) */
void next_os_hello_world_update_clock(uint8_t hour, uint8_t minute);

#endif
