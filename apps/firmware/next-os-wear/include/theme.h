/**
 * Tactical Warm Cream — kontrak warna UI Next-OS Wear v1 (runtime palette).
 */
#ifndef NEXT_OS_THEME_H
#define NEXT_OS_THEME_H

#include <lvgl.h>

#include "runtime_theme.h"

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

static inline lv_color_t next_os_color_cream(void) {
    return next_os_runtime_color_cream();
}

static inline lv_color_t next_os_color_olive(void) {
    return next_os_runtime_color_olive();
}

static inline lv_color_t next_os_color_dark(void) {
    return next_os_runtime_color_dark();
}

static inline lv_color_t next_os_color_clay(void) {
    return next_os_runtime_color_clay();
}

static inline lv_color_t next_os_color_critical(void) {
    return next_os_runtime_color_critical();
}

static inline lv_color_t next_os_color_light_grey(void) {
    return next_os_runtime_color_light_grey();
}

static inline lv_color_t next_os_color_muted(void) {
    return next_os_runtime_color_muted();
}

static inline lv_color_t next_os_color_separator(void) {
    return next_os_runtime_color_separator();
}

static inline lv_color_t next_os_color_black(void) {
    return next_os_runtime_color_black();
}

static inline lv_color_t next_os_color_dark_tactical(void) {
    return next_os_runtime_color_dark_tactical();
}

static inline lv_color_t next_os_color_dark_separator(void) {
    return next_os_runtime_color_dark_separator();
}

static inline lv_color_t next_os_color_blue(void) {
    return next_os_runtime_color_blue();
}

static inline lv_color_t next_os_color_amber(void) {
    return next_os_runtime_color_amber();
}

static inline lv_color_t next_os_color_live_green(void) {
    return next_os_runtime_color_live_green();
}

#endif /* NEXT_OS_THEME_H */
