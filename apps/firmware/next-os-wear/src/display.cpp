#include "display.h"

#include "config.h"

#include <lvgl.h>

#if defined(NEXT_OS_HARDWARE)
#include <Arduino.h>
#include <Arduino_GFX_Library.h>

/* Pinout referensi LILYGO T-Watch S3 (GC9A01 round) — sesuaikan jika board rev berbeda */
#define TFT_CS 12
#define TFT_DC 11
#define TFT_RST 10
#define TFT_BL 46

static Arduino_DataBus *s_bus = nullptr;
static Arduino_GFX *s_gfx = nullptr;
static lv_display_t *s_disp = nullptr;

static void lvgl_flush_cb(lv_display_t *disp, const lv_area_t *area, uint8_t *px_map) {
    const int32_t w = area->x2 - area->x1 + 1;
    const int32_t h = area->y2 - area->y1 + 1;
    s_gfx->draw16bitRGBBitmap(area->x1, area->y1, reinterpret_cast<uint16_t *>(px_map),
                              static_cast<uint16_t>(w), static_cast<uint16_t>(h));
    lv_display_flush_ready(disp);
}

bool next_os_display_init(void) {
    s_bus = new Arduino_ESP32SPI(TFT_DC, TFT_CS, 38, 39, 40, 41);
    s_gfx = new Arduino_GC9A01(s_bus, TFT_RST, 0, true, NEXT_OS_DISPLAY_WIDTH, NEXT_OS_DISPLAY_HEIGHT);
    if (!s_gfx->begin()) {
        return false;
    }
    pinMode(TFT_BL, OUTPUT);
    digitalWrite(TFT_BL, HIGH);

    lv_init();
    s_disp = lv_display_create(NEXT_OS_DISPLAY_WIDTH, NEXT_OS_DISPLAY_HEIGHT);
    lv_display_set_flush_cb(s_disp, lvgl_flush_cb);
    static lv_color_t buf1[NEXT_OS_DISPLAY_WIDTH * 20];
    static lv_color_t buf2[NEXT_OS_DISPLAY_WIDTH * 20];
    lv_display_set_buffers(s_disp, buf1, buf2, sizeof(buf1), LV_DISPLAY_RENDER_MODE_PARTIAL);
    return true;
}

void next_os_display_lvgl_handler(void) {
    lv_timer_handler();
}

uint16_t next_os_display_width(void) {
    return NEXT_OS_DISPLAY_WIDTH;
}

uint16_t next_os_display_height(void) {
    return NEXT_OS_DISPLAY_HEIGHT;
}

#else

bool next_os_display_init(void) {
    return false;
}

void next_os_display_lvgl_handler(void) {}

uint16_t next_os_display_width(void) {
    return NEXT_OS_DISPLAY_WIDTH;
}

uint16_t next_os_display_height(void) {
    return NEXT_OS_DISPLAY_HEIGHT;
}

#endif
