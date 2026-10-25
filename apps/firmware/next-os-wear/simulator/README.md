# Simulator PC (alternatif CMake)

PlatformIO adalah jalur utama (`pio run -e simulator -t exec`).

Jika SDL2 sudah terpasang via MSYS2/vcpkg:

```bash
cd apps/firmware/next-os-wear/simulator
cmake -B build -DCMAKE_PREFIX_PATH="C:/path/to/SDL2"
cmake --build build
./build/next_os_wear_sim
```

Perlu menautkan LVGL secara manual di CMake (Week 3+); untuk saat ini gunakan PlatformIO.
