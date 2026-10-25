#ifndef NEXT_OS_RUNTIME_THEME_H
#define NEXT_OS_RUNTIME_THEME_H

#include <lvgl.h>

#include "user_prefs.h"

void next_os_runtime_theme_init(void);
void next_os_runtime_theme_cycle(void);
void next_os_runtime_theme_apply_global_refresh(void);

lv_color_t next_os_runtime_color_cream(void);
lv_color_t next_os_runtime_color_olive(void);
lv_color_t next_os_runtime_color_dark(void);
lv_color_t next_os_runtime_color_clay(void);
lv_color_t next_os_runtime_color_critical(void);
lv_color_t next_os_runtime_color_light_grey(void);
lv_color_t next_os_runtime_color_muted(void);
lv_color_t next_os_runtime_color_separator(void);
lv_color_t next_os_runtime_color_black(void);
lv_color_t next_os_runtime_color_dark_tactical(void);
lv_color_t next_os_runtime_color_dark_separator(void);
lv_color_t next_os_runtime_color_blue(void);
lv_color_t next_os_runtime_color_amber(void);
lv_color_t next_os_runtime_color_live_green(void);

void next_os_apply_screen_style(lv_obj_t *screen);
void next_os_apply_dark_tactical_style(lv_obj_t *screen);
void next_os_apply_black_screen_style(lv_obj_t *screen);

const lv_font_t *next_os_font_clock_large(void);

#endif /* NEXT_OS_RUNTIME_THEME_H */
