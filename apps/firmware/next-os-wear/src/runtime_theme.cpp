#include "runtime_theme.h"

#include "layout.h"

static next_os_theme_pref_t s_active = NEXT_OS_THEME_CREAM;

static lv_color_t from_hex(uint32_t hex) {
    return lv_color_hex(hex);
}

void next_os_runtime_theme_init(void) {
    s_active = next_os_user_prefs_theme();
}

void next_os_runtime_theme_cycle(void) {
    s_active = (s_active == NEXT_OS_THEME_CREAM) ? NEXT_OS_THEME_TACTICAL_DARK : NEXT_OS_THEME_CREAM;
    next_os_user_prefs_set_theme(s_active);
    s_active = next_os_user_prefs_theme();
}

void next_os_runtime_theme_apply_global_refresh(void) {
    lv_obj_t *scr = lv_screen_active();
    if (scr != nullptr) {
        lv_obj_invalidate(scr);
    }
    lv_display_t *disp = lv_display_get_default();
    if (disp != nullptr) {
        lv_refr_now(disp);
    }
}

lv_color_t next_os_runtime_color_cream(void) {
    return s_active == NEXT_OS_THEME_CREAM ? from_hex(0xF5EFE0) : from_hex(0x1C1F18);
}

lv_color_t next_os_runtime_color_olive(void) {
    return s_active == NEXT_OS_THEME_CREAM ? from_hex(0x556B4A) : from_hex(0x8FA882);
}

lv_color_t next_os_runtime_color_dark(void) {
    return s_active == NEXT_OS_THEME_CREAM ? from_hex(0x1F1F1F) : from_hex(0xF5EFE0);
}

lv_color_t next_os_runtime_color_clay(void) {
    return from_hex(0xD97757);
}

lv_color_t next_os_runtime_color_critical(void) {
    return from_hex(0xB23A3A);
}

lv_color_t next_os_runtime_color_light_grey(void) {
    return s_active == NEXT_OS_THEME_CREAM ? from_hex(0xB8B2A6) : from_hex(0x5A5A52);
}

lv_color_t next_os_runtime_color_muted(void) {
    return s_active == NEXT_OS_THEME_CREAM ? from_hex(0x6B6B63) : from_hex(0x9A9A90);
}

lv_color_t next_os_runtime_color_separator(void) {
    return s_active == NEXT_OS_THEME_CREAM ? from_hex(0xD0C7B0) : from_hex(0x2E3328);
}

lv_color_t next_os_runtime_color_black(void) {
    return from_hex(0x0A0A0A);
}

lv_color_t next_os_runtime_color_dark_tactical(void) {
    return from_hex(0x1C1F18);
}

lv_color_t next_os_runtime_color_dark_separator(void) {
    return from_hex(0x2E3328);
}

lv_color_t next_os_runtime_color_blue(void) {
    return from_hex(0x4A7FB8);
}

lv_color_t next_os_runtime_color_amber(void) {
    return from_hex(0xD4A017);
}

lv_color_t next_os_runtime_color_live_green(void) {
    return from_hex(0x3DAA63);
}

void next_os_apply_screen_style(lv_obj_t *screen) {
    lv_obj_set_style_bg_color(screen, next_os_runtime_color_cream(), 0);
    lv_obj_set_style_bg_opa(screen, LV_OPA_COVER, 0);
    lv_obj_set_style_border_width(screen, 0, 0);
    lv_obj_set_style_pad_all(screen, 0, 0);
}

void next_os_apply_dark_tactical_style(lv_obj_t *screen) {
    lv_obj_set_style_bg_color(screen, next_os_runtime_color_dark_tactical(), 0);
    lv_obj_set_style_bg_opa(screen, LV_OPA_COVER, 0);
    lv_obj_set_style_border_width(screen, 0, 0);
    lv_obj_set_style_pad_all(screen, 0, 0);
}

void next_os_apply_black_screen_style(lv_obj_t *screen) {
    lv_obj_set_style_bg_color(screen, next_os_runtime_color_black(), 0);
    lv_obj_set_style_bg_opa(screen, LV_OPA_COVER, 0);
    lv_obj_set_style_border_width(screen, 0, 0);
    lv_obj_set_style_pad_all(screen, 0, 0);
}

const lv_font_t *next_os_font_clock_large(void) {
    const int scale = nextos_font_scaled(48);
    if (scale >= 44) {
        return &lv_font_montserrat_48;
    }
    if (scale >= 34) {
        return &lv_font_montserrat_36;
    }
    return &lv_font_montserrat_24;
}
