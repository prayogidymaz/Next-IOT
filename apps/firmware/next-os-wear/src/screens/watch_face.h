#ifndef NEXT_OS_WATCH_FACE_H
#define NEXT_OS_WATCH_FACE_H

#include <lvgl.h>

void next_os_watch_face_create(lv_obj_t *root);
void next_os_watch_face_refresh_from_mesh(void);

void next_os_watch_face_install_input(lv_obj_t *root);
void next_os_watch_face_variant_next(void);
void next_os_watch_face_variant_prev(void);

#endif
