/**
 * Simulator PC — SDL2 + LVGL 9.6 (240×240)
 * Event pointer: timer internal LVGL; keyboard: PeepEvents (tidak mencuri mouse SDL).
 */
#include <SDL2/SDL.h>

#include <cstdint>

#include <lvgl.h>

#include "app.h"
#include "config.h"
#include "screens/screen_manager.h"

static void simulator_handle_keyboard(void) {
    SDL_Event event;
    /* Ambil hanya KEYDOWN — mouse/touch tetap untuk driver LVGL SDL */
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

    lv_init();

    lv_display_t *disp = lv_sdl_window_create(NEXT_OS_DISPLAY_WIDTH, NEXT_OS_DISPLAY_HEIGHT);
    lv_sdl_window_set_title(disp, "Next-OS Wear v1 — Simulator");
    (void)lv_sdl_mouse_create();

    next_os_app_init();
    next_os_screen_manager_tune_pointer_gesture();

    while (lv_is_initialized() && lv_display_get_default() != nullptr) {
        simulator_handle_keyboard();
        lv_timer_handler();
        lv_delay_ms(5);
    }

    return 0;
}
