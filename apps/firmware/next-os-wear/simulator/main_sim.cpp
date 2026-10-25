/**
 * Simulator PC — SDL2 + LVGL 9.6 (240×240)
 * Event pointer: timer internal LVGL; keyboard: PeepEvents (tidak mencuri mouse SDL).
 */
#include <SDL2/SDL.h>

#include <cstdio>
#include <cstdint>

#include <lvgl.h>

#include "app.h"
#include "config.h"
#include "layout.h"
#include "mqtt.h"
#include "navigation/nav_stack.h"
#include "screens/screen_manager.h"

static void simulator_handle_keyboard(void) {
    SDL_Event event;
    while (SDL_PeepEvents(&event, 1, SDL_GETEVENT, SDL_KEYDOWN, SDL_KEYDOWN) > 0) {
        if (event.key.keysym.sym == SDLK_LEFT) {
            next_os_screen_manager_prev();
        } else if (event.key.keysym.sym == SDLK_RIGHT) {
            next_os_screen_manager_next();
        }
    }
}

int SDL_main(int argc, char **argv) {
    (void)argc;
    (void)argv;

    (void)std::printf("[BOOT] Starting Next-OS Wear simulator\n");
    (void)std::fflush(stdout);

    lv_init();
    (void)std::printf("[BOOT] 1. LVGL init done\n");
    (void)std::fflush(stdout);

    lv_display_t *disp = lv_sdl_window_create(NEXT_OS_DISPLAY_WIDTH, NEXT_OS_DISPLAY_HEIGHT);
    if (disp == nullptr) {
        (void)std::printf("[BOOT] FATAL: SDL display create failed\n");
        (void)std::fflush(stdout);
        return 1;
    }
    lv_sdl_window_set_title(disp, "Next-OS Wear v1 — Simulator");
    (void)std::printf("[BOOT] 2. SDL display created %dx%d\n", NEXTOS_W, NEXTOS_H);
    (void)std::fflush(stdout);

    lv_indev_t *mouse = lv_sdl_mouse_create();
    if (mouse == nullptr) {
        (void)std::printf("[BOOT] WARN: SDL mouse indev null\n");
        (void)std::fflush(stdout);
    }
    (void)std::printf("[BOOT] 3. SDL mouse created\n");
    (void)std::fflush(stdout);

    next_os_nav_stack_init();
    (void)std::printf("[BOOT] nav_stack initialized (pre-app)\n");
    (void)std::fflush(stdout);

    (void)std::printf("[BOOT] 4. next_os_app_init() calling\n");
    (void)std::fflush(stdout);
    next_os_app_init();
    (void)std::printf("[BOOT] 5. next_os_app_init() returned\n");
    (void)std::fflush(stdout);

    next_os_screen_manager_tune_pointer_gesture();

    (void)std::printf("[BOOT] 6. Entering event loop\n");
    (void)std::fflush(stdout);

    while (lv_is_initialized() && lv_display_get_default() != nullptr) {
        simulator_handle_keyboard();
        lv_timer_handler();
        next_os_app_tick();
        lv_delay_ms(5);
    }

    (void)std::printf("[BOOT] Event loop exited cleanly\n");
    (void)std::fflush(stdout);
    return 0;
}
