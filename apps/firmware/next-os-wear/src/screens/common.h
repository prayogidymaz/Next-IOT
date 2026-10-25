/**
 * Helper UI bersama — layar round 240×240 (Artifact preview 01–04)
 */
#ifndef NEXT_OS_SCREENS_COMMON_H
#define NEXT_OS_SCREENS_COMMON_H

#include <lvgl.h>
#include <stdbool.h>

#include "screens/screen_manager.h"

#define NEXT_OS_SCREEN_PAD 12
#define NEXT_OS_SCREEN_SAFE_TOP 14
#define NEXT_OS_TILE_GAP 6

lv_obj_t *next_os_common_create_header_label(lv_obj_t *parent, const char *text);

lv_obj_t *next_os_common_create_inset_header_row(lv_obj_t *parent, int32_t height);

lv_obj_t *next_os_common_create_settings_title_row(lv_obj_t *parent);

lv_obj_t *next_os_common_create_round_container(lv_obj_t *parent, int32_t size);

lv_obj_t *next_os_common_create_v_separator(lv_obj_t *parent);

void next_os_common_create_pagination_dots(lv_obj_t *parent, uint8_t dot_count, uint8_t active_index);

void next_os_common_create_back_button(lv_obj_t *screen);

void next_os_common_create_corner_nav_for_launcher(lv_obj_t *screen);

void next_os_common_create_corner_nav_for_watch_face(lv_obj_t *screen);

void next_os_common_disable_scroll(lv_obj_t *obj);

lv_obj_t *next_os_common_create_hub_row(lv_obj_t *parent, const char *title, const char *status,
                                        next_os_screen_id_t target);

/** Non-null widget still attached to an active screen tree. */
bool nextos_ui_obj_alive(lv_obj_t *obj);

#endif /* NEXT_OS_SCREENS_COMMON_H */
