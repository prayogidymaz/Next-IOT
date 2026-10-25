#include "runtime_theme.h"

#include "layout.h"
#include "theme.h"
#include "user_prefs.h"

lv_color_t NEXTOS_BG {};
lv_color_t NEXTOS_SURFACE {};
lv_color_t NEXTOS_SURFACE_DIM {};
lv_color_t NEXTOS_BORDER {};
lv_color_t NEXTOS_TEXT_PRIMARY {};
lv_color_t NEXTOS_TEXT_SECONDARY {};
lv_color_t NEXTOS_TEXT_MUTED {};
lv_color_t NEXTOS_ACCENT_PRIMARY {};
lv_color_t NEXTOS_ACCENT_SECONDARY {};
lv_color_t NEXTOS_CRITICAL {};
lv_color_t NEXTOS_SUCCESS {};

static nextos_theme_mode_t s_mode = NEXTOS_THEME_MODE_LIGHT;

static lv_color_t hex(uint32_t v) {
    return lv_color_hex(v);
}

void nextos_theme_apply(nextos_theme_mode_t mode) {
    s_mode = mode;
    if (mode == NEXTOS_THEME_MODE_LIGHT) {
        NEXTOS_BG = hex(NEXTOS_LIGHT_BG_HEX);
        NEXTOS_SURFACE = hex(NEXTOS_LIGHT_SURFACE_HEX);
        NEXTOS_SURFACE_DIM = hex(NEXTOS_LIGHT_SURFACE_DIM_HEX);
        NEXTOS_BORDER = hex(NEXTOS_LIGHT_BORDER_HEX);
        NEXTOS_TEXT_PRIMARY = hex(NEXTOS_LIGHT_TEXT_PRIMARY_HEX);
        NEXTOS_TEXT_SECONDARY = hex(NEXTOS_LIGHT_TEXT_SECONDARY_HEX);
        NEXTOS_TEXT_MUTED = hex(NEXTOS_LIGHT_TEXT_MUTED_HEX);
        NEXTOS_ACCENT_PRIMARY = hex(NEXTOS_LIGHT_ACCENT_PRIMARY_HEX);
        NEXTOS_ACCENT_SECONDARY = hex(NEXTOS_LIGHT_ACCENT_SECONDARY_HEX);
        NEXTOS_CRITICAL = hex(NEXTOS_LIGHT_CRITICAL_HEX);
        NEXTOS_SUCCESS = hex(NEXTOS_LIGHT_SUCCESS_HEX);
        return;
    }
    NEXTOS_BG = hex(NEXTOS_DARK_BG_HEX);
    NEXTOS_SURFACE = hex(NEXTOS_DARK_SURFACE_HEX);
    NEXTOS_SURFACE_DIM = hex(NEXTOS_DARK_SURFACE_DIM_HEX);
    NEXTOS_BORDER = hex(NEXTOS_DARK_BORDER_HEX);
    NEXTOS_TEXT_PRIMARY = hex(NEXTOS_DARK_TEXT_PRIMARY_HEX);
    NEXTOS_TEXT_SECONDARY = hex(NEXTOS_DARK_TEXT_SECONDARY_HEX);
    NEXTOS_TEXT_MUTED = hex(NEXTOS_DARK_TEXT_MUTED_HEX);
    NEXTOS_ACCENT_PRIMARY = hex(NEXTOS_DARK_ACCENT_PRIMARY_HEX);
    NEXTOS_ACCENT_SECONDARY = hex(NEXTOS_DARK_ACCENT_SECONDARY_HEX);
    NEXTOS_CRITICAL = hex(NEXTOS_DARK_CRITICAL_HEX);
    NEXTOS_SUCCESS = hex(NEXTOS_DARK_SUCCESS_HEX);
}

nextos_theme_mode_t nextos_theme_mode(void) {
    return s_mode;
}

void next_os_runtime_theme_init(void) {
    const next_os_theme_pref_t pref = next_os_user_prefs_theme();
    nextos_theme_apply(pref == NEXT_OS_THEME_DARK ? NEXTOS_THEME_MODE_DARK : NEXTOS_THEME_MODE_LIGHT);
}

void next_os_runtime_theme_cycle(void) {
    const nextos_theme_mode_t next =
        s_mode == NEXTOS_THEME_MODE_LIGHT ? NEXTOS_THEME_MODE_DARK : NEXTOS_THEME_MODE_LIGHT;
    nextos_theme_apply(next);
    next_os_user_prefs_set_theme(next == NEXTOS_THEME_MODE_DARK ? NEXT_OS_THEME_DARK : NEXT_OS_THEME_LIGHT);
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
    return NEXTOS_BG;
}

lv_color_t next_os_runtime_color_olive(void) {
    return NEXTOS_ACCENT_PRIMARY;
}

lv_color_t next_os_runtime_color_dark(void) {
    return NEXTOS_TEXT_PRIMARY;
}

lv_color_t next_os_runtime_color_clay(void) {
    return NEXTOS_ACCENT_SECONDARY;
}

lv_color_t next_os_runtime_color_critical(void) {
    return NEXTOS_CRITICAL;
}

lv_color_t next_os_runtime_color_light_grey(void) {
    return NEXTOS_BORDER;
}

lv_color_t next_os_runtime_color_muted(void) {
    return NEXTOS_TEXT_MUTED;
}

lv_color_t next_os_runtime_color_separator(void) {
    return NEXTOS_BORDER;
}

lv_color_t next_os_runtime_color_black(void) {
    return hex(NEXTOS_DARK_BG_HEX);
}

lv_color_t next_os_runtime_color_dark_tactical(void) {
    return NEXTOS_BG;
}

lv_color_t next_os_runtime_color_dark_separator(void) {
    return NEXTOS_BORDER;
}

lv_color_t next_os_runtime_color_blue(void) {
    return hex(0x3B82F6);
}

lv_color_t next_os_runtime_color_amber(void) {
    return hex(0xF59E0B);
}

lv_color_t next_os_runtime_color_live_green(void) {
    return NEXTOS_SUCCESS;
}

void next_os_apply_screen_style(lv_obj_t *screen) {
    lv_obj_set_style_bg_color(screen, NEXTOS_BG, 0);
    lv_obj_set_style_bg_opa(screen, LV_OPA_COVER, 0);
    lv_obj_set_style_border_width(screen, 0, 0);
    lv_obj_set_style_pad_all(screen, 0, 0);
}

void next_os_apply_dark_tactical_style(lv_obj_t *screen) {
    lv_obj_set_style_bg_color(screen, NEXTOS_BG, 0);
    lv_obj_set_style_bg_opa(screen, LV_OPA_COVER, 0);
    lv_obj_set_style_border_width(screen, 0, 0);
    lv_obj_set_style_pad_all(screen, 0, 0);
}

void next_os_apply_black_screen_style(lv_obj_t *screen) {
    lv_obj_set_style_bg_color(screen, hex(NEXTOS_DARK_BG_HEX), 0);
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
