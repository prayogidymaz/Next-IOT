#ifndef NEXT_OS_DISPLAY_H
#define NEXT_OS_DISPLAY_H

#include <stdint.h>

bool next_os_display_init(void);
void next_os_display_lvgl_handler(void);
uint16_t next_os_display_width(void);
uint16_t next_os_display_height(void);

#endif
