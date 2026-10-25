/**
 * Modern UI palette — Light (clean white) + Dark (OLED).
 */
#ifndef NEXT_OS_THEME_H
#define NEXT_OS_THEME_H

#include <lvgl.h>

#define NEXTOS_LIGHT_BG_HEX 0xFAFBFC
#define NEXTOS_LIGHT_SURFACE_HEX 0xFFFFFF
#define NEXTOS_LIGHT_SURFACE_DIM_HEX 0xF1F3F5
#define NEXTOS_LIGHT_BORDER_HEX 0xE2E8F0
#define NEXTOS_LIGHT_TEXT_PRIMARY_HEX 0x0F172A
#define NEXTOS_LIGHT_TEXT_SECONDARY_HEX 0x475569
#define NEXTOS_LIGHT_TEXT_MUTED_HEX 0x94A3B8
#define NEXTOS_LIGHT_ACCENT_PRIMARY_HEX 0x10B981
#define NEXTOS_LIGHT_ACCENT_SECONDARY_HEX 0xF97316
#define NEXTOS_LIGHT_CRITICAL_HEX 0xEF4444
#define NEXTOS_LIGHT_SUCCESS_HEX 0x10B981

#define NEXTOS_DARK_BG_HEX 0x0A0A0B
#define NEXTOS_DARK_SURFACE_HEX 0x18181B
#define NEXTOS_DARK_SURFACE_DIM_HEX 0x27272A
#define NEXTOS_DARK_BORDER_HEX 0x3F3F46
#define NEXTOS_DARK_TEXT_PRIMARY_HEX 0xF8FAFC
#define NEXTOS_DARK_TEXT_SECONDARY_HEX 0xCBD5E1
#define NEXTOS_DARK_TEXT_MUTED_HEX 0x64748B
#define NEXTOS_DARK_ACCENT_PRIMARY_HEX 0x34D399
#define NEXTOS_DARK_ACCENT_SECONDARY_HEX 0xFB923C
#define NEXTOS_DARK_CRITICAL_HEX 0xF87171
#define NEXTOS_DARK_SUCCESS_HEX 0x4ADE80

typedef enum {
    NEXTOS_THEME_MODE_LIGHT = 0,
    NEXTOS_THEME_MODE_DARK = 1,
} nextos_theme_mode_t;

extern lv_color_t NEXTOS_BG;
extern lv_color_t NEXTOS_SURFACE;
extern lv_color_t NEXTOS_SURFACE_DIM;
extern lv_color_t NEXTOS_BORDER;
extern lv_color_t NEXTOS_TEXT_PRIMARY;
extern lv_color_t NEXTOS_TEXT_SECONDARY;
extern lv_color_t NEXTOS_TEXT_MUTED;
extern lv_color_t NEXTOS_ACCENT_PRIMARY;
extern lv_color_t NEXTOS_ACCENT_SECONDARY;
extern lv_color_t NEXTOS_CRITICAL;
extern lv_color_t NEXTOS_SUCCESS;

void nextos_theme_apply(nextos_theme_mode_t mode);
nextos_theme_mode_t nextos_theme_mode(void);

#include "runtime_theme.h"

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
