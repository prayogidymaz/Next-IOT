#ifndef NEXT_OS_NAV_STACK_H
#define NEXT_OS_NAV_STACK_H

#include "screens/screen_manager.h"

void next_os_nav_stack_init(void);

bool next_os_nav_stack_is_ready(void);

void next_os_nav_stack_push(next_os_screen_id_t screen_id, bool animate);
void next_os_nav_stack_pop(void);
void next_os_nav_stack_go_home(void);

uint8_t next_os_nav_stack_depth(void);

#endif /* NEXT_OS_NAV_STACK_H */
