#ifndef NEXT_OS_SCREEN_BOOT_H
#define NEXT_OS_SCREEN_BOOT_H

#include <lvgl.h>

/** Buat layar boot; animasi ~2 detik lalu memanggil on_finished */
void next_os_boot_screen_create(lv_obj_t *root, void (*on_finished)(void));

#endif
