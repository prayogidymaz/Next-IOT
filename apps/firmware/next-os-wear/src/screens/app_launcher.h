#ifndef NEXT_OS_APP_LAUNCHER_H
#define NEXT_OS_APP_LAUNCHER_H

#include <lvgl.h>

void next_os_app_launcher_create(lv_obj_t *root);
void next_os_app_launcher_page_prev(void);
void next_os_app_launcher_page_next(void);
uint8_t next_os_app_launcher_page_count(void);
uint8_t next_os_app_launcher_page_index(void);

#endif
