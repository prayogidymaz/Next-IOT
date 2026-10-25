#ifndef NEXT_OS_CONTROL_CENTER_H
#define NEXT_OS_CONTROL_CENTER_H

#include <lvgl.h>

typedef void (*next_os_overlay_dismiss_fn)(void);

void next_os_control_center_show(lv_obj_t *parent, next_os_overlay_dismiss_fn on_dismiss);

#endif
