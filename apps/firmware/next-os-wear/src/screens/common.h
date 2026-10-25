/**
 * Helper UI bersama — layar round 240×240 (Artifact preview 01–04)
 */
#ifndef NEXT_OS_SCREENS_COMMON_H
#define NEXT_OS_SCREENS_COMMON_H

#include <lvgl.h>

#include "theme.h"

#define NEXT_OS_SCREEN_PAD 12
#define NEXT_OS_SCREEN_SAFE_TOP 14
#define NEXT_OS_TILE_GAP 6

/** Label header atas (Montserrat — nanti JetBrains Mono) */
lv_obj_t *next_os_common_create_header_label(lv_obj_t *parent, const char *text);

/** Kontainer bulat / kartu dengan radius penuh */
lv_obj_t *next_os_common_create_round_container(lv_obj_t *parent, int32_t size);

/** Garis pemisah vertikal tipis antar KPI */
lv_obj_t *next_os_common_create_v_separator(lv_obj_t *parent);

/** Indikator pagination (3 dot) — active_index 0..dot_count-1 */
void next_os_common_create_pagination_dots(lv_obj_t *parent, uint8_t dot_count, uint8_t active_index);

/** Tombol ◀ / ▶ di pojok atas (nav utama di simulator + touch) */
lv_obj_t *next_os_common_create_nav_buttons(lv_obj_t *screen);

/** Pasang deteksi swipe kiri/kanan pada layar (mouse drag di simulator) */
void next_os_common_attach_swipe_navigation(lv_obj_t *screen);

/** Nonaktifkan scroll pada kontainer statis (ganti remove_flag SCROLLABLE) */
void next_os_common_disable_scroll(lv_obj_t *obj);

#endif /* NEXT_OS_SCREENS_COMMON_H */
