#ifndef NEXT_OS_SCREENS_TERMINAL_FEED_H
#define NEXT_OS_SCREENS_TERMINAL_FEED_H

#include <lvgl.h>

void next_os_terminal_feed_create(lv_obj_t *root);
void next_os_terminal_feed_dispose(void);
void next_os_terminal_feed_refresh_from_mesh(void);

#endif /* NEXT_OS_SCREENS_TERMINAL_FEED_H */
