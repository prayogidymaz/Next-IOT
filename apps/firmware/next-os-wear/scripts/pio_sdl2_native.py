"""
PlatformIO pre-script: tautkan SDL2 untuk env native/simulator (Windows/Linux).
- Linux: pkg-config sdl2 (+ SDL2_mixer), fallback /usr/lib/<triplet>
- Windows: SDL2_PATH / Scoop, MinGW .dll.a atau MSVC .lib di akhir LIBS
"""

import os
import subprocess
import sys

from SCons.Script import Copy

Import("env")


def _sdl2_header_path(root):
    return os.path.join(root, "include", "SDL2", "SDL.h")


def _split_pkg_output(text):
    return [part for part in text.strip().split() if part]


def _linux_lib_dir_from_prefix(root):
    for rel in ("lib/x86_64-linux-gnu", "lib/aarch64-linux-gnu", "lib64", "lib"):
        lib_dir = os.path.join(root, rel)
        if os.path.isdir(lib_dir):
            return lib_dir
    return ""


def _linux_sdl2_lib_candidates():
    return [
        "/usr/lib/x86_64-linux-gnu/libSDL2.so",
        "/usr/lib/x86_64-linux-gnu/libSDL2.a",
        "/usr/lib/aarch64-linux-gnu/libSDL2.so",
        "/usr/lib/libSDL2.so",
    ]


def _linux_find_system_libpath():
    for path in _linux_sdl2_lib_candidates():
        if os.path.isfile(path):
            return os.path.dirname(path)
    return ""


def _linux_header_dirs():
    dirs = []
    for path in ("/usr/include/SDL2/SDL.h", "/usr/local/include/SDL2/SDL.h"):
        if os.path.isfile(path):
            dirs.append(os.path.dirname(os.path.dirname(path)))
    if not dirs:
        dirs.append("/usr/include")
    return dirs


def _linux_split_pkg_libs(libs, main_lib_token):
    """Ambil -L dan flag selain -l<main> (mis. -pthread); -l<main> di-link terakhir."""
    libpaths = []
    extra = []
    for part in libs:
        if part.startswith("-L"):
            libpaths.append(part[2:])
        elif part == main_lib_token:
            continue
        else:
            extra.append(part)
    return libpaths, extra


def _append_linux_shared_lib_end(link_env, lib_name, lib_dirs, extra_linkflags=None):
    """Paksa -l<lib> di akhir rantai link (setelah liblvgl.a) via LINKFLAGS."""
    if lib_dirs:
        link_env.Append(LIBPATH=lib_dirs)
    tail = list(extra_linkflags or [])
    tail.extend(["-Wl,--no-as-needed", f"-l{lib_name}", "-Wl,--as-needed"])
    link_env.Append(LINKFLAGS=tail)
    print(
        f"SDL link (Linux): LIBPATH+={lib_dirs or []} "
        f"LINKFLAGS+=--no-as-needed -l{lib_name} (+ {len(extra_linkflags or [])} extra)"
    )


def _append_pkg_config_sdl2(link_env, module, label):
    cflags = _split_pkg_output(
        subprocess.check_output(["pkg-config", "--cflags", module], text=True)
    )
    libs = _split_pkg_output(
        subprocess.check_output(["pkg-config", "--libs", module], text=True)
    )
    if cflags:
        link_env.Append(CCFLAGS=cflags)
    if module == "sdl2":
        lib_token = "-lSDL2"
        lib_name = "SDL2"
    elif module in ("SDL2_mixer", "sdl2_mixer"):
        lib_token = "-lSDL2_mixer"
        lib_name = "SDL2_mixer"
    else:
        lib_token = f"-l{module}"
        lib_name = module
    libpaths, extra = _linux_split_pkg_libs(libs, lib_token)
    if not libpaths:
        libpaths = [_linux_find_system_libpath() or "/usr/lib/x86_64-linux-gnu"]
    _append_linux_shared_lib_end(link_env, lib_name, libpaths, extra)
    print(f"{label} (Linux pkg-config {module}): pkg-libs={' '.join(libs) or '(none)'}")


