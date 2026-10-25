/**
 * Tactical Warm Cream — kontrak warna UI Next-OS Wear v1
 */
#ifndef NEXT_OS_THEME_H
#define NEXT_OS_THEME_H

#include <lvgl.h>

/* Palette (RGB888) — alias preview Artifact */
#define NEXT_OS_COLOR_CREAM 0xF5EFE0
#define NEXT_OS_COLOR_OLIVE 0x556B4A
#define NEXT_OS_COLOR_CLAY 0xD97757
#define NEXT_OS_COLOR_CRITICAL 0xB23A3A
#define NEXT_OS_COLOR_DARK 0x1F1F1F
#define NEXT_OS_COLOR_DARK_TACTICAL 0x1C1F18
#define NEXT_OS_COLOR_BLACK 0x0A0A0A
#define NEXT_OS_COLOR_DARK_SEPARATOR 0x2E3328
#define NEXT_OS_COLOR_BLUE 0x4A7FB8
#define NEXT_OS_COLOR_AMBER 0xD4A017
#define NEXT_OS_COLOR_LIVE_GREEN 0x3DAA63
#define NEXT_OS_COLOR_MUTED 0x6B6B63
#define NEXT_OS_COLOR_LIGHT_GREY 0xB8B2A6
#define NEXT_OS_COLOR_SEPARATOR 0xD0C7B0

#define NEXT_OS_COLOR_CREAM_ALIAS NEXT_OS_COLOR_CREAM
#define NEXT_OS_COLOR_OLIVE_ALIAS NEXT_OS_COLOR_OLIVE
#define NEXT_OS_COLOR_CLAY_ALIAS NEXT_OS_COLOR_CLAY
#define NEXT_OS_COLOR_CRITICAL_ALIAS NEXT_OS_COLOR_CRITICAL
#define NEXT_OS_COLOR_DARK_ALIAS NEXT_OS_COLOR_DARK
#define NEXT_OS_COLOR_LIGHT_GREY_ALIAS NEXT_OS_COLOR_LIGHT_GREY

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

static inline lv_color_t next_os_color_critical(void) {
    return lv_color_hex(NEXT_OS_COLOR_CRITICAL);
}

static inline lv_color_t next_os_color_light_grey(void) {
    return lv_color_hex(NEXT_OS_COLOR_LIGHT_GREY);
}

static inline lv_color_t next_os_color_muted(void) {
    return lv_color_hex(NEXT_OS_COLOR_MUTED);
}

static inline lv_color_t next_os_color_separator(void) {
    return lv_color_hex(NEXT_OS_COLOR_SEPARATOR);
}

static inline lv_color_t next_os_color_black(void) {
    return lv_color_hex(NEXT_OS_COLOR_BLACK);
}

static inline lv_color_t next_os_color_dark_tactical(void) {
    return lv_color_hex(NEXT_OS_COLOR_DARK_TACTICAL);
}

static inline lv_color_t next_os_color_dark_separator(void) {
    return lv_color_hex(NEXT_OS_COLOR_DARK_SEPARATOR);
}

static inline lv_color_t next_os_color_blue(void) {
    return lv_color_hex(NEXT_OS_COLOR_BLUE);
}

static inline lv_color_t next_os_color_amber(void) {
    return lv_color_hex(NEXT_OS_COLOR_AMBER);
}

static inline lv_color_t next_os_color_live_green(void) {
    return lv_color_hex(NEXT_OS_COLOR_LIVE_GREEN);
}

static inline void next_os_apply_screen_style(lv_obj_t *screen) {
    lv_obj_set_style_bg_color(screen, next_os_color_cream(), 0);
    lv_obj_set_style_bg_opa(screen, LV_OPA_COVER, 0);
    lv_obj_set_style_border_width(screen, 0, 0);
    lv_obj_set_style_pad_all(screen, 0, 0);
}

static inline void next_os_apply_dark_tactical_style(lv_obj_t *screen) {
    lv_obj_set_style_bg_color(screen, next_os_color_dark_tactical(), 0);
    lv_obj_set_style_bg_opa(screen, LV_OPA_COVER, 0);
    lv_obj_set_style_border_width(screen, 0, 0);
    lv_obj_set_style_pad_all(screen, 0, 0);
}

static inline void next_os_apply_black_screen_style(lv_obj_t *screen) {
    lv_obj_set_style_bg_color(screen, next_os_color_black(), 0);
    lv_obj_set_style_bg_opa(screen, LV_OPA_COVER, 0);
    lv_obj_set_style_border_width(screen, 0, 0);
    lv_obj_set_style_pad_all(screen, 0, 0);
}

#endif /* NEXT_OS_THEME_H */
