# Next-OS Wear v1 (Native Firmware)

Firmware native untuk **LILYGO T-Watch S3** (ESP32-S3, layar bulat GC9A01 240×240, touch CST816D). Branding produk: **Next-OS Wear v1**, terintegrasi dengan platform Next-IOT (MQTT + HTTP).

Tanpa hardware fisik, UI bisa diuji di **simulator PC** (SDL2 + LVGL 9).

## Struktur singkat

| Path | Fungsi |
|------|--------|
| `src/` | Entry point, driver, layar LVGL |
| `include/` | `config.h`, `theme.h`, `lv_conf.h` |
| `simulator/` | Entry SDL untuk Windows/Linux |
| `docs/` | Panduan setup, arsitektur, referensi UI |
| `test/` | Unit test tema (env `native`) |

## Mulai cepat (simulator)

1. Baca [docs/setup-guide.md](docs/setup-guide.md) lengkap.
2. Pasang SDL2, set variabel lingkungan `SDL2_PATH` (folder yang berisi `include/` dan `lib/`).
3. Buka folder ini di VS Code + ekstensi PlatformIO.

```powershell
cd apps/firmware/next-os-wear
$env:SDL2_PATH = "C:\path\ke\SDL2"   # contoh: scoop install sdl2
pio run -e simulator -t exec
```

Harapan: jendela 240×240, animasi boot ~2 detik, lalu layar Hello World (jam analog + KPI dummy).

## Flash hardware (setelah T-Watch datang)

```powershell
pio run -e lilygo-t-watch-s3 -t upload
pio run -e lilygo-t-watch-s3 -t monitor
```

## Dokumen

- [Panduan setup (Prayogi)](docs/setup-guide.md)
- [Arsitektur](docs/architecture.md)
- [Referensi UI](docs/ui-reference.md)

## Lisensi / tim

Dikembangkan untuk NextGrow / Next-IOT. Komentar kode berbahasa Indonesia agar konsisten untuk tim lokal.