def _configure_sdl2_linux(link_env):
    from_env = os.environ.get("SDL2_PATH", "").strip()
    if from_env:
        root = os.path.abspath(from_env)
        if os.path.isfile(_sdl2_header_path(root)):
            include = os.path.join(root, "include")
            lib_dir = _linux_lib_dir_from_prefix(root)
            if lib_dir:
                link_env.Append(CPPPATH=[include])
                _append_linux_shared_lib_end(link_env, "SDL2", [lib_dir])
                print(f"SDL2 native (Linux SDL2_PATH): CPPPATH+={include}")
                return include, lib_dir

    try:
        _append_pkg_config_sdl2(link_env, "sdl2", "SDL2 native")
        return _linux_header_dirs()[0], _linux_find_system_libpath() or "/usr/lib/x86_64-linux-gnu"
    except (FileNotFoundError, subprocess.CalledProcessError) as err:
        print(f"WARN: pkg-config sdl2 gagal ({err}), fallback path sistem")

    lib_dir = _linux_find_system_libpath()
    if not lib_dir:
        print(
            "ERROR: SDL2 tidak ditemukan di Linux.\n"
            "  Pasang: sudo apt install libsdl2-dev\n"
            "  Atau set SDL2_PATH ke prefix dengan include/SDL2/SDL.h\n"
            "  Diharapkan mis.: /usr/lib/x86_64-linux-gnu/libSDL2.so",
            file=sys.stderr,
        )
        link_env.Exit(1)

    include_dirs = _linux_header_dirs()
    link_env.Append(CPPPATH=include_dirs)
    _append_linux_shared_lib_end(link_env, "SDL2", [lib_dir, "/usr/lib"])
    print(f"SDL2 native (Linux fallback): CPPPATH+={include_dirs}")
    return include_dirs[0], lib_dir


def _configure_mixer_linux(link_env):
    from_env = os.environ.get("SDL2_MIXER_PATH", "").strip()
    if from_env:
        root = os.path.abspath(from_env)
        inc = os.path.join(root, "include", "SDL2", "SDL_mixer.h")
        if os.path.isfile(inc):
            lib_dir = _linux_lib_dir_from_prefix(root)
            if lib_dir:
                link_env.Append(CPPDEFINES=[("NEXTOS_HAS_SDL_MIXER", "1")])
                link_env.Append(CPPPATH=[os.path.join(root, "include", "SDL2")])
                _append_linux_shared_lib_end(link_env, "SDL2_mixer", [lib_dir])
                print(f"SDL2_mixer (Linux SDL2_MIXER_PATH): {root}")
                return True

    for module in ("SDL2_mixer", "sdl2_mixer"):
        try:
            link_env.Append(CPPDEFINES=[("NEXTOS_HAS_SDL_MIXER", "1")])
            _append_pkg_config_sdl2(link_env, module, "SDL2_mixer")
            return True
        except (FileNotFoundError, subprocess.CalledProcessError):
            continue

    link_env.Append(CPPDEFINES=[("NEXTOS_HAS_SDL_MIXER", "0")])
    print(
        "WARN: SDL2_mixer tidak ditemukan — audio simulator disabled "
        "(sudo apt install libsdl2-mixer-dev)"
    )
    return False


def _resolve_sdl2_root_windows():
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


def _resolve_lib_dir_windows(root):
    for rel in ("lib/x64", "lib"):
        lib_dir = os.path.join(root, rel)
        if os.path.isdir(lib_dir):
            return lib_dir
    print(f"ERROR: folder lib SDL2 tidak ada di {root} (coba lib/x64 atau lib).", file=sys.stderr)
    env.Exit(1)
    return ""


def _append_sdl2_libs_windows(link_env, lib_dir):
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
    link_env.Append(LIBS=[link_env.File(path) for path in libs])


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


