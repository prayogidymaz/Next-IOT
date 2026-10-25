"""
PlatformIO pre-script: tautkan SDL2 untuk env native/simulator (Windows/Linux).
- Include: SDL2_PATH atau Scoop sdl2
- Link: lib MinGW (libSDL2.dll.a) atau import lib Scoop (SDL2main.lib + SDL2.lib)
  harus di akhir rantai link (setelah liblvgl.a) → pakai env LIBS, bukan LINKFLAGS -l.
"""

import os
import sys

from SCons.Script import Copy

Import("env")


def _sdl2_header_path(root):
    return os.path.join(root, "include", "SDL2", "SDL.h")


def _resolve_sdl2_root():
    candidates = []
    from_env = os.environ.get("SDL2_PATH", "").strip()
    if from_env:
        candidates.append(from_env)
    user_profile = os.environ.get("USERPROFILE", "")
    if user_profile:
        candidates.append(os.path.join(user_profile, "scoop", "apps", "sdl2", "current"))

    for raw in candidates:
        root = os.path.abspath(raw)
        if os.path.isfile(_sdl2_header_path(root)):
            return root

    print(
        "ERROR: SDL2 tidak ditemukan.\n"
        "  Set variabel lingkungan SDL2_PATH ke folder root SDL2 "
        "(harus ada include/SDL2/SDL.h).\n"
        "  Contoh PowerShell:\n"
        '    $env:SDL2_PATH = "$env:USERPROFILE\\scoop\\apps\\sdl2\\current"',
        file=sys.stderr,
    )
    env.Exit(1)
    return ""


def _resolve_lib_dir(root):
    for rel in ("lib/x64", "lib"):
        lib_dir = os.path.join(root, rel)
        if os.path.isdir(lib_dir):
            return lib_dir
    print(f"ERROR: folder lib SDL2 tidak ada di {root} (coba lib/x64 atau lib).", file=sys.stderr)
    env.Exit(1)
    return ""


def _append_sdl2_libs(link_env, lib_dir):
    """Tambah library SDL2 ke akhir link (LIBS), bukan LINKFLAGS awal."""
    mingw_core = os.path.join(lib_dir, "libSDL2.dll.a")
    mingw_main = os.path.join(lib_dir, "libSDL2main.dll.a")
    msvc_core = os.path.join(lib_dir, "SDL2.lib")
    msvc_main = os.path.join(lib_dir, "SDL2main.lib")

    libs = []
    if os.path.isfile(mingw_core):
        if os.path.isfile(mingw_main):
            libs = [mingw_main, mingw_core]
        else:
            libs = [mingw_core]
    elif os.path.isfile(msvc_core) and os.path.isfile(msvc_main):
        # Scoop SDL2 (MSVC import .lib) — MinGW ld64 menerima path penuh di akhir link
        libs = [msvc_main, msvc_core]
    else:
        print(
            "ERROR: tidak ada lib SDL2 yang dikenali di "
            f"{lib_dir}\n"
            "  MinGW: libSDL2.dll.a (+ libSDL2main.dll.a)\n"
            "  Scoop/VC: SDL2main.lib + SDL2.lib\n"
            "  Alternatif MinGW: MSYS2 pacman -S mingw-w64-x86_64-SDL2, "
            "SDL2_PATH=C:\\msys64\\mingw64",
            file=sys.stderr,
        )
        link_env.Exit(1)
        return

    link_env.Append(LIBPATH=[lib_dir])
    link_env.Append(LIBS=libs)


def _copy_sdl2_dll_for_runtime(link_env, sdl_root):
    """Salin SDL2.dll ke folder build agar `pio run -t exec` jalan tanpa PATH panjang."""
    for rel in ("lib/x64/SDL2.dll", "lib/SDL2.dll"):
        dll_src = os.path.join(sdl_root, rel)
        if os.path.isfile(dll_src):
            build_dir = link_env.subst("$BUILD_DIR")
            dll_dst = os.path.join(build_dir, "SDL2.dll")
            dll_node = link_env.Command(dll_dst, dll_src, Copy("$TARGET", "$SOURCE"))
            program = os.path.join(build_dir, "program.exe")
            link_env.Depends(program, dll_node)
            return


sdl_root = _resolve_sdl2_root()
sdl_include = os.path.join(sdl_root, "include")
sdl_lib = _resolve_lib_dir(sdl_root)

env.Append(CPPPATH=[sdl_include])
_append_sdl2_libs(env, sdl_lib)
_copy_sdl2_dll_for_runtime(env, sdl_root)

# Header publik LVGL: <lvgl/drivers/sdl/*.h> (relatif ke .../lvgl/include)
libdeps_dir = env.subst("$PROJECT_LIBDEPS_DIR")
pioenv = env["PIOENV"]
lvgl_public_include = os.path.join(libdeps_dir, pioenv, "lvgl", "include")
if os.path.isdir(lvgl_public_include):
    env.Append(CPPPATH=[lvgl_public_include])

print(f"SDL2 native: CPPPATH+={sdl_include} LIBPATH+={sdl_lib} LIBS+=SDL2 (akhir link)")
