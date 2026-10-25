/**
 * Simulator PC — SDL2 + LVGL 9.6 (240×240)
 * Event SDL ditangani timer internal driver LVGL (lv_sdl_window); loop utama cukup lv_timer_handler().
 */
#include <SDL2/SDL.h>

#include <cstdint>

#include <lvgl.h>

#include "app.h"
#include "config.h"

int SDL_main(int argc, char **argv) {
    (void)argc;
    (void)argv;

    lv_init();

    lv_display_t *disp = lv_sdl_window_create(NEXT_OS_DISPLAY_WIDTH, NEXT_OS_DISPLAY_HEIGHT);
    lv_sdl_window_set_title(disp, "Next-OS Wear v1 — Simulator");
    (void)lv_sdl_mouse_create();

    next_os_app_init();

    /*
     * Tutup jendela (X) → lv_display_delete → default display NULL.
     * Jangan lv_timer_handler() setelah itu (access violation).
     */
    while (lv_is_initialized() && lv_display_get_default() != nullptr) {
        lv_timer_handler();
        lv_delay_ms(5);
    }

    return 0;
}
