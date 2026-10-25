#include "user_prefs.h"

#include <cstdio>

#if defined(NEXT_OS_HARDWARE)
#include <Preferences.h>
#endif

static next_os_theme_pref_t s_theme = NEXT_OS_THEME_CREAM;
static uint8_t s_brightness = 70;
static bool s_notif = true;

#if defined(NEXT_OS_HARDWARE)
static Preferences s_prefs;
#endif

void next_os_user_prefs_init(void) {
#if defined(NEXT_OS_HARDWARE)
    s_prefs.begin("nextos_wear", false);
    s_theme = static_cast<next_os_theme_pref_t>(s_prefs.getUChar("theme", NEXT_OS_THEME_CREAM));
    s_brightness = s_prefs.getUChar("bright", 70);
    s_notif = s_prefs.getBool("notif", true);
#else
    s_theme = NEXT_OS_THEME_CREAM;
    s_brightness = 70;
    s_notif = true;
#endif
}

next_os_theme_pref_t next_os_user_prefs_theme(void) {
    return s_theme;
}

void next_os_user_prefs_set_theme(next_os_theme_pref_t theme) {
    s_theme = theme;
#if defined(NEXT_OS_HARDWARE)
    s_prefs.putUChar("theme", static_cast<uint8_t>(theme));
#endif
}

uint8_t next_os_user_prefs_brightness(void) {
    return s_brightness;
}

void next_os_user_prefs_set_brightness(uint8_t pct) {
    if (pct < 10) {
        pct = 10;
    }
    if (pct > 100) {
        pct = 100;
    }
    s_brightness = pct;
#if defined(NEXT_OS_HARDWARE)
    s_prefs.putUChar("bright", pct);
#else
    (void)std::printf("[PREFS] brightness=%u (simulator — no backlight)\n", static_cast<unsigned>(pct));
#endif
}

bool next_os_user_prefs_notif_enabled(void) {
    return s_notif;
}

void next_os_user_prefs_set_notif_enabled(bool enabled) {
    s_notif = enabled;
#if defined(NEXT_OS_HARDWARE)
    s_prefs.putBool("notif", enabled);
#endif
}