def _configure_sdl2_windows(link_env):
    sdl_root = _resolve_sdl2_root_windows()
    sdl_include = os.path.join(sdl_root, "include")
    sdl_lib = _resolve_lib_dir_windows(sdl_root)
    link_env.Append(CPPPATH=[sdl_include])
    _append_sdl2_libs_windows(link_env, sdl_lib)
    _copy_sdl2_dll_for_runtime(link_env, sdl_root)
    print(f"SDL2 native: CPPPATH+={sdl_include} LIBPATH+={sdl_lib} LIBS+=SDL2 (akhir link)")
    return sdl_include, sdl_lib


def _resolve_mixer_root_windows():
    candidates = []
    from_env = os.environ.get("SDL2_MIXER_PATH", "").strip()
    if from_env:
        candidates.append(from_env)
    user_profile = os.environ.get("USERPROFILE", "")
    if user_profile:
        candidates.append(os.path.join(user_profile, "scoop", "apps", "sdl2-mixer", "current"))
    for raw in candidates:
        root = os.path.abspath(raw)
        inc = os.path.join(root, "include", "SDL2", "SDL_mixer.h")
        if os.path.isfile(inc):
            return root
    return ""


def _append_mixer_libs_windows(link_env, mixer_root):
    lib_dir = os.path.join(mixer_root, "lib")
    if not os.path.isdir(lib_dir):
        lib_dir = os.path.join(mixer_root, "lib", "x64")
    mingw = os.path.join(lib_dir, "libSDL2_mixer.dll.a")
    msvc = os.path.join(lib_dir, "SDL2_mixer.lib")
    if os.path.isfile(mingw):
        link_env.Append(LIBPATH=[lib_dir])
        link_env.Append(LIBS=[link_env.File(mingw)])
    elif os.path.isfile(msvc):
        link_env.Append(LIBPATH=[lib_dir])
        link_env.Append(LIBS=[link_env.File(msvc)])


def _configure_mixer_windows(link_env):
    mixer_root = _resolve_mixer_root_windows()
    if not mixer_root:
        link_env.Append(CPPDEFINES=[("NEXTOS_HAS_SDL_MIXER", "0")])
        print(
            "WARN: SDL2_mixer tidak ditemukan — audio simulator disabled "
            "(scoop install sdl2-mixer)"
        )
        return False

    link_env.Append(CPPDEFINES=[("NEXTOS_HAS_SDL_MIXER", "1")])
    link_env.Append(CPPPATH=[os.path.join(mixer_root, "include", "SDL2")])
    _append_mixer_libs_windows(link_env, mixer_root)
    for rel in ("lib/x64/SDL2_mixer.dll", "lib/SDL2_mixer.dll"):
        dll_src = os.path.join(mixer_root, rel)
        if os.path.isfile(dll_src):
            build_dir = link_env.subst("$BUILD_DIR")
            dll_dst = os.path.join(build_dir, "SDL2_mixer.dll")
            dll_node = link_env.Command(dll_dst, dll_src, Copy("$TARGET", "$SOURCE"))
            program = os.path.join(build_dir, "program.exe")
            link_env.Depends(program, dll_node)
            break
    print(f"SDL2_mixer: linked from {mixer_root}")
    return True


if sys.platform.startswith("linux"):
    _configure_sdl2_linux(env)
    _configure_mixer_linux(env)
else:
    _configure_sdl2_windows(env)
    _configure_mixer_windows(env)

# Header publik LVGL: <lvgl/drivers/sdl/*.h> (relatif ke .../lvgl/include)
libdeps_dir = env.subst("$PROJECT_LIBDEPS_DIR")
pioenv = env["PIOENV"]
lvgl_public_include = os.path.join(libdeps_dir, pioenv, "lvgl", "include")
if os.path.isdir(lvgl_public_include):
    env.Append(CPPPATH=[lvgl_public_include])
