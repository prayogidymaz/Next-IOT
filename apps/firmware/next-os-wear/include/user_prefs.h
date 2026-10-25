#ifndef NEXT_OS_USER_PREFS_H
#define NEXT_OS_USER_PREFS_H

#include <stdbool.h>
#include <stdint.h>

typedef enum {
    NEXT_OS_THEME_CREAM = 0,
    NEXT_OS_THEME_TACTICAL_DARK = 1,
} next_os_theme_pref_t;

void next_os_user_prefs_init(void);

next_os_theme_pref_t next_os_user_prefs_theme(void);
void next_os_user_prefs_set_theme(next_os_theme_pref_t theme);

uint8_t next_os_user_prefs_brightness(void);
void next_os_user_prefs_set_brightness(uint8_t pct);

bool next_os_user_prefs_notif_enabled(void);
void next_os_user_prefs_set_notif_enabled(bool enabled);

#endif /* NEXT_OS_USER_PREFS_H */
