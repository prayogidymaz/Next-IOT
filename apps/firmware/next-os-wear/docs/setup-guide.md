# Panduan Setup — Next-OS Wear v1 (Week 1–2)

Panduan step-by-step untuk developer (Prayogi & tim) menyiapkan lingkungan **tanpa hardware** dulu, lalu flash ke LILYGO T-Watch S3 ketika perangkat sudah tiba.

## 1. Prasyarat

- Windows 10/11 (64-bit)
- Git
- Koneksi internet (unduh toolchain PlatformIO + library LVGL)

## 2. Install VS Code

1. Unduh [Visual Studio Code](https://code.visualstudio.com/).
2. Install seperti aplikasi biasa.

## 3. Install PlatformIO

1. Buka VS Code → **Extensions** (Ctrl+Shift+X).
2. Cari **PlatformIO IDE** → Install.
3. Restart VS Code jika diminta.

## 4. SquareLine Studio (opsional)

Untuk edit visual UI LVGL nanti (Week 3+):

- Unduh [SquareLine Studio](https://squareline.io/) (versi yang mendukung LVGL 9).
- Export asset ke folder proyek sesuai dokumentasi SquareLine.

Tidak wajib untuk Week 1–2; layar boot & Hello World sudah ditulis manual di `src/screens/`.

## 5. Clone monorepo & buka proyek firmware

```powershell
git clone <url-repo-next-iot>
cd Next-IOT/apps/firmware/next-os-wear
```

Di VS Code: **File → Open Folder** → pilih `apps/firmware/next-os-wear`.

## 6. Install SDL2 (simulator PC)

Simulator membutuhkan **SDL2** di PATH build (bukan di runtime ESP32).

### Opsi A — Scoop (disarankan di Windows)

```powershell
scoop install sdl2
# Biasanya: C:\Users\<user>\scoop\apps\sdl2\current
$env:SDL2_PATH = "$env:USERPROFILE\scoop\apps\sdl2\current"
```

### Opsi B — MSYS2

```bash
pacman -S mingw-w64-x86_64-SDL2
# Set SDL2_PATH ke prefix MSYS2 (folder dengan include/SDL2 dan lib)
```

### Opsi C — Unduh manual

1. [SDL2 development libraries](https://github.com/libsdl-org/SDL/releases) (VC zip).
2. Ekstrak, misalnya `C:\SDL2`.
3. Pastikan ada `C:\SDL2\include\SDL2\SDL.h` dan `C:\SDL2\lib\x64\SDL2.lib`.

```powershell
$env:SDL2_PATH = "C:\SDL2"
```

**Catatan:** Set `SDL2_PATH` di setiap sesi terminal baru, atau tambahkan ke variabel lingkungan Windows permanen.

## 7. First run — simulator

```powershell
cd apps/firmware/next-os-wear
pio run -e simulator -t exec
```

**Yang diharapkan:**

1. PlatformIO mengunduh LVGL 9.x (pertama kali agak lama).
2. Jendela SDL 240×240 terbuka.
3. Boot: fade-in + arc berputar, label **NEXT-IOT** / **Next-OS Wear**.
4. Setelah ~2 detik → layar **NEXT-OS WEAR v1.0.0-dev**, jam analog, teks KPI `0 FARM • 0 ALERT • 0 IRIG`.

**Loop pengembangan:** edit file di `src/screens/` → jalankan ulang `pio run -e simulator -t exec` → verifikasi UI → baru flash ke hardware.

Jika SDL2 belum terpasang, Anda tetap bisa review struktur folder, `platformio.ini`, dan dokumen ini; build simulator akan gagal di tahap link SDL.

## 8. Unit test tema (opsional)

```powershell
pio test -e native
```

Memverifikasi konstanta warna Tactical Warm Cream di `include/theme.h`.

## 9. First flash — hardware (setelah LILYGO T-Watch S3 datang)

1. Hubungkan T-Watch via **USB-C** (kabel data, bukan charge-only).
2. Driver: biasanya **USB Serial/JTAG** ESP32-S3 (Windows Update atau [driver Espressif](https://docs.espressif.com/projects/esp-idf/en/latest/esp32s3/get-started/establish-serial-connection.html)).
3. Cek port COM di Device Manager.

```powershell
pio run -e lilygo-t-watch-s3 -t upload
pio run -e lilygo-t-watch-s3 -t monitor
```

Serial monitor 115200: pesan `Next-OS Wear v1 boot`, lalu UI sama seperti simulator (lewat driver GC9A01).

### Mode boot / upload gagal

- Tahan tombol **BOOT** saat colok USB, lepas setelah upload dimulai.
- Ganti kabel USB atau port.
- Kurangi `upload_speed` di `platformio.ini` jika sering timeout.
- Pastikan env benar: `lilygo-t-watch-s3`, bukan `simulator`.

## 10. Konfigurasi WiFi (placeholder)

Edit `include/config.h` atau gunakan `build_flags` di `platformio.ini`:

```ini
build_flags =
    -D NEXT_OS_WIFI_SSID=\"LAB-WIFI\"
    -D NEXT_OS_WIFI_PASSWORD=\"rahasia\"
```

Jangan commit password produksi.

## 11. Troubleshooting

| Gejala | Kemungkinan | Solusi |
|--------|-------------|--------|
| `SDL2.h not found` | `SDL2_PATH` salah | Perbaiki path, pastikan `include/SDL2/SDL.h` ada |
| Link error `SDL2.lib` | Lib 32 vs 64 bit | Pakai lib x64 untuk toolchain native PlatformIO |
| Upload `Failed to connect` | Port / driver | BOOT mode, ganti kabel, pilih port `pio device list` |
| Layar putih di hardware | Pinout / rev board | Cek pin di `src/display.cpp`, dokumentasi LILYGO |
| WiFi tidak connect | SSID salah | UI tetap jalan offline; perbaiki `config.h` |

## 12. Kontak & dokumen lanjutan

- Arsitektur: [architecture.md](architecture.md)
- Kontrak UI: [ui-reference.md](ui-reference.md)
- README root proyek: [../README.md](../README.md)
