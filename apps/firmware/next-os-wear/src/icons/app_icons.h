#ifndef NEXT_OS_APP_ICONS_H
#define NEXT_OS_APP_ICONS_H

#include "screens/screen_manager.h"

typedef struct {
    next_os_screen_id_t screen_id;
    const char *symbol;
    const char *label;
} next_os_app_icon_entry_t;

uint8_t next_os_app_icon_count(void);
const next_os_app_icon_entry_t *next_os_app_icon_at(uint8_t index);

#endif /* NEXT_OS_APP_ICONS_H */
