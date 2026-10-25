#include "navigation/nav_stack.h"

#include "screens/screen_manager.h"

#include <cstdio>

static next_os_screen_id_t s_stack[10];
static uint8_t s_depth = 0;
static bool s_ready = false;

static bool nav_stack_screen_id_valid(next_os_screen_id_t screen_id) {
    if (screen_id < NEXT_OS_SCREEN_WATCH_FACE || screen_id > NEXT_OS_SCREEN_ABOUT) {
        return false;
    }
    return next_os_screen_manager_is_stackable(screen_id);
}

void next_os_nav_stack_init(void) {
    s_depth = 0;
    s_ready = true;
    (void)std::printf("[NAV] stack initialized depth=0\n");
    (void)std::fflush(stdout);
}

bool next_os_nav_stack_is_ready(void) {
    return s_ready;
}

void next_os_nav_stack_push(next_os_screen_id_t screen_id, bool animate) {
    if (!s_ready) {
        (void)std::printf("[NAV] push ignored - stack not ready id=%d\n", static_cast<int>(screen_id));
        (void)std::fflush(stdout);
        return;
    }
    if (!nav_stack_screen_id_valid(screen_id)) {
        (void)std::printf("[NAV] push rejected invalid id=%d\n", static_cast<int>(screen_id));
        (void)std::fflush(stdout);
        return;
    }
    if (s_depth >= 10U) {
        (void)std::printf("[NAV] push rejected - stack full\n");
        (void)std::fflush(stdout);
        return;
    }
    s_stack[s_depth] = screen_id;
    s_depth++;
    (void)std::printf("[NAV] push id=%d depth=%u\n", static_cast<int>(screen_id),
                      static_cast<unsigned>(s_depth));
    (void)std::fflush(stdout);
    next_os_screen_manager_present(screen_id, animate);
}

void next_os_nav_stack_pop(void) {
    if (!s_ready) {
        (void)std::printf("[NAV] pop ignored - stack not ready\n");
        (void)std::fflush(stdout);
        return;
    }
    if (s_depth == 0U) {
        next_os_nav_stack_go_home();
        return;
    }
    s_depth--;
    (void)std::printf("[NAV] pop depth=%u\n", static_cast<unsigned>(s_depth));
    (void)std::fflush(stdout);
    if (s_depth == 0U) {
        next_os_screen_manager_present(NEXT_OS_SCREEN_WATCH_FACE, true);
        return;
    }
    const next_os_screen_id_t target = s_stack[s_depth - 1U];
    if (!nav_stack_screen_id_valid(target)) {
        next_os_nav_stack_go_home();
        return;
    }
    next_os_screen_manager_present(target, true);
}

void next_os_nav_stack_go_home(void) {
    if (!s_ready) {
        (void)std::printf("[NAV] go_home ignored - stack not ready\n");
        (void)std::fflush(stdout);
        return;
    }
    s_depth = 0;
    (void)std::printf("[NAV] go_home -> watch face\n");
    (void)std::fflush(stdout);
    next_os_screen_manager_present(NEXT_OS_SCREEN_WATCH_FACE, true);
}

uint8_t next_os_nav_stack_depth(void) {
    return s_depth;
}
