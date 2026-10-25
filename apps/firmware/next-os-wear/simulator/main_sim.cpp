/**
 * Simulator PC — SDL2 + LVGL 9.6 (240×240)
 * Event SDL ditangani timer internal driver LVGL (lv_sdl_window); loop utama cukup lv_timer_handler().
 */
#include <SDL2/SDL.h>

#include <cstdint>

#include <lvgl.h>
#include <lvgl/drivers/sdl/lv_sdl_mouse.h>
#include <lvgl/drivers/sdl/lv_sdl_window.h>

#include "app.h"
#include "config.h"

static uint32_t s_last_tick = 0;

int SDL_main(int argc, char **argv) {
    (void)argc;
    (void)argv;

    lv_init();

    lv_display_t *disp = lv_sdl_window_create(NEXT_OS_DISPLAY_WIDTH, NEXT_OS_DISPLAY_HEIGHT);
    lv_sdl_window_set_title(disp, "Next-OS Wear v1 — Simulator");
    (void)lv_sdl_mouse_create();

    next_os_app_init();
    s_last_tick = lv_tick_get();

    /* Setelah SDL_QUIT, driver LVGL memanggil lv_deinit() — keluar saat LVGL tidak aktif lagi */
    while (lv_is_initialized()) {
        lv_timer_handler();

        const uint32_t now = lv_tick_get();
        if (now - s_last_tick >= 1000U) {
            s_last_tick = now;
            next_os_app_tick();
        }
    }

    return 0;
}
