/**
 * Tactical Warm Cream — kontrak warna UI Next-OS Wear v1
 */
#ifndef NEXT_OS_THEME_H
#define NEXT_OS_THEME_H

#include <lvgl.h>

/* Palette (RGB888) */
#define NEXT_OS_COLOR_CREAM 0xF5EFE0
#define NEXT_OS_COLOR_OLIVE 0x556B4A
#define NEXT_OS_COLOR_CLAY 0xD97757
#define NEXT_OS_COLOR_CRITICAL 0xB23A3A
#define NEXT_OS_COLOR_DARK 0x1F1F1F
#define NEXT_OS_COLOR_MUTED 0x6B6B63

#define NEXT_OS_FONT_SIZE_TITLE 16
#define NEXT_OS_FONT_SIZE_KPI 12
#define NEXT_OS_FONT_SIZE_CLOCK 20

static inline lv_color_t next_os_color_cream(void) {
    return lv_color_hex(NEXT_OS_COLOR_CREAM);
}

static inline lv_color_t next_os_color_olive(void) {
    return lv_color_hex(NEXT_OS_COLOR_OLIVE);
}

static inline lv_color_t next_os_color_dark(void) {
    return lv_color_hex(NEXT_OS_COLOR_DARK);
}

static inline lv_color_t next_os_color_clay(void) {
    return lv_color_hex(NEXT_OS_COLOR_CLAY);
}

static inline void next_os_apply_screen_style(lv_obj_t *screen) {
    lv_obj_set_style_bg_color(screen, next_os_color_cream(), 0);
    lv_obj_set_style_bg_opa(screen, LV_OPA_COVER, 0);
    lv_obj_set_style_border_width(screen, 0, 0);
    lv_obj_set_style_pad_all(screen, 0, 0);
}

#endif /* NEXT_OS_THEME_H */
