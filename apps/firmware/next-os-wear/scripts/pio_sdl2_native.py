"""
PlatformIO pre-script: tautkan SDL2 untuk env native/simulator (Windows/Linux).
${sysenv.SDL2_PATH} di platformio.ini sering tidak ter-expand di Windows — path di-set di sini.
"""

import os
import sys

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


sdl_root = _resolve_sdl2_root()
sdl_include = os.path.join(sdl_root, "include")
sdl_lib = _resolve_lib_dir(sdl_root)

env.Append(CPPPATH=[sdl_include])
env.Append(LIBPATH=[sdl_lib])
env.Append(LINKFLAGS=["-lSDL2main", "-lSDL2"])

# Header publik LVGL: <lvgl/drivers/sdl/*.h> (relatif ke .../lvgl/include)
libdeps_dir = env.subst("$PROJECT_LIBDEPS_DIR")
pioenv = env["PIOENV"]
lvgl_public_include = os.path.join(libdeps_dir, pioenv, "lvgl", "include")
if os.path.isdir(lvgl_public_include):
    env.Append(CPPPATH=[lvgl_public_include])

print(f"SDL2 native: CPPPATH+={sdl_include} LIBPATH+={sdl_lib}")
