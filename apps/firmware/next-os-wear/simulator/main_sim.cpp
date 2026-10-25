/**
 * Simulator PC — SDL2 + LVGL 9 (240×240)
 * Build: set SDL2_PATH lalu `pio run -e simulator -t exec`
 */
#include "app.h"
#include "config.h"

#include <lvgl.h>

#if LV_USE_SDL
#include <SDL2/SDL.h>

#include "drivers/sdl/lv_sdl_window.h"
#include "drivers/sdl/lv_sdl_mouse.h"
#endif

#include <cstdint>

static uint32_t s_last_tick = 0;

#if LV_USE_SDL
static uint32_t sdl_tick_cb(void) {
    return static_cast<uint32_t>(SDL_GetTicks());
}
#endif

int main(void) {
    lv_init();

#if LV_USE_SDL
    lv_tick_set_cb(sdl_tick_cb);
    lv_display_t *disp = lv_sdl_window_create(NEXT_OS_DISPLAY_WIDTH, NEXT_OS_DISPLAY_HEIGHT);
    lv_sdl_window_set_title(disp, "Next-OS Wear v1 — Simulator");
    (void)lv_sdl_mouse_create();
#endif

    next_os_app_init();

    while (true) {
#if LV_USE_SDL
        if (lv_sdl_quit()) {
            break;
        }
        lv_sdl_window_handle_events();
#endif
        lv_timer_handler();

        const uint32_t now = lv_tick_get();
        if (now - s_last_tick >= 1000U) {
            s_last_tick = now;
            next_os_app_tick();
        }
        lv_delay_ms(5);
    }

    return 0;
}
