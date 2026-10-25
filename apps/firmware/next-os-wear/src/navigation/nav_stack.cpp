#include "navigation/nav_stack.h"

#include "screens/screen_manager.h"

static next_os_screen_id_t s_stack[10];
static uint8_t s_depth = 0;

void next_os_nav_stack_init(void) {
    s_depth = 0;
}

void next_os_nav_stack_push(next_os_screen_id_t screen_id, bool animate) {
    if (!next_os_screen_manager_is_stackable(screen_id)) {
        return;
    }
    if (s_depth >= 10U) {
        return;
    }
    s_stack[s_depth] = screen_id;
    s_depth++;
    next_os_screen_manager_present(screen_id, animate);
}

void next_os_nav_stack_pop(void) {
    if (s_depth == 0U) {
        next_os_nav_stack_go_home();
        return;
    }
    s_depth--;
    if (s_depth == 0U) {
        next_os_screen_manager_present(NEXT_OS_SCREEN_WATCH_FACE, true);
        return;
    }
    next_os_screen_manager_present(s_stack[s_depth - 1U], true);
}

void next_os_nav_stack_go_home(void) {
    s_depth = 0;
    next_os_screen_manager_present(NEXT_OS_SCREEN_WATCH_FACE, true);
}

uint8_t next_os_nav_stack_depth(void) {
    return s_depth;
}
