# Referensi UI — Next-OS Wear v1

## Sumber desain

Visual utama mengacu pada **Artifact UI preview — 12 artboard** (round watch, square companion, grafik unik). Simpan link internal tim di sini:

- **Artboard 12 (round 240×240):** `[tautkan URL Figma/Artifact tim Anda]`
- Kontrak: **setiap layar di preview = target implementasi LVGL** dengan warna & hierarki yang sama.

Jika link belum dipublikasikan di repo, minta akses ke lead desain Next-IOT; jangan mengganti palet tanpa menyelaraskan `include/theme.h`.

## Palet Tactical Warm Cream (wajib)

| Token | Hex | Pemakaian |
|-------|-----|-----------|
| Cream | `#F5EFE0` | Background layar |
| Olive | `#556B4A` | Header, border jam, aksen |
| Dark | `#1F1F1F` | Teks utama, face jam |
| Clay | `#D97757` | Indikator boot, jarum menit |
| Critical | `#B23A3A` | Alert (fase berikutnya) |

Definisi kode: `include/theme.h`.

## Font

| Peran | Font desain | Status firmware |
|-------|-------------|-----------------|
| Versi / mono KPI | **JetBrains Mono** | Week 1–2: Montserrat LVGL default; konversi binary minggu berikutnya |
| Body / label | **Inter** | Idem — gunakan [LVGL Font Converter](https://lvgl.io/tools/fontconverter) |

Setelah konversi, letakkan `.c` di `src/assets/fonts/` dan set `LV_FONT_CUSTOM_DECLARE` di `lv_conf.h`.

## Prioritas implementasi layar

1. **Boot** — logo Next-IOT, animasi 2s (`screens/boot.cpp`) ✅ skeleton
2. **Watch face** — jam digital + KPI farm/alert/irig (`screens/watch_face.cpp`) ✅ MVP
3. **Sensor monitor** — daftar node + sparkline (belum)
4. **Irrigation control** — toggle zone + countdown (belum)
5. **Alert center** — daftar prioritas + acknowledge (belum)

## Round display (240×240)

- Safe area: padding ~12 px dari tepi lingkaran; hindari teks di sudut terpotong.
- Touch target minimum ~40×40 px (LVGL padding).
- Boot & watch face sudah di-center; screen berikutnya gunakan `lv_obj_set_style_clip_corner` jika perlu mask bulat.

## Simulator vs perangkat

Verifikasi di `pio run -e simulator -t exec` sebelum flash. Perbedaan kecil gamma GC9A01 vs SDL normal — kalibrasi di hardware nanti.

## Checklist review UI

- [ ] Warna match `theme.h`
- [ ] Boot 2 detik lalu transisi halus
- [ ] Teks versi sesuai `NEXT_OS_FIRMWARE_VERSION` di `config.h`
- [ ] KPI placeholder konsisten dengan mock data platform (nanti dari MQTT)
